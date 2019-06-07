import cv2
import numpy as np
import matplotlib.pyplot as plt

from PIL import ImageFont, ImageDraw, Image


class Mouse:

    def __init__(self, window="Webcam", rect=((0, 0), (0, 0))):
        self.point1 = (0, 0)
        self.point2 = (0, 0)
        self.rect = None
        self.click = False
        self.drag = False
        self.select = False
        cv2.setMouseCallback(window, self.handler, None)

    def handler(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and not self.click:
            print("DOWN")
            self.select = False
            self.point1 = (x, y)
            self.click = True

        if event == cv2.EVENT_MOUSEMOVE and self.click:
            # print(f"{x},{y}")
            self.point2 = (x, y)
            self.drag = True
            self.rect = (self.point1, self.point2)

        if event == cv2.EVENT_LBUTTONUP and self.click:
            print("UP")
            self.point2 = (x, y)
            self.click = False
            self.select = True

            if self.point1 != self.point2:
                self.select = True
                self.rect = (self.point1, self.point2)
            else:
                self.select = False
                self.rect = None


class Graphics:

    def __init(self):
        pass

    # returns roi
    def draw_roi(self, img, point1, point2):
        x1, y1 = point1
        x2, y2 = point2

        # swap if selecting from right to left
        if x1 > x2 and y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        if x2 > x1 and y1 > y2:
            # x1, x2 = x2, x1
            y1, y2 = y2, y1

        if x1 > x2 and y2 > y1:
            x1, x2 = x2, x1

        roi = img[y1:y2, x1:x2].copy()
        img[:, :] = cv2.blur(img, (100, 100))
        img[y1:y2, x1:x2] = roi
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 1)
        self.bordered_rect(img, (x1, y1), (x1, y2), (x2, y1), (x2, y2), 30)
        return img[y1:y2, x1:x2]  # roi

    def draw_static_roi(self, img, point1, point2, roi):
        x1, y1 = point1
        x2, y2 = point2

        # swap if selecting from right to left
        if x1 > x2 and y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        if x2 > x1 and y1 > y2:
            # x1, x2 = x2, x1
            y1, y2 = y2, y1

        if x1 > x2 and y2 > y1:
            x1, x2 = x2, x1

        img[:, :] = cv2.blur(img, (100, 100))
        img[y1:y2, x1:x2] = roi
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 1)
        self.border(img, (x1, y1), (x1, y2), (x2, y1), (x2, y2), 30)

    def bordered_rect(self, img, point1, point2, point3, point4, line_length):

        x1, y1 = point1
        x2, y2 = point2
        x3, y3 = point3
        x4, y4 = point4

        # cv2.circle(img, (x1, y1), 5, (255, 0, 255), -1)    #-- top_left
        # cv2.circle(img, (x2, y2), 5, (255, 0, 255), -1)    #-- bottom-left
        # cv2.circle(img, (x3, y3), 5, (255, 0, 255), -1)    #-- top-right
        # cv2.circle(img, (x4, y4), 5, (255, 0, 255), -1)    #-- bottom-right

        cv2.rectangle(img, (x1, y1), (x1 + 5, y1 + line_length),
                      (255, 255, 255), -1)  # -- top-left
        cv2.rectangle(img, (x1, y1), (x1 + line_length, y1 + 5),
                      (255, 255, 255), -1)

        cv2.rectangle(img, (x2, y2), (x2 + 5, y2 - line_length),
                      (255, 255, 255), -1)  # -- bottom-left
        cv2.rectangle(img, (x2, y2), (x2 + line_length, y2 - 5),
                      (255, 255, 255), -1)

        cv2.rectangle(img, (x3, y3), (x3 - line_length, y3 + 5),
                      (255, 255, 255), -1)  # -- top-right
        cv2.rectangle(img, (x3, y3), (x3 - 5, y3 + line_length),
                      (255, 255, 255), -1)

        cv2.rectangle(img, (x4, y4), (x4 - 5, y4 - line_length),
                      (255, 255, 255), -1)  # -- bottom-right
        cv2.rectangle(img, (x4, y4), (x4 - line_length, y4 - 5),
                      (255, 255, 255), -1)

        # return img

    def write(self, image, text, pos, font=None, color="#ff0000"):
        text_to_show = text
        x, y = pos
        # Convert the image to RGB (OpenCV uses BGR)
        cv2_im_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Pass the image to PIL
        pil_im = Image.fromarray(cv2_im_rgb)

        draw = ImageDraw.Draw(pil_im)
        # use a truetype font

        # Draw the text
        draw.text((x, y), text_to_show, font=font, fill=color)

        # Get back the image to OpenCV
        cv2_im_processed = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
        image[:, :] = cv2_im_processed

        return image

    def draw_boxes(self, im, boxes, p1, p2):
        x1, y1 = p1
        x2, y2 = p2

        for x, y, w, h in boxes:
            cv2.rectangle(im, (x1 + x, y1 + y),
                          (x1 + x + w, y1 + y + h), (0, 255, 0), 1)


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
