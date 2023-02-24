from math import cos, pi, ceil
import matplotlib.pyplot as plt

class Window():
  def __init__(self, window_type, dw) -> None:    
    if window_type == "rectangular":
      self.wn = self.__rectangular(dw)
    
    elif window_type == "barlett":
      self.wn = self.__barlett(dw)
      
    elif window_type == "hanning":
      self.wn = self.__hanning(dw)
      
    elif window_type == "hamming":
      self.wn = self.__hamming(dw)
      
    elif window_type == "blackman":
      self.wn = self.__blackman(dw)

    elif window_type == "kaiser":
      self.wn = self.__kaiser(dw)
      
    else:
      raise ValueError("Unrecognizable \"{}\" window type".format(window_type))
    
    self.window_type = window_type
  
  def __repr__(self) -> str:
    prompt = "Window = {}\nValue: ".format(self.window_type)
    
    for val in self.wn:
      prompt += "{},".format(val)
      
    return prompt[:-2]
  
  def window(self, hn, precision=-1):
    if len(hn) != len(self.wn):
      raise ValueError("Invalid input size. Expected array of length {}".format(len(self.wn)))

    if precision < -1 or type(precision).__name__ != "int":
      raise ValueError ("Invalid precision value. Precision must be an integer greater or equal to zero.")
    
    if precision > -1:
      prod = lambda x, y: round(x * y, precision)
    
    else:
      prod = lambda x, y: x * y
      
    return list(map(prod, self.wn, hn))
      
  @staticmethod
  def __rectangular(dw):
    N = ceil(4 * pi / dw)
    N += 1 - N % 2
    return [1 for i in range(N)]
  
  @staticmethod
  def __barlett(dw):
    N = ceil(6.1 * pi / dw)
    N += 1 - N % 2
    
    half_length = N // 2
    
    first_iter = lambda x: 2 * x / (N - 1)
    second_iter = lambda x: 2 - first_iter(x)
    barlett_fnc = lambda x: first_iter(x) if x <= half_length else second_iter(x)
    
    return [barlett_fnc(i) for i in range(N)]
  
  @staticmethod
  def __hanning(dw):
    N = ceil(6.2 * pi / dw)
    N += 1 - N % 2
    
    hanning_fnc = lambda x: 0.5 * (1 - cos( 2 * pi * x / (N - 1) ) )
    return [hanning_fnc(i) for i in range(N)]
    
  @staticmethod
  def __hamming(dw):
    N = ceil(6.6 * pi / dw)
    N += 1 - N % 2
    
    hamming_fnc = lambda x: 0.54 - 0.46 * cos( 2 * pi * x / (N - 1) )
    return [hamming_fnc(i) for i in range(N)]
  
  @staticmethod
  def __blackman(dw):
    N = ceil(11 * pi / dw)
    N += 1 - N % 2
    
    blackman_fnc = lambda x: 0.42 - 0.5 * cos( 2 * pi * x / (N - 1) ) + 0.08 * cos( 4 * pi * x / (N - 1) )
    return [blackman_fnc(i) for i in range(N)]
  
  @staticmethod
  def __kaiser(dw):
    pass
  
  def show(self):
    plt.stem(self.wn)
    plt.show()
  
if __name__ == "__main__":
  window = Window(5, "barlett")
  hn = [1, 1, 1, 1, 1]
  print(window)
  window_hn = window.window(hn, precision=5)
  print(window_hn)
  window.show()
  