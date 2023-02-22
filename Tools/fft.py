from math import pi, log10, atan
from cmath import exp

PRECISION = 5

def to_power_of_two(length):
  # find the closest power of two
  k = 1
  while k < length:
    k <<= 1
  
  return k

def do_fft(coeff : list[complex], isForward : bool):
  if len(coeff) == 1:
    return [coeff[0]]
  
  half_length = len(coeff) >> 1
  angle = complex(0)
  dt = (-2j * pi) / len(coeff) if isForward else (2j * pi) / len(coeff)
  
  # even - odd decomposition
  even_coeff = [coeff[i] for i in range(len(coeff)) if i % 2 == 0]
  odd_coef = [coeff[i] for i in range(len(coeff)) if i % 2 == 1]
  
  # solve decomposition
  ye = do_fft(even_coeff, isForward)
  yo = do_fft(odd_coef, isForward)
  
  res = [0] * len(coeff)
  
  # combine result
  for i in range(half_length):
    temp = exp(angle) * yo[i]
    res[i] = ye[i]  + temp
    res[i + half_length] = ye[i] - temp 
    angle += dt
  
  return res

def fft(coeff : list[complex]):
  # zero padding to the closest power of two
  new_length = to_power_of_two(len(coeff))
  pad_length = new_length - len(coeff)
  coeff = coeff + [0] * pad_length
  
  res = do_fft(coeff, isForward=True)
  res = map(lambda x: complex(round(x.real, PRECISION), round(x.imag, PRECISION)), res)
  return list(res)

  
def ifft(coeff : list[complex], force_symmetric = False):
  # zero padding to the closest power of two
  new_length = to_power_of_two(len(coeff))
  pad_length = new_length - len(coeff)
  coeff = coeff + [0] * pad_length
  
  res = do_fft(coeff, isForward=False)
  for i in range(len(res)):
    res[i] /= len(res)
    
  res = map(lambda x: complex(round(x.real, PRECISION), round(x.imag, PRECISION)), res) 
  res = list(res)
  
  if force_symmetric:
    # discard complex value
    for i in range(len(res)):
      res[i] = res[i].real

  return res

def convFFT(c1, c2, force_symmetric=False):
  # basically multiplication of 
  # two polynomial
  # with coeff c1 and c2
  
  length = len(c1) + len(c2) - 1
  
  pad_length_1 = length - len(c1)
  pad_length_2 = length - len(c2)
  
  c1 = c1 + [0] * (pad_length_1)
  c2 = c2 + [0] * (pad_length_2)
  
  Ck1 = fft(c1)
  Ck2 = fft(c2) 
 
  # convolution is just multiplication in freq domain
  Ck_result = [ck1 * ck2 for (ck1, ck2) in zip(Ck1, Ck2)]
  
  ck_result = ifft(Ck_result, force_symmetric)
  return ck_result[:length]

def mag2db(mag):
  max_val = max(mag)
  mag_db = []
  for magnitude in mag:
    if magnitude == 0:
      mag_db.append(float("-infinity"))
    else:
      mag_db.append(10 * log10(magnitude/max_val))
      
  return mag_db

def magnitude(freq_response):
  return (freq_response.real ** 2 + freq_response.imag ** 2) ** (0.5)

def angle(freq_response):
  return atan(freq_response.imag / freq_response.real)
  
if __name__ == "__main__":
  coef1 = [1, 1, 1, 2, 2, 0, 0, 0, 1, 0, 0, 0, 1, 1, 2, 0]
  coef2 = [1, 1, 1, 1, 2]
  coef3 = convFFT(coef1, coef2, True)
  print(coef3)
  
  
