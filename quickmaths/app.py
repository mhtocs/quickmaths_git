from PIL import ImageFont

from imutils.video import WebcamVideoStream, FPS
from quickmaths.utils.window import Mouse, Graphics
from quickmaths.utils import image as im
from quickmaths.utils import component

import cv2
import time
import numpy as np


class App:

    def __init__(self, logger, src, ROOT_DIR):
        self.vs = WebcamVideoStream(src)
        self.fps = FPS()
        self.logger = logger
        self.ROOT_DIR = ROOT_DIR

        cv2.namedWindow("Webcam")
        cv2.namedWindow("roi")
        cv2.namedWindow("stacked")
        cv2.createTrackbar('dilate kernel', 'roi', 2, 5, self.none)
        cv2.createTrackbar('erode kernel', 'roi', 1, 5, self.none)

        self.mouse = Mouse(window="Webcam")
        self.gt = Graphics()
        # self.hist = Hist()
        self.msg = "draw a rectangle to continue ..."
        self.font_20 = ImageFont.truetype(f'{self.ROOT_DIR}/fonts/raleway/Raleway-Light.ttf', 20)
        self.font_30 = ImageFont.truetype(f'{self.ROOT_DIR}/fonts/raleway/Raleway-Light.ttf', 30)

    def run(self):
        self.vs.start()
        self.fps.start()
        self.logger.info("app started ...")
        frame = self.vs.read()
        wh, ww, _ = frame.shape
        cv2.moveWindow("Webcam", 0, 0)
        cv2.moveWindow("roi", ww, 0)
        cv2.moveWindow("stacked", 0, wh + 79)

        while True:
            frame = self.vs.read()
            # frame = frame[:, ::-1]  # flip
            orig = frame.copy()
            if self.mouse.rect:
                p1, p2 = self.mouse.rect
                roi = self.gt.draw_roi(orig, p1, p2)
                if roi.size != 0:
                    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

                    dk = cv2.getTrackbarPos("dilate kernel", "roi")
                    ek = cv2.getTrackbarPos("erode kernel", "roi")
                    thresh = im.thresify(gray_roi, dk, ek)
                    im.warp(thresh, roi)
                    # boxes, digits, cnts = component.get_symbols(
                    #     thresh, im=roi, draw_contours=True)

                    digits = component.connect_cnts2(thresh, roi)
                    # print(type(digits[0]))
                    stacked_digits = component.stack_digits(digits, im.resize)
                    # self.gt.draw_boxes(orig, boxes, p1, p2)

                    # self.hist.draw(gray_roi)
                    cv2.imshow('roi', thresh)
                    cv2.imshow('stacked', stacked_digits)

                # self.gt.write(orig, self.msg, (10, 10), self.font_20)
            else:
                orig[:, :] = cv2.blur(orig, (100, 100))
                windowRect = cv2.getWindowImageRect('Webcam')
                wx, wy, ww, wh = windowRect
                self.gt.write(orig, self.msg, (100, wh / 2 - 30), self.font_30)

            cv2.imshow('Webcam', orig)
            self.fps.update()

            key = cv2.waitKey(1)

            if (key & 0xFF == ord('q')) or (key & 0xFF == 27):
                self.logger.info('exiting ...')
                break

            elif key & 0xFF == ord('c'):
                CAPTURED_DIR = f'{self.ROOT_DIR}/screenshots'
                imageName = f'{CAPTURED_DIR}/{str(time.strftime("%Y_%m_%d_%H_%M"))}.png'
                cv2.imwrite(imageName, orig)
                self.logger.info(f'screenshot saved at {imageName}')

        self.fps.stop()
        self.vs.stop()
        cv2.destroyAllWindows()
        self.logger.info("elapsed time: {:.2f}".format(self.fps.elapsed()))
        self.logger.info("approx. FPS: {:.2f}".format(self.fps.fps()))

    def none(self, x):
        pass
