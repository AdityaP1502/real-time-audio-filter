from Tools.pole_zero import fromZeroToPolynomial, calculate_freq_response
from Tools.fft import mag2db, magnitude, angle
from multiprocessing import Pool, cpu_count
import matplotlib.pyplot as plt

class Filter():
  def __init__(self, N, b0 = None, zero = [], pole = [], hn = []) -> None:
    self.N = N
    self.b0 = None
    self.zero = []
    self.pole = []
    self.hn = []
    
    if (b0 != None and len(zero) > 0 and len(pole) > 0):
      # IIR Filter Init
      self.b0 = b0
      self.zero = zero
      self.pole = pole
      
    elif (len(hn) > 0):
      # FIR Filter Init
      self.hn = hn
      
    else:
      raise ValueError("Bad initialization. Filter can only be created with either pole-zero form or impulse response form")

  def __repr__(self) -> str:
    prompt = """Designed Filter
    N     : order of Filter             = {}
    b0    : transfer function constant  = {}
    zero  : filter zero location        = {}
    pole  : filter pole location        = {} 
    """.format(self.N, self.b0, self.zero, self.pole)
    
    return prompt

  def findPolynomial(self):
    Bn = fromZeroToPolynomial(self.zero)
    An = fromZeroToPolynomial(self.pole)
    return Bn, An
  
  def __format_transfer_function(self, b):
    transfer_function_str = ""
    degree = len(b) - 1
    
    for coef  in b:
      x = round(coef.real, 5)
      y = round(coef.imag, 5)
      if x == 0 and y == 0:
        continue
      
      if x == 0:
        
        if degree == 0:
          transfer_function_str += "+{}".format(y, degree)
          
        else:
          transfer_function_str += "+j{}z^{}".format(y, degree)
          
      elif y == 0:
        
        if degree == 0:
          transfer_function_str += "+{}".format(x, degree)
          
        else:
          transfer_function_str += "+{}z^{}".format(x, degree)
          
      else:
        if degree == 0:
          transfer_function_str += "+{}".format(coef, degree)
          
        else:
          transfer_function_str += "+({})z^{}".format(coef, degree)
          
      degree -= 1
      
    return transfer_function_str
  
  def transferFunction(self):
    b, a = self.findPolynomial()
    numen_str = self.__format_transfer_function(b)
    denom_str = self.__format_transfer_function(a)
    return "{}/{}".format(numen_str, denom_str)
  
  def __freq_response_data_points(self, N : int):
    # normalized frequency (xpi)
    # from [0...1] 
    
    w = [i/N for i in range(N)]
    
    data_pole = [[self.pole, omega] for omega in w]
    data_zero = [[self.zero, omega] for omega in w]
        
    with Pool(cpu_count()) as pool:
      pole_response = pool.map(calculate_freq_response, data_pole)
      zero_response = pool.map(calculate_freq_response, data_zero)
    
    b0_mag = magnitude(self.b0)
    b0_angle = angle(self.b0)
    
    find_total_response = lambda x, y: (b0_mag * x[0]/y[0], b0_angle + x[1] - y[1])
    return w, list(map(find_total_response, zero_response, pole_response))

  def showFreqResponse(self, N = 500, log_scale=False):
    w, data_points = self.__freq_response_data_points(N)
    mag_response, phase_response = zip(*data_points)

    if log_scale:
      mag_response = mag2db(mag_response)
      
    plt.plot(w, mag_response)
    plt.show()
    
    plt.plot(w, phase_response)
    plt.plot()
    
  def filter(self, xn):
    NotImplemented
