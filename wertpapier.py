import math
import matplotlib.pyplot as plt
import numpy as np


def calculateInterest(rate, time_in_years):
    return pow((1 + rate), time_in_years)


def calculateInterestRate(interest, time_in_years):
    return (interest ** (1 / time_in_years)) - 1


def calculateTime(interest, rate):
    return math.log(interest, 1 + rate)


def presentValueBasic(couponRate, face, timeToMaturity, discountRate, frequency=1):
    return (((face * couponRate / frequency) *
            (1 - (1 + discountRate / frequency) ** (-timeToMaturity * frequency)) / (discountRate / frequency))
            + face * (1 + discountRate / frequency) ** (-timeToMaturity * frequency))


def generalSensitivity(toPeriod, toDiscountRate, couponRate, face=1000, fromPeriod=0.1, fromDiscountRate=0.001):
    ax = plt.axes(projection="3d")
    y = np.arange(fromPeriod, toPeriod, 0.1)
    x = np.arange(fromDiscountRate, toDiscountRate, 0.001)

    X, Y = np.meshgrid(x, y)
    Z = presentValueBasic(couponRate, face, Y, X)

    ax.set_title("Bond Sensitivity")
    ax.set_xlabel("Discount Rate")
    ax.set_ylabel("Time to Maturity")
    ax.set_zlabel("Present Value")

    ax.plot_surface(X, Y, Z, cmap="Spectral")
    plt.show()


