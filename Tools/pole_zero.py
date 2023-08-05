from Tools.fft.fft import Radix2FFT
from cmath import exp, polar
from math import pi


def fromZeroToPolynomial(zeros):
    # given list of zeros
    # calculate the coefficient of the polynomial
    # (z - z1)(z - z2)(z - z3)...(z - zn)
    fft = Radix2FFT()
    coefs = [[1, -zero] for zero in zeros]
    k = len(coefs)
    while k > 1:
        for i in range(k >> 1):
            coefs[i] = fft.convfft(coefs[i], coefs[i + 1])

        if k % 2 == 1:
            coefs[k >> 1] = coefs[k - 1]

        k = (k >> 1) + (k % 2)

    return coefs[0]


def calculate_freq_response(data):
    p, w = data
    # (z - zk) -> (e^jw - zk)
    def find_response(x): return exp(1j * pi * w) - x
    def seperate_response(x): return polar(x)
    def freq_response(x): return seperate_response(find_response(x))

    responses = map(freq_response, p)
    freq_phase_response = 0
    freq_mag_response = 1

    for (mag, phase) in responses:
        freq_mag_response *= mag
        freq_phase_response += phase

    return freq_mag_response, freq_phase_response


if __name__ == "__main__":
    zeros = [1, 2, 3, 4, 5, 6]
    coef = fromZeroToPolynomial(zeros)
    print(coef)
