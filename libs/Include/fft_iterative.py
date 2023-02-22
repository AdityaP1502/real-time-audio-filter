from ctypes import *
import sys
import os.path as path
import random
from time import time
from multiprocessing import Value
n_finished = Value("i", 0)

"""
A python wrapper function for c fft iteretive function
"""

SHARED_LIBS_DIR_FFT = path.abspath("libs/shared/libitfft.so")
SHARED_LIBS_DIR_CONVFFT = path.abspath("libs/shared/libconv.so")

# Structure definition 

class COMPLEX_NUMBER(Structure):
    _fields_ = [
        ("real", c_double), 
        ("imag", c_double), 
    ]

bins = POINTER(POINTER(COMPLEX_NUMBER))

class FFT_BINS(Structure):
    global bins
    _fields_ = [
        ("bin", bins), 
        ("length", c_int), 
    ]

class IFFT_SYMMETRIC_BINS(Structure):
    _fields_ = [
        ("bin", POINTER(c_double)), 
        ("length", c_int), 
    ]

# load shared library
iterative_fft = CDLL(SHARED_LIBS_DIR_FFT)
conv_fft = CDLL(SHARED_LIBS_DIR_CONVFFT)

# function definition
iterative_fft.fft_iterative.argtypes = [POINTER(c_double), c_int, c_char_p]
iterative_fft.fft_iterative.restype = POINTER(FFT_BINS)

iterative_fft.ifft_iterative.argtypes = [bins, c_int, c_char_p]
iterative_fft.ifft_iterative.restype = POINTER(FFT_BINS)

iterative_fft.ifft_iterative_symmetric.argtypes = [bins, c_int, c_char_p]
iterative_fft.ifft_iterative_symmetric.restype = POINTER(IFFT_SYMMETRIC_BINS)

conv_fft.convfft.argtypes = [POINTER(c_double), POINTER(c_double), c_int, c_int]
conv_fft.convfft.restype = POINTER(IFFT_SYMMETRIC_BINS)

conv_fft.convfft_overlap_save.argtypes = [POINTER(c_double), POINTER(c_double), c_int]
conv_fft.convfft_overlap_save.restype = POINTER(IFFT_SYMMETRIC_BINS)
# function wrapper
def fft(xn, order = "NR"):
    global iterative_fft

    if len(order) != 2:
        raise ValueError("Invalid order")
    
    order = order + '\0'
    length = len(xn)

    xn_ptr = cast((c_double * length)(*xn), POINTER(c_double))
    order_ptr = c_char_p(bytes(order, 'UTF-8'))
    try:
        Xk_pointer = iterative_fft.fft_iterative((xn_ptr), length, order_ptr)
        Xk = Xk_pointer.contents
        result = []

        for i in range(Xk.length):
            complex_number_ptr = Xk.bin[i]
            complex_number = complex_number_ptr.contents
            result.append(complex(complex_number.real, complex_number.imag))

        return result

    except Exception as e:
        print(e)
        sys.exit(-1)

def ifft(Xk : list[complex], order : str = "NR"):
    global iterative_fft, COMPLEX_NUMBER, FFT_BINS

    if len(order) != 2:
        raise ValueError("Invalid order")
    
    order = order + '\0'
    length = len(Xk)

    # create an complex number structure
    bins = (POINTER(COMPLEX_NUMBER) * length) ()
    order_ptr = c_char_p(bytes(order, 'UTF-8'))

    for i in range(length):
        number =  COMPLEX_NUMBER(real=Xk[i].real, imag=Xk[i].imag) 
        bins[i] = pointer(number)

    try:
        Xk_pointer = iterative_fft.ifft_iterative(cast(bins, POINTER(POINTER(COMPLEX_NUMBER))), length, order_ptr)
        Xk = Xk_pointer.contents
        result = []

        for i in range(Xk.length):
            complex_number_ptr = Xk.bin[i]
            complex_number = complex_number_ptr.contents
            result.append(complex(complex_number.real, complex_number.imag))

        return result

    except Exception as e:
        print(e)
        sys.exit(-1)


def ifft_symmetric(Xk : list[complex], order : str = "NR"):
    global iterative_fft, COMPLEX_NUMBER, FFT_BINS

    if len(order) != 2:
        raise ValueError("Invalid order")
    
    order = order + '\0'
    length = len(Xk)

    # create an complex number structure
    bins = (POINTER(COMPLEX_NUMBER) * length) ()
    order_ptr = c_char_p(bytes(order, 'UTF-8'))

    for i in range(length):
        number =  COMPLEX_NUMBER(real=Xk[i].real, imag=Xk[i].imag) 
        bins[i] = pointer(number)

    try:
        xn_pointer = iterative_fft.ifft_iterative_symmetric(cast(bins, POINTER(POINTER(COMPLEX_NUMBER))), length, order_ptr)
        xn = xn_pointer.contents
        result = []

        for i in range(xn.length):
            result.append(xn.bin[i])

        return result

    except Exception as e:
        print(e)
        sys.exit(-1)

def convfft(xa : list[float], xb : list[float]):
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

def convfft_overlap_save(xa : list[float], xb : list[float]):
    length_a = len(xa)
    xn_ptr_a = cast((c_double * length_a)(*xa), POINTER(c_double))
    length_b = len(xb)
    xn_ptr_b = cast((c_double * length_b)(*xb), POINTER(c_double))

    assert length_a == length_b, "each block must have the same length that is the sample length/chunksize. {} != {}".format(length_a, length_b)

    try:
        xn_ptr = conv_fft.convfft_overlap_save(xn_ptr_a, xn_ptr_b, length_a)
        xn = xn_ptr.contents
        result = []

        for i in range(xn.length):
            result.append(xn.bin[i])

        return result[:length_a + length_b]

    except Exception as e:
        print(e)
        sys.exit(-1)

def profiler(id):
    global time_taken, N, n_finished
    for j in range(20):
            a = [random.random() * 100 for i in range(N)]
            b = [random.random() * 100 for i in range(N)]
            start_time = time()
            _ = convfft(a, b)
            end_time = time()
            time_taken[id].append((end_time - start_time) * 1000)
            N <<= 1
            n_finished += 1

def job(n_job):
    import threading
    from time import sleep

    global n_finished, N

    for i in range(n_job):
        t = threading.Thread(target=profiler, args=(i,  ))
        t.start()

        while t.is_alive():
            sys.stdout.write("\rLoading. {}/20           ".format(n_finished))
            sleep(0.3)
            sys.stdout.write("\rLoading.. {}/20          ".format(n_finished))
            sleep(0.3)
            sys.stdout.write("\rLoading... {}/20         ".format(n_finished))
            sleep(0.3)
        
        sys.stdout.write("\rLoading                                                     ")
        n_finished = 0
        N = 2
    
if __name__ == "__main__":
    n_job = 10
    N = 2
    n_finished = 0

    time_taken = [[] for i in range(n_job)]
    job(n_job)
    content = ""
    for j in range(20):
        run : list[str] = [str(time_taken[i][j]) for i in range(n_job)]
        new_content = ";".join(run)
        content += "{};".format(2 ** (j + 1)) + new_content + "\n"
    
    with open("data.csv", "w") as f:
        f.write(content)
    
    sys.stdout.write("\r                                                    ")
    print("\rdone!")
    