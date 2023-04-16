import copy
class SoftClipper():  
  @staticmethod
  def apply_effects(x : float, thresh=10) -> float:
    n = x/thresh
    if n >= 1:
      return 2/3 * thresh
    
    if n <= -1:
      return -2/3 * thresh

    else:
      return (n - n**3 / 3) * thresh
    
  
class HardClipper(): 
  @staticmethod 
  def apply_effects(x : float, thresh=10) -> float:
    n = x/thresh
    if n >= 0.75:
      return 0.75 * thresh
    
    if n <= -0.75:
      return -0.75 * thresh
    
    return n * thresh

class Delay():
  def __init__(self, delay_strength, delay, Fs=44100, chunk=1024) -> None:
    self.delay = delay
    self.delay_strength = delay_strength
    self.Fs = Fs
    self.chunk = chunk
    self.buffer = []
    self.offset = int(Fs * delay)
    self.start = self.offset % self.chunk
    self.counter = 0

  def apply_effects(self, data):
    # add current audio to delay buffer
    self.buffer.append(copy.copy(data))
    
    # add delay from buffer delay amount has been reached
    if len(self.buffer) * self.chunk > self.offset:
      for i in range(self.start, self.chunk):
        if self.counter >= self.chunk:
          # use the next data from the buffer
          # self.test.append(self.buffer[0])
          self.counter = 0
          del self.buffer[0]
        
        
        data[i] += self.delay_strength * self.buffer[0][self.counter]
        self.counter += 1

    # else:
    #   self.test.append(([0] * self.chunk))
      
    self.start = 0