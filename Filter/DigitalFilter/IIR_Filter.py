from Filter.DigitalFilter.Filter import Filter

class IIR_Filter(Filter):
  def __init__(self, N, b0, zero, pole) -> None:
    super().__init__(N, b0, zero, pole)