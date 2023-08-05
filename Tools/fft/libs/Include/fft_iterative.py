from ctypes import *
import platform
import os.path as path

"""
Python CDLL Function and Structure Definition for FFT
"""

if platform.system() == "Linux":
    SHARED_LIBS_DIR_FFT = path.abspath("Tools/fft/libs/shared/libitfft.so")
    SHARED_LIBS_DIR_CONVFFT = path.abspath("Tools/fft/libs/shared/libconv.so")
    SHARED_LIBS_DIR_UTILFFT = path.abspath("Tools/fft/libs/shared/libfft.so")
    SHARED_LIBS_DIR_FFT_4 = path.abspath("Tools/fft/libs/shared/itfft4.so")

elif platform.system() == "Windows":
    SHARED_LIBS_DIR_FFT = path.abspath("Tools/fft/libs/shared/itfft.dll")
    SHARED_LIBS_DIR_CONVFFT = path.abspath("Tools/fft/libs/shared/conv.dll")
    SHARED_LIBS_DIR_UTILFFT = path.abspath("Tools/fft/libs/shared/fft.dll")
    SHARED_LIBS_DIR_FFT_4 = path.abspath("Tools/fft/libs/shared/itfft4.dll")
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
iterative_fft_4 = CDLL(SHARED_LIBS_DIR_FFT_4)
conv_fft = CDLL(SHARED_LIBS_DIR_CONVFFT)
util_fft = CDLL(SHARED_LIBS_DIR_UTILFFT)

# c function definition
util_fft.precompute_twiddle_factor.argtypes = [c_int, c_int]
util_fft.precompute_twiddle_factor.restype = bins

util_fft.precompute_twiddle_factor_radix_4.argtypes = [c_int, c_int]
util_fft.precompute_twiddle_factor_radix_4.restype = bins

util_fft.destroy_bin.argtypes = [bins, c_int]
util_fft.destroy_bin.restypes = c_void_p

# non static fft
iterative_fft.fft_iterative.argtypes = [POINTER(c_double), c_int, c_char_p]
iterative_fft.fft_iterative.restype = POINTER(FFT_BINS)

iterative_fft.ifft_iterative.argtypes = [bins, c_int, c_char_p]
iterative_fft.ifft_iterative.restype = POINTER(FFT_BINS)

iterative_fft.ifft_iterative_symmetric.argtypes = [bins, c_int, c_char_p]
iterative_fft.ifft_iterative_symmetric.restype = POINTER(IFFT_SYMMETRIC_BINS)

conv_fft.convfft.argtypes = [
    POINTER(c_double), POINTER(c_double), c_int, c_int]
conv_fft.convfft.restype = POINTER(IFFT_SYMMETRIC_BINS)

conv_fft.convfft_overlap_save.argtypes = [
    POINTER(c_double), POINTER(c_double), c_int]
conv_fft.convfft_overlap_save.restype = POINTER(IFFT_SYMMETRIC_BINS)

# static fft
iterative_fft.fft_iterative_static_n.argtypes = [
    bins, c_int, POINTER(c_double), c_int, c_char_p]
iterative_fft.fft_iterative_static_n.restype = POINTER(FFT_BINS)

iterative_fft.ifft_iterative_static_n.argtypes = [
    bins, bins, c_int, c_int, c_char_p]
iterative_fft.ifft_iterative_static_n.restype = POINTER(FFT_BINS)

iterative_fft.ifft_iterative_symmetric_static_n.argtypes = [
    bins, bins, c_int, c_int, c_char_p]
iterative_fft.ifft_iterative_symmetric_static_n.restype = POINTER(
    IFFT_SYMMETRIC_BINS)

conv_fft.convfft_static_n.argtypes = [
    POINTER(c_double), POINTER(c_double), c_int, c_int, bins, bins, c_int]
conv_fft.convfft_static_n.restype = POINTER(IFFT_SYMMETRIC_BINS)

conv_fft.convfft_overlap_save_static_n.argtypes = [
    POINTER(c_double), POINTER(c_double), bins, bins, c_int]
conv_fft.convfft_overlap_save_static_n.restype = POINTER(IFFT_SYMMETRIC_BINS)

# Radix 4
iterative_fft_4.fft_radix_4_iterative_static_n.argtypes = [
    bins, c_int, POINTER(c_double), c_int]
iterative_fft_4.fft_radix_4_iterative_static_n.restype = POINTER(FFT_BINS)

iterative_fft_4.ifft_radix_4_iterative_static_n.argtypes = [
    bins, c_int, bins, c_int]
iterative_fft_4.ifft_radix_4_iterative_static_n.restype = POINTER(FFT_BINS)

iterative_fft_4.ifft_radix_4_iterative_symmetric_static_n.argtypes = [
    bins, c_int, bins, c_int]
iterative_fft_4.ifft_radix_4_iterative_symmetric_static_n.restype = POINTER(
    IFFT_SYMMETRIC_BINS)

conv_fft.convfft4_static_n.argtypes = [
    POINTER(c_double), POINTER(c_double), c_int, c_int, bins, bins, c_int]
conv_fft.convfft4_static_n.restype = POINTER(IFFT_SYMMETRIC_BINS)

conv_fft.convfft4_overlap_save_static_n.argtypes = [
    POINTER(c_double), POINTER(c_double), bins, bins, c_int]
conv_fft.convfft4_overlap_save_static_n.restype = POINTER(IFFT_SYMMETRIC_BINS)

if __name__ == "__main__":
    # test function definition
    print("OK")
