import cv2
import numpy as np
import imutils
from scipy import ndimage


def thresify(gray, dk, ek):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)

    _, thresh = cv2.threshold(
        blackhat, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    thresh = cv2.GaussianBlur(thresh, (1, 1), cv2.BORDER_DEFAULT)

    thresh = cv2.dilate(thresh, np.ones((dk, dk)))
    if ek != 0:
        thresh = cv2.erode(thresh, np.ones((ek, ek)))

    return thresh


# def warp(thresh, im):
#     cnts = cv2.findContours(thresh.copy(), cv2.RETR_LIST,
#                             cv2.CHAIN_APPROX_SIMPLE)
#     cnts = cnts[0] if imutils.is_cv2() else cnts[1]
#     cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
#     screenCnt = None
#     for c in cnts:
#         peri = cv2.arcLength(c, True)
#         approx = cv2.approxPolyDP(c, 0.02 * peri, True)
#         if len(approx) == 4:
#             screenCnt = approx
#             break

    # cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)


def getBestShift(img):
    cy, cx = ndimage.measurements.center_of_mass(img)

    rows, cols = img.shape
    shiftx = np.round(cols / 2.0 - cx).astype(int)
    shifty = np.round(rows / 2.0 - cy).astype(int)

    return shiftx, shifty


def shift(img, sx, sy):
    rows, cols = img.shape
    M = np.float32([[1, 0, sx], [0, 1, sy]])
    shifted = cv2.warpAffine(img, M, (cols, rows))
    return shifted


def resize(sym, IMG_ROW=32, IMG_COL=32):
    # Resize
    border_v = 0
    border_h = 0
    if (IMG_COL / IMG_ROW) >= (sym.shape[0] / sym.shape[1]):
        border_v = int(
            (((IMG_COL / IMG_ROW) * sym.shape[1]) - sym.shape[0]) / 2)
    else:
        border_h = int(
            (((IMG_ROW / IMG_COL) * sym.shape[0]) - sym.shape[1]) / 2)
    sym = cv2.copyMakeBorder(sym, border_v, border_v,
                             border_h, border_h, cv2.BORDER_CONSTANT, 0)
    sym = cv2.resize(sym, (IMG_ROW, IMG_COL), interpolation=cv2.INTER_AREA)
    # sym = cv2.cvtColor(sym, cv2.COLOR_BGR2GRAY)
    _, sym = cv2.threshold(
        sym.copy(), 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    sym = cv2.dilate(sym, np.ones((3, 3)))
    sym = cv2.erode(sym, np.ones((2, 2)))

    # padding
    gray = sym

    # while gray.shape[0] != 0 and np.sum(gray[0]) == 0:
    #     gray = gray[1:]

    # while gray.shape[1] != 0 and np.sum(gray[:, 0]) == 0:
    #     gray = np.delete(gray, 0, 1)

    # while gray.shape[0] != 0 and np.sum(gray[-1]) == 0:
    #     gray = gray[:-1]

    # while gray.shape[1] != 0 and np.sum(gray[:, -1]) == 0:
    #     gray = np.delete(gray, -1, 1)

    rows, cols = gray.shape

    if rows > cols:
        factor = 20.0 / rows
        rows = 20
        cols = int(round(cols * factor))
        gray = cv2.resize(gray, (cols, rows))
    else:
        factor = 20.0 / cols
        cols = 20
        rows = int(round(rows * factor))
        gray = cv2.resize(gray, (cols, rows))

    colsPadding = (int(np.ceil((28 - cols) / 2.0)),
                   int(np.floor((28 - cols) / 2.0)))
    rowsPadding = (int(np.ceil((28 - rows) / 2.0)),
                   int(np.floor((28 - rows) / 2.0)))
    gray = np.lib.pad(gray, (rowsPadding, colsPadding), 'constant')
    shiftx, shifty = getBestShift(gray)
    shifted = shift(gray, shiftx, shifty)
    gray = shifted
    return gray
