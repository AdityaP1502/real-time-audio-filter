import math as mt

from Tools.Filter.AnalogFilter.NLPF import NLPF
from Tools.Filter.DigitalFilter.IIR_Filter import IIR_Filter
from Tools.Filter.DigitalFilter.FIR_Filter import FIR_Filter
from Tools.Filter.DigitalFilter.WIndow import Window


class IIR_FilterDesigner():
    def __init__(self, f_p, f_s, A_p, A_s, Fs, filter_type, analog_filter_type="butter") -> None:
        if (len(f_p) != 1 or len(f_s) != 1) and (filter_type == "lowpass" or filter_type == "highpass"):
            raise ValueError("Expecting one passband / stopband frequency for filter type {}, get {}".format(filter_type, max(len(f_p), len(f_s))))
        
        if (len(f_p) != 2 or len(f_s) != 2) and (filter_type == "lowpass" or filter_type == "highpass"):
            raise ValueError("Expecting two passband / stopband frequency for filter type {}, get {}".format(filter_type, max(len(f_p), len(f_s))))
        
        if A_p >= A_s:
            raise ValueError("Passband ripple must be smaller than Stopband ripple")
        
        self.omega_p = [2 * mt.pi * fp / Fs for fp in f_p]
        self.omega_s = [2 * mt.pi * fs / Fs for fs in f_s]
        self.A_p = A_p
        self.A_s = A_s
        self.Fs = Fs
        self.filter_type = filter_type
        self.analog_filter_type = analog_filter_type

    def __repr__(self) -> str:
        omega_p = [omega * mt.pi for omega in self.omega_p]
        omega_s = [omega * mt.pi for omega in self.omega_s]
        
        prompt = """Filter Specification
    omega_p             : Passband frequency(xpi)  = {} 
    omega_s             : Stopband frequency(xpi)  = {}
    A_p                 : Passband ripple          = {} dB
    A_s                 : Stopband ripple          = {} dB
    Fs                  : Sampling Frequency       = {} Hz
    filter_type         : Filter type              = {}
    analog_filter_type  : Analog Filter Type       = {}
    """.format(omega_p, omega_s, self.A_p, self.A_s,
               self.Fs, self.filter_type, self.analog_filter_type)

        return prompt

    def __transform_frequency(self, transformation):
        if transformation == "bilinear":
            Omega_p = list(map(lambda x: 2 * self.Fs *
                           mt.tan(x / 2), self.omega_p))
            Omega_s = list(map(lambda x: 2 * self.Fs *
                           mt.tan(x / 2), self.omega_s))

        if transformation == "impulse invariance":
            NotImplemented

        return Omega_p, Omega_s

    def __pole_conversion(self, pk):
        for (i, pole) in enumerate(pk):
            numen = 2 * self.Fs + pole
            denom = 2 * self.Fs - pole
            pk[i] = numen / denom

        return pk

    def __pole_zero_conversion_lowpass(self, zk, pk):
        zk = [-1] * len(pk)
        pk = self.__pole_conversion(pk)
        return zk, pk

    def __pole_zero_conversion_highpass(self, zk, pk):
        zk = [1] * len(pk)
        pk = self.__pole_conversion(pk)
        return zk, pk

    def __pole_zero_conversion_bandpass(self, zk, pk):
        zk = [-1] * (len(pk) // 2) + [1] * (len(pk) // 2)
        pk = self.__pole_conversion(pk)
        return zk, pk

    def __pole_zero_conversion_bandstop(self, zk, pk):
        zk = self.__pole_conversion(zk)
        pk = self.__pole_conversion(pk)
        return zk, pk

    def __calculate_multiplier(self, pk):
        multi = 1
        for pole in pk:
            multi *= 2 * self.Fs - pole

        return multi

    def __multi_all_pole(self, pk):
        prod = 1
        for pole in pk:
            prod *= pole

        return prod

    def create_filter(self, transformation="bilinear"):
        if transformation != "bilinear" and transformation != "impulse invariance":
            raise ValueError(
                "transformation {} is not recognizable".format(transformation))

        # convert frequency
        Omega_p, Omega_s = self.__transform_frequency(transformation)

        # create a filter from NLPF
        N, [_, za, pa] = NLPF.create_filter(
            Omega_p, Omega_s,
            self.A_p, self.A_s,
            self.filter_type, self.analog_filter_type,
            do_convertion=True
        )

        multiplier = self.__calculate_multiplier(pa)

        # transform transfer function
        if self.filter_type == "lowpass":
            za, pa = self.__pole_zero_conversion_lowpass(za, pa)
            b0 = Omega_p[0] ** (N) / multiplier

        elif self.filter_type == "highpass":
            za, pa = self.__pole_zero_conversion_highpass(za, pa)
            pole_multi = self.__multi_all_pole(pa)
            b0 = (2 * self.Fs) ** (N) / (multiplier * pole_multi)

        elif self.filter_type == "bandpass":
            za, pa = self.__pole_zero_conversion_bandpass(za, pa)
            b0 = ((2 * (Omega_p[1] - Omega_p[0]) * self.Fs) ** N) / multiplier

        elif self.filter_type == "bandstop":
            za, pa = self.__pole_zero_conversion_bandstop(za, pa)
            multiplier_zero = self.__calculate_multiplier(za)
            pole_multi = self.__multi_all_pole(pa)
            b0 = multiplier_zero / (pole_multi * multiplier)

        return IIR_Filter(N, b0, za, pa)

class FIR_FilterDesigner():
    def __init__(self, f_p, f_s, A_p, A_s, Fs, filter_type, linear_type = 1, window_filter_type="rectangular") -> None:
        if (len(f_p) != 1 or len(f_s) != 1) and (filter_type == "lowpass" or filter_type == "highpass"):
            raise ValueError("Expecting one passband / stopband frequency for filter type {}, get {}".format(filter_type, max(len(f_p), len(f_s))))
        
        if (len(f_p) != 2 or len(f_s) != 2) and (filter_type == "bandpass" or filter_type == "bandstop"):
            raise ValueError("Expecting two passband / stopband frequency for filter type {}, get {}".format(filter_type, max(len(f_p), len(f_s))))
        
        if A_p >= A_s:
            raise ValueError("Passband ripple must be smaller than Stopband ripple")
        
        if linear_type > 4 or linear_type < 1 or type(linear_type).__name__ != "int":
            raise ValueError("linear type must be an integer from 1 to 4")
        
        self.omega_p = [2 * mt.pi * fp / Fs for fp in f_p]
        self.omega_s = [2 * mt.pi * fs / Fs for fs in f_s]
        self.A_p = A_p
        self.A_s = A_s
        self.Fs = Fs
        self.filter_type = filter_type
        self.linear_type = linear_type
        self.window_filter_type = window_filter_type

    def __repr__(self) -> str:
        omega_p = [omega * mt.pi for omega in self.omega_p]
        omega_s = [omega * mt.pi for omega in self.omega_s]
        
        prompt = """Filter Specification
    omega_p             : Passband frequency(xpi)  = {} 
    omega_s             : Stopband frequency(xpi)  = {}
    A_p                 : Passband ripple          = {} dB
    A_s                 : Stopband ripple          = {} dB
    Fs                  : Sampling Frequency       = {} Hz
    filter_type         : Filter type              = {}
    linear_type         : linear  type             = {}
    window_filter_type  : window function          = {}
    """.format(omega_p, omega_s, self.A_p, self.A_s,
               self.Fs, self.filter_type, self.linear_type, self.window_filter_type)

        return prompt
    
    def __sinc(self, alpha, omega_c):
        return lambda x: mt.sin(omega_c * (x - alpha)) / (mt.pi * (x - alpha))
  
    def __ideal_lowpass(self, alpha, omega_c):
      sinc = self.__sinc(alpha, omega_c)
      return lambda x: sinc(x) if x != alpha else omega_c / mt.pi
    
    def __ideal_highpass(self, alpha, omega_c):
      sinc = self.__sinc(alpha, omega_c)
      return lambda x: -1 * sinc(x) if x != alpha else 1 - omega_c / mt.pi
    
    def __ideal_bandpass(self, alpha, omega_c):
      sinc_lower = self.__sinc(alpha, omega_c[0])
      sinc_upper = self.__sinc(alpha, omega_c[1])
      return lambda x:  sinc_upper(x) - sinc_lower(x)  if x != alpha else (omega_c[1] - omega_c[0]) / mt.pi
    
    def __ideal_bandstop(self, alpha, omega_c):
      sinc_lower = self.__sinc(alpha, omega_c[0])
      sinc_upper = self.__sinc(alpha, omega_c[1])
      return lambda x: -sinc_upper(x) + sinc_lower(x) if x != alpha else -(omega_c[1] - omega_c[0]) / mt.pi
    
    def __ideal_filter_impulse_response(self, N, omega_c):
      # create an impulse response of an ideal filter
      # which start at 0
      # and center at (N - 1) / 2
      # N is odd

      if N % 2 != 1:
        raise ValueError("Length must be odd")

      shift_val = N >> 1
      points = (i for i in range(N))

      if self.filter_type == "lowpass":
        return list(map(self.__ideal_lowpass(shift_val, omega_c[0]), points))

      elif self.filter_type == "highpass":
        return list(map(self.__ideal_highpass(shift_val, omega_c[0]), points))

      elif self.filter_type == "bandpass":
        return list(map(self.__ideal_bandpass(shift_val, omega_c), points))    

      elif self.filter_type == "bandstop":
        return list(map(self.__ideal_bandstop(shift_val, omega_c), points))

      else:
        raise ValueError("Filter type \"{}\" is not recognizable".format(self.filter_type))


    def create_filter(self):
        if len(self.omega_p) > 1:
            dw = min(abs(self.omega_p[1] - self.omega_s[1]), abs(self.omega_p[0] - self.omega_s[0]))
        
        else:
            dw = abs(self.omega_p[0] - self.omega_s[0])

        # filter window and filter length
        window = Window(self.window_filter_type, dw)
        N = len(window.wn)
        
        omega_c = [(self.omega_p[i] + self.omega_s[i]) / 2 for i in range(len(self.omega_p))]
        hd = self.__ideal_filter_impulse_response(N, omega_c)
        h = window.window(hd, precision=5)
        
        assert len(h) % 2 == 1, "Something is wrong, getting an even length in ideal impulse response"
        
        if self.linear_type == 2:
            # symmetric even length
            # remove the middle element
            del h[N // 2]
        
        elif self.linear_type == 3:
            # antisymmetric odd length
            antisymm = [(-1) ** (i >= N // 2) for i in range(N)]
            antisymm[N // 2] = 0
            h = Window.window(antisymm, hd)
        
        elif self.linear_type == 4:
            # antisymmetric even length
            antisymm = [(-1) ** (i >= N // 2) for i in range(N)]
            antisymm[N // 2] = 0
            h = Window.window(antisymm, hd)
            del h[N // 2]
        
    
        return FIR_Filter(N - 1, hn=h)