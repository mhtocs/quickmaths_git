# histogram
import matplotlib.pyplot as plt
import numpy as np
import cv2


class Hist:

    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.fig.set_size_inches(6, 2)
        self.ax.set_title('Histogram (grayscale)')
        self.ax.set_xlabel('Bin')
        self.ax.set_ylabel('Frequency')
        self.lw = 3
        self.alpha = 0.5
        self.bins = 16
        self.lineGray, = self.ax.plot(
            np.arange(self.bins), np.zeros((self.bins, 1)), c='k', lw=self.lw)
        self.ax.set_xlim(0, self.bins - 1)
        self.ax.set_ylim(0, 1)
        self.old = None
        plt.rcParams["figure.figsize"] = (1, 1)
        plt.ion()
        plt.show()

    def draw(self, gray):
        # hist
        numPixels = np.prod(gray.shape[:2])
        histogram = cv2.calcHist(
            [gray], [0], None, [self.bins], [0, 255]) / numPixels
        if self.old is not None:
            self.chi2_distance(self.old, histogram)
        self.old = histogram
        self.lineGray.set_ydata(histogram)
        self.fig.canvas.draw()

    def chi2_distance(self, histA, histB, eps=1e-10):
        # compute the chi-squared distance
        d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
                          for (a, b) in zip(histA, histB)])
        # return the chi-squared distance
        return d
