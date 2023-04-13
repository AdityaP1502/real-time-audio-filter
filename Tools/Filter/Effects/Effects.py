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
