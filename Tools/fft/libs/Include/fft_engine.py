# Function Wrapper for FFT
# with static length
# therefore we can cache the twiddle factors

from Tools.fft.libs.Include.fft_iterative import *
import sys


class Radix2FFT():
    def __init__(self, order="NR"):
        if len(order) != 2:
            raise ValueError("Invalid order")

        self.order = order

    def fft(self, xn):
        global iterative_fft

        order = self.order + '\0'
        length = len(xn)

        xn_ptr = cast((c_double * length)(*xn), POINTER(c_double))
        order_ptr = c_char_p(bytes(order, 'UTF-8'))
        try:
            Xk_pointer = iterative_fft.fft_iterative(
                (xn_ptr), length, order_ptr)
            Xk = Xk_pointer.contents
            result = []

            for i in range(Xk.length):
                complex_number_ptr = Xk.bin[i]
                complex_number = complex_number_ptr.contents
                result.append(
                    complex(complex_number.real, complex_number.imag))

            return result

        except Exception as e:
            print(e)
            sys.exit(-1)

    def ifft(self, Xk: list[complex]):
        global iterative_fft, COMPLEX_NUMBER, FFT_BINS

        order = self.order + '\0'
        length = len(Xk)

        # create an complex number structure
        bins = (POINTER(COMPLEX_NUMBER) * length)()
        order_ptr = c_char_p(bytes(order, 'UTF-8'))

        for i in range(length):
            number = COMPLEX_NUMBER(real=Xk[i].real, imag=Xk[i].imag)
            bins[i] = pointer(number)

        try:
            Xk_pointer = iterative_fft.ifft_iterative(
                cast(bins, POINTER(POINTER(COMPLEX_NUMBER))), length, order_ptr)
            Xk = Xk_pointer.contents
            result = []

            for i in range(Xk.length):
                complex_number_ptr = Xk.bin[i]
                complex_number = complex_number_ptr.contents
                result.append(
                    complex(complex_number.real, complex_number.imag))

            return result

        except Exception as e:
            print(e)
            sys.exit(-1)

    def ifft_symmetric(self, Xk: list[complex]):
        global iterative_fft, COMPLEX_NUMBER, FFT_BINS

        order = self.order + '\0'
        length = len(Xk)

        # create an complex number structure
        bins = (POINTER(COMPLEX_NUMBER) * length)()
        order_ptr = c_char_p(bytes(order, 'UTF-8'))

        for i in range(length):
            number = COMPLEX_NUMBER(real=Xk[i].real, imag=Xk[i].imag)
            bins[i] = pointer(number)

        try:
            xn_pointer = iterative_fft.ifft_iterative_symmetric(
                cast(bins, POINTER(POINTER(COMPLEX_NUMBER))), length, order_ptr)
            xn = xn_pointer.contents
            result = []

            for i in range(xn.length):
                result.append(xn.bin[i])

            return result

        except Exception as e:
            print(e)
            sys.exit(-1)

    def convfft(self, xa: list[float], xb: list[float]):
        length_a = len(xa)
        xn_ptr_a = cast((c_double * length_a)(*xa), POINTER(c_double))
        length_b = len(xb)
        xn_ptr_b = cast((c_double * length_b)(*xb), POINTER(c_double))

        try:
            xn_ptr = conv_fft.convfft(xn_ptr_a, xn_ptr_b, length_a, length_b)
            xn = xn_ptr.contents
            result = []

            for i in range(xn.length):
                result.append(xn.bin[i])

            return result[:length_a + length_b]

        except Exception as e:
            print(e)
            sys.exit(-1)

    def convfft_overlap_save(self, xa: list[float], xb: list[float]):
        length_a = len(xa)
        xn_ptr_a = cast((c_double * length_a)(*xa), POINTER(c_double))
        length_b = len(xb)
        xn_ptr_b = cast((c_double * length_b)(*xb), POINTER(c_double))

        assert length_a == length_b, "each block must have the same length that is the sample length/chunksize. {} != {}".format(
            length_a, length_b)

        try:
            xn_ptr = conv_fft.convfft_overlap_save(
                xn_ptr_a, xn_ptr_b, length_a)
            xn = xn_ptr.contents
            result = []

            for i in range(xn.length):
                result.append(xn.bin[i])

            return result[:length_a + length_b]

        except Exception as e:
            print(e)
            sys.exit(-1)


class StaticRadix2FFT():
    def __init__(self, N, order="NR") -> None:
        self.fft_size = N
        self.order = order

        self.__forward_twid_factor = util_fft.precompute_twiddle_factor(
            self.fft_size, 0)
        self.__backward_twid_factor = util_fft.precompute_twiddle_factor(
            self.fft_size, 1)

        self.__is_destroyed = False

    def fft(self, xn):
        assert not self.__is_destroyed, "This object has already been destroyed"
        global iterative_fft

        order = self.order + '\0'
        length = len(xn)

        xn_ptr = cast((c_double * length)(*xn), POINTER(c_double))
        order_ptr = c_char_p(bytes(order, 'UTF-8'))

        try:
            Xk_pointer = iterative_fft.fft_iterative_static_n(
                self.__forward_twid_factor, self.fft_size, xn_ptr, length, order_ptr)
            Xk = Xk_pointer.contents
            result = []

            for i in range(Xk.length):
                complex_number_ptr = Xk.bin[i]
                complex_number = complex_number_ptr.contents
                result.append(
                    complex(complex_number.real, complex_number.imag))

            return result

        except Exception as e:
            print(e)
            sys.exit(-1)

    def ifft(self, Xk: list[complex]):
        assert not self.__is_destroyed, "This object has already been destroyed"
        global iterative_fft, COMPLEX_NUMBER, FFT_BINS

        order = self.order + '\0'
        length = len(Xk)

        # create an complex number structure
        bins = (POINTER(COMPLEX_NUMBER) * length)()
        order_ptr = c_char_p(bytes(order, 'UTF-8'))

        for i in range(length):
            number = COMPLEX_NUMBER(real=Xk[i].real, imag=Xk[i].imag)
            bins[i] = pointer(number)

        try:
            Xk_pointer = iterative_fft.ifft_iterative_static_n(cast(bins, POINTER(POINTER(
                COMPLEX_NUMBER))), self.__backward_twid_factor, self.fft_size, length, order_ptr)
            Xk = Xk_pointer.contents
            result = []

            for i in range(Xk.length):
                complex_number_ptr = Xk.bin[i]
                complex_number = complex_number_ptr.contents
                result.append(
                    complex(complex_number.real, complex_number.imag))

            return result

        except Exception as e:
            print(e)
            sys.exit(-1)

    def ifft_symmetric(Xk: list[complex]):
        NotImplemented

    def convfft(xa: list[float], xb: list[float]):
        NotImplemented

    def convfft_overlap_save(xa: list[float], xb: list[float]):
        NotImplemented

    def destroy(self):
        global util_fft
        util_fft.destroy_bin(self.__backward_twid_factor, self.fft_size // 2)
        util_fft.destroy_bin(self.__forward_twid_factor, self.fft_size // 2)
        self.__is_destroyed = True


class StaticRadix4FFT():
    def __init__(self, N) -> None:
        self.fft_size = N

        self.__forward_twid_factor = util_fft.precompute_twiddle_factor_radix_4(
            self.fft_size, 0)
        self.__backward_twid_factor = util_fft.precompute_twiddle_factor_radix_4(
            self.fft_size, 1)

        self.__is_destroyed = False

    def fft(self, xn):
        assert not self.__is_destroyed, "This object has already been destroyed"
        global iterative_fft_4

        length = len(xn)

        xn_ptr = cast((c_double * length)(*xn), POINTER(c_double))

        try:
            Xk_pointer = iterative_fft_4.fft_radix_4_iterative_static_n(
                self.__forward_twid_factor, self.fft_size, xn_ptr, length)
            Xk = Xk_pointer.contents
            result = []

            for i in range(Xk.length):
                complex_number_ptr = Xk.bin[i]
                complex_number = complex_number_ptr.contents
                result.append(
                    complex(complex_number.real, complex_number.imag))

            return result

        except Exception as e:
            print(e)
            sys.exit(-1)

    def ifft(self, Xk: list[complex]):
        assert not self.__is_destroyed, "This object has already been destroyed"
        global iterative_fft_4, COMPLEX_NUMBER, FFT_BINS

        length = len(Xk)

        # create an complex number structure
        bins = (POINTER(COMPLEX_NUMBER) * length)()

        for i in range(length):
            number = COMPLEX_NUMBER(real=Xk[i].real, imag=Xk[i].imag)
            bins[i] = pointer(number)

        try:
            Xk_pointer = iterative_fft_4.ifft_radix_4_iterative_static_n(
                self.__backward_twid_factor, self.fft_size, cast(bins, POINTER(POINTER(COMPLEX_NUMBER))), length)
            Xk = Xk_pointer.contents
            result = []

            for i in range(Xk.length):
                complex_number_ptr = Xk.bin[i]
                complex_number = complex_number_ptr.contents
                result.append(
                    complex(complex_number.real, complex_number.imag))

            return result

        except Exception as e:
            print(e)
            sys.exit(-1)

    def ifft_symmetric(self, Xk: list[complex]):
        global iterative_fft, COMPLEX_NUMBER, FFT_BINS
        length = len(Xk)

        # create an complex number structure
        bins = (POINTER(COMPLEX_NUMBER) * length)()

        for i in range(length):
            number = COMPLEX_NUMBER(real=Xk[i].real, imag=Xk[i].imag)
            bins[i] = pointer(number)
        try:
            xn_pointer = iterative_fft.ifft_radix_4_iterative_symmetric(
                self.__backward_twid_factor, self.fft_size, cast(bins, POINTER(POINTER(COMPLEX_NUMBER))), length)
            xn = xn_pointer.contents
            result = []
            for i in range(xn.length):
                result.append(xn.bin[i])
            return result

        except Exception as e:
            print(e)
            sys.exit(-1)

    def convfft(self, xa: list[float], xb: list[float]):
        length_a = len(xa)
        xn_ptr_a = cast((c_double * length_a)(*xa), POINTER(c_double))
        length_b = len(xb)
        xn_ptr_b = cast((c_double * length_b)(*xb), POINTER(c_double))

        assert self.fft_size > length_a + length_b - \
            1, "FFT Size is smaller than the convolution length. FFT size is {} whereas the convolution length is {}".format(
                self.fft_size, length_a + length_b - 1)

        try:
            xn_ptr = conv_fft.convfft4_static_n(
                xn_ptr_a, xn_ptr_b, length_a, length_b, self.__forward_twid_factor, self.__backward_twid_factor, self.fft_size)
            xn = xn_ptr.contents
            result = []

            for i in range(xn.length):
                result.append(xn.bin[i])

            return result[:length_a + length_b]

        except Exception as e:
            print(e)
            sys.exit(-1)

    def convfft_overlap_save(self, xa: list[float], xb: list[float]):
        length_a = len(xa)
        xn_ptr_a = cast((c_double * length_a)(*xa), POINTER(c_double))
        length_b = len(xb)
        xn_ptr_b = cast((c_double * length_b)(*xb), POINTER(c_double))

        assert length_a == length_b, "each block must have the same length that is the sample length/chunksize. {} != {}".format(
            length_a, length_b)

        try:
            xn_ptr = conv_fft.convfft4_overlap_save_static_n(
                xn_ptr_a, xn_ptr_b, self.__forward_twid_factor, self.__backward_twid_factor, length_a)
            xn = xn_ptr.contents
            result = []

            for i in range(xn.length):
                result.append(xn.bin[i])

            return result[:length_a + length_b]

        except Exception as e:
            print(e)
            sys.exit(-1)

    def destroy(self):
        global util_fft
        util_fft.destroy_bin(self.__backward_twid_factor, self.fft_size // 2)
        util_fft.destroy_bin(self.__forward_twid_factor, self.fft_size // 2)
        self.__is_destroyed = True


class StaticSplitRadixFFT():
    # Static FFT for split radix (4 - 2)
    pass


if __name__ == "__main__":
    a = [1, 3, 2, 1, 4, 4, 4, 5, 6, 7, 1, 2, 3, 7, 5, 11]
    c = [1] * 16

    fft = Radix2FFT()
    b = fft.convfft(a, c)
    print(b)

    fft4 = StaticRadix4FFT(64)
    b4 = fft4.convfft(a, c)
    print(b4)

    for (x1, x2) in zip(b, b4):
        err_real = abs(x1.real - x2.real) / (x1.real + sys.float_info.min)
        err_imag = abs(x1.imag - x2.imag) / (x1.imag + sys.float_info.min)

        print("err_real : {} err_imag : {}".format(err_real, err_imag))

        if err_real < 0.1 and err_imag < 0.1:
            print("OK")

        else:
            print("Err")
            print("b2 : {}; b4 : {}".format(x1, x2))
            sys.exit(1)

    print("OK")
