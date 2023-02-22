from Filter.AnalogFilter.Butter import Butterworth
from cmath import sqrt

class NLPF():
  @staticmethod
  def __find_stopband_lowpass(omega_p, omega_s):
    return omega_s[0] / omega_p[0]
  
  @staticmethod
  def __find_stopband_highpass(omega_p, omega_s):
    return omega_p[0] / omega_s[0]
  
  @staticmethod
  def __find_stopband_bandpass(omega_p, omega_s):
    prod = omega_p[0] * omega_p[1]
    width = omega_p[1] - omega_p[0]
    A = (-(omega_s[0] ** 2) + prod) / (omega_s[0] * width)
    B = ((omega_s[1] ** 2) - prod) / (omega_s[1] * width)
    return min(abs(A), abs(B))
  
  @staticmethod
  def __find_stopband_bandstop(omega_p, omega_s):
    prod = omega_p[0] * omega_p[1]
    width = omega_p[1] - omega_p[0]
    A = (omega_s[0] * width) / (-(omega_s[0] ** 2) + prod) 
    B = (omega_s[1] * width) / ((omega_s[1] ** 2) - prod)
    return min(abs(A), abs(B))
  
  @staticmethod
  def __find_stopband(omega_p, omega_s, filter_type):
    if filter_type == "lowpass":
      omega_s_nlpf = NLPF.__find_stopband_lowpass(omega_p, omega_s)
    
    elif filter_type == "highpass":
      omega_s_nlpf = NLPF.__find_stopband_highpass(omega_p, omega_s)
      
    elif  filter_type == "bandpass":
      omega_s_nlpf = NLPF.__find_stopband_bandpass(omega_p, omega_s)
      
    elif filter_type == "bandstop":
      omega_s_nlpf = NLPF.__find_stopband_bandstop(omega_p, omega_s)
    
    else:
      raise ValueError("filter type \"{}\" is not recognizable".format(filter_type))
    
    return omega_s_nlpf
  
  @staticmethod
  def __design_filter(omega_p, omega_s, A_p, A_s, analog_filter_type):
    if analog_filter_type == "butter":
      return Butterworth.create_filter(omega_p, omega_s, A_p, A_s)
    
    else:
      raise ValueError("analog filter type \"{}\" is not recognizable".format(analog_filter_type))
    
  @staticmethod
  def create_filter(omega_p, omega_s, A_p, A_s, filter_type, analog_filter_type, do_convertion=False):
    omega_p_nlpf = 1
    omega_s_nlpf = NLPF.__find_stopband(omega_p, omega_s, filter_type)
    
    if omega_s_nlpf < 1:
      raise ValueError("Error: Invalid specification. NLPF stopband frequency is less than one. ")
    
    if not do_convertion:
      return NLPF.__design_filter(omega_p_nlpf, omega_s_nlpf, A_p, A_s, analog_filter_type)
    
    else:
      N, [_, zk, pk] = NLPF.__design_filter(omega_p_nlpf, omega_s_nlpf, A_p, A_s, analog_filter_type)
      return NLPF.convert_to(N, zk, pk, omega_p, filter_type)
  
  @staticmethod
  def __pole_zero_conversion_lowpass(zk, pk, omega_p):
    pk = [pole * omega_p[0] for pole in pk]
    return zk, pk
  
  @staticmethod
  def __pole_zero_conversion_highpass(zk, pk, omega_p):
    zk = [0] * len(pk)
    pk = [omega_p[0] / pole  for pole in pk]
    return zk, pk
  
  @staticmethod
  def __quadratic_roots(b, c, a=1):
    determinant = sqrt(b ** 2 - 4*a*c)
    temp1 = -b / 2*a
    temp2 = determinant / 2*a
    
    return (temp1 + temp2, temp1 - temp2)
    
  @staticmethod
  def __pole_zero_conversion_bandpass(zk, pk, omega_p):
    zk = [0] * len(pk) # half of the zero is at z = 0, the other half at z = infinity
    new_pk = [0 for i in range(2 * len(pk))]
    start = 0
    
    width = omega_p[1] - omega_p[0]
    prod = omega_p[1] * omega_p[0]
    
    for i in range(len(pk)):
      pk1, pk2 = NLPF.__quadratic_roots(-1 * (width * pk[i]), prod)
      new_pk[start] = pk1
      new_pk[start + 1] = pk2
      start += 2
    
    return zk, new_pk
      
  @staticmethod
  def __pole_zero_conversion_bandstop(zk, pk, omega_p):
    new_pk = [0 for i in range(2 * len(pk))]
    start = 0
    
    width = omega_p[1] - omega_p[0]
    prod = omega_p[1] * omega_p[0]
    
    temp = sqrt(-prod)
    zk = [temp] * len(pk) + [-temp] * len(pk)
    
    for i in range(len(pk)):
      pk1, pk2 = NLPF.__quadratic_roots(-1 * (width / pk[i]), prod)
      new_pk[start] = pk1
      new_pk[start + 1] = pk2
      start += 2
      
    return zk, new_pk
     
  @staticmethod
  def convert_to(N, zk, pk, omega_p, filter_type):
    if filter_type == "lowpass":
      zk, pk = NLPF.__pole_zero_conversion_lowpass(zk, pk, omega_p=omega_p)
      b0 = 1
      
    elif filter_type == "highpass":
      zk, pk = NLPF.__pole_zero_conversion_highpass(zk, pk, omega_p=omega_p)
      b0 = 1
      
    elif filter_type == "bandpass":
      zk, pk = NLPF.__pole_zero_conversion_bandpass(zk, pk, omega_p=omega_p)
      b0 = 1
      
    elif filter_type == "bandstop":
      zk, pk = NLPF.__pole_zero_conversion_bandstop(zk, pk, omega_p=omega_p)
      b0 = 1
      
    return N, [b0, zk, pk]
  