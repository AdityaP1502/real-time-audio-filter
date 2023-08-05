from Config.conf import FFT_ENGINE
from Tools.fft.fft import *
from Tools.Filter.DigitalFilter.Filter import Filter


class FIR_Filter(Filter):
    def __init__(self, N, b0=None, zero=..., pole=..., hn=...) -> None:
        super().__init__(N, b0, zero, pole, hn)
        self.buffer = [0] * (N)
        self.output_buffer = []
        self.__do_filter = None
        self.sample_length = None

    def init_filter(self, sample_length: int, is_real_time=True):
        assert sample_length > len(
            self.hn), "Sample length must be bigger or equal to filter length"
        self.hn = self.hn + [0] * (sample_length - (self.N + 1))
        self.__do_filter = self.__filter_overlap_save if is_real_time else self.__filter_normal
        self.sample_length = sample_length

        if FFT_ENGINE == "RADIX4":
            self.fft = StaticRadix4FFT(sample_length)

        elif FFT_ENGINE == "RADIX2":
            self.fft = Radix2FFT()

        elif FFT_ENGINE == "SPLITRADIX":
            NotImplemented

    def __filter_overlap_save(self, xn_0, xn_1):
        """ Filter using overlap save. Can create output up to 2 chunk of data. Need two input chunks 
            to form the output chunks. 
        Args:
            xn_0 (list[float]): First chunk
            xn_1 (list[float]): Second chunk

        Returns:
            res : list[list[float]] : The output chunks
        """

        assert type(xn_0).__name__ == "list", "input must have type list. Not {}".format(
            type(xn_0).__name__)
        assert type(xn_1).__name__ == "list", "input must have type list. Not {}".format(
            type(xn_1).__name__)

        xm_0 = self.buffer + xn_0[0:self.sample_length - (self.N)]
        xm_1 = xm_0[-(self.N):] + xn_1[0:self.sample_length - (self.N)]

        res = []

        assert len(xm_0) == self.sample_length, "the length of the block must eqaul to sample length {}. Received {}".format(
            self.sample_length, len(xm_0))
        assert len(xm_1) == self.sample_length, "the length of the block must eqaul to sample length {}. Received {}".format(
            self.sample_length, len(xm_1))

        y0 = self.fft.convfft_overlap_save(
            xm_0, self.hn)[self.N:]  # discard M - 1 element
        y1 = self.fft.convfft_overlap_save(
            xm_1, self.hn)[self.N:]  # discard M - 1 element

        # append data from the output buffer to y0
        y = self.output_buffer + \
            y0[0: self.sample_length - (len(self.output_buffer))]

        # add data from the next output chunk
        if len(y) < self.sample_length:
            y = y + y1[0:self.sample_length - (len(y))]

        assert len(y) == self.sample_length, "Each output chunk must have {} length. Received {}".format(
            self.sample_length, len(y))
        res.append(y)
        buffer_length = len(self.output_buffer) + len(y0) + \
            len(y1) - self.sample_length

        # add lefover from the last and part of the next output to form another chunk
        if buffer_length > self.sample_length:
            y = y0[self.sample_length - (len(y)):]
            y += y1[:self.sample_length - (len(y))]
            buffer_length -= self.sample_length
            assert len(y) == self.sample_length, "Each output chunk must have {} length. Received {}".format(
                self.sample_length, len(y))
            res.append(y)

        # update buffer
        self.output_buffer = y1[len(y1) - buffer_length: len(y1)]
        self.buffer = xm_1[-(self.N):]

        return res

    def __filter_normal(self, xn):
        y = self.fft.convfft(xn, self.hn)
        return y

    def filter(self, xn, xn_=None):
        if type(xn_).__name__ == "list":
            return self.__do_filter(xn, xn_)

        return self.__do_filter(xn)
