from Tools.fft.fft import *
from Tools.Filter.DigitalFilter.Filter import Filter

class FIR_Filter(Filter):
  def __init__(self, N, b0=None, zero=..., pole=..., hn=...) -> None:
    super().__init__(N, b0, zero, pole, hn)
    self.buffer = [0] * (N)
    self.__do_filter = None
    self.sample_length = None

  def init_filter(self, sample_length : int, is_real_time=True):
    assert sample_length > len(self.hn), "Sample length must be bigger or equal to filter length"
    self.hn = self.hn + [0] * (sample_length - (self.N + 1))
    self.__do_filter = self.__filter_overlap_save if is_real_time else self.__filter_normal
    self.sample_length = sample_length

  def __filter_overlap_save(self, xn):
    xm = self.buffer + xn[0:self.sample_length - (self.N)]
    assert len(xm) == self.sample_length, "the length of the block must eqaul to sample length {}. Received {}".format(self.sample_length, len(xm))

    y = convfft_overlap_save(xm, self.hn)
    self.buffer = xm[-(self.N):]
    return y
  
  def __filter_normal(self, xn):
    y = convfft(xn, self.hn)
    return y

  def filter(self, xn):
    return self.__do_filter(xn)

    
    
  

