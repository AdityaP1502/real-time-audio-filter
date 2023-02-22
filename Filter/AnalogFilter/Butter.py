import math as mt
import cmath as cmt

class Butterworth():
  @staticmethod
  def __calculate_order(omega_p, omega_s, A_p, A_s):
    # N = log((10^(Ap/10) - 1) / (log(10^(As/10)) - 1)) / 2log(wp/ws)
    numen = mt.log10(( 1 / (10 ** (-A_p/10)) - 1 ) / ( 1/(10 **  (-A_s/10)) - 1 ))
    denom = 2 * mt.log10(omega_p / omega_s)
    return mt.ceil(numen / denom)
  
  @staticmethod
  def __pole_k(i, N):
    return cmt.exp(1j * mt.pi * (((2 * i + 1) / (2 * N)) + 0.5))
  
  @staticmethod
  def __calculate_pole_zero(N):
    zk = [] # only  zero at infinity
    pk = [Butterworth.__pole_k(i, N) for i in range(N)]
    return zk, pk
  
  @staticmethod
  def create_filter(omega_p, omega_s, A_p, A_s):
    """Create a butterworth lowpass filter

    Args:
        omega_p (float): Passband frequency 
        omega_s (float): Stopband frequency
        A_p (float): Passband ripple(dB)
        A_s (float): Stopband attenuation(dB)
    """
    N = Butterworth.__calculate_order(omega_p, omega_s, A_p, A_s)
    zk, pk = Butterworth.__calculate_pole_zero(N)
    return N, [1, zk, pk]
  
    