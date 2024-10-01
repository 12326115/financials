
import math
import matplotlib.pyplot as plt
import numpy as np

from wertpapier import presentValueBasic


class Bond:
    def __init__(self, couponRate, face, currentPrice, daysToMaturity, rating, frequency=1, transactionCosts=0):
        self.couponRate = couponRate
        self.face = face
        self.rating = rating
        self.frequency = frequency
        self.transactionCosts = transactionCosts
        self.daysToMaturity = daysToMaturity
        self.daysToNextCoupon = daysToMaturity % 365
        self.accruedInterest = self.calcAccruedInterest() if self.daysToNextCoupon != 0 else 0
        self.cleanPrice = currentPrice + self.accruedInterest
        self.cashflows = self.generateCashflowArray()

    def generateCashflowArray(self):
        cashflows = np.ndarray((math.ceil(self.daysToMaturity / 365) * self.frequency + 1), float)
        cashflows.fill(self.coupon() / self.frequency)
        cashflows[0] = -self.cleanPrice
        cashflows[-1] = cashflows[-1] + self.face
        return cashflows

    def calcAccruedInterest(self):
        return self.coupon() * ((365 - self.daysToNextCoupon) / 365.)

    def coupon(self):
        return self.couponRate * self.face

    def currentRate(self):
        return self.coupon() / self.cleanPrice

    def cashFlowInPeriod(self, period):
        return self.cashflows[period]

    # present value calculation
    def presentValueOfCashFlow(self, period, discountRate):
        return self.cashFlowInPeriod(period) / (1 + discountRate) ** period

    def discountedCashflows(self, discountRate):
        dcf = np.ndarray(self.cashflows.__len__() - 1, float)
        factor = self.daysToNextCoupon / 365 / self.frequency if self.daysToNextCoupon / 365 != 0 else 1
        dcr = 1 + discountRate / self.frequency
        for i in range(len(self.cashflows) - 1):
            dcf[i] = self.cashflows[i + 1] / np.power(dcr, i + factor)
        return dcf

    def presentValue(self, discountRate):
        return self.discountedCashflows(discountRate).sum() - self.transactionCosts

    def netPresentValue(self, discountRate):
        return self.presentValue(discountRate) - self.cleanPrice

    # sensitivity calculation
    def sensitivity(self, toDiscountRate, fromDiscountRate=0.001):
        return presentValueBasic(self.couponRate, self.face, self.daysToMaturity / 365,
                                 np.arange(fromDiscountRate, toDiscountRate, 0.001), self.frequency)

    def showSensitivity(self, toDiscountRate, fromDiscountRate=0.001):
        ax = plt.axes()

        x = np.arange(fromDiscountRate, toDiscountRate, 0.001)
        y = self.sensitivity(toDiscountRate, fromDiscountRate)

        ax.set_title("Bond Sensitivity")
        ax.set_xlabel("Discount Rate / Yield to Maturity")
        ax.set_ylabel("Present Value")

        ax.plot(x, y)
        plt.show()

    # internal rate of return calculation
    def irr(self):
        top = 1.
        bottom = 0.

        while self.netPresentValue(top) > 0:
            top *= 2

        discountRate = (top + bottom) / 2.

        for i in range(50):
            npv = self.netPresentValue(discountRate)

            if np.abs(npv) < 1e-5:
                return discountRate
            elif npv > 0:
                bottom = discountRate
            else:
                top = discountRate
            discountRate = (top + bottom) / 2.
        return discountRate

    def macaulayDuration(self, discountRate):
        dur = 0
        pv = self.presentValue(discountRate)
        dcf = self.discountedCashflows(discountRate)
        for i, j in np.ndenumerate(dcf):
            dur += j / pv * (i[0] + 1) / self.frequency

        return dur

    def modifiedDuration(self, discountRate):
        return self.macaulayDuration(discountRate)/(1 + discountRate / self.frequency)

    def effectiveDuration(self, discountRate, rateChange=0.01):
        return ((self.presentValue(discountRate - rateChange) - self.presentValue(discountRate + rateChange))
                / (2 * rateChange * self.presentValue(discountRate)))

    def convexity(self, discountRate, rateChange):
        return (self.presentValue(discountRate - rateChange) + self.presentValue(discountRate + rateChange)
                - 2 * self.presentValue(discountRate)) / (self.presentValue(discountRate) * rateChange ** 2)

