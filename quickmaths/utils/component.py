import numpy as np
import cv2

avgHeight = 0


def get_symbols(thresh, im=None, draw_contours=False):

    thresh, cnts, _ = cv2.findContours(
        thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(cnts) > 0:
        cnts, _ = sort_contours(cnts)
    avgCntArea = np.mean([cv2.contourArea(k) for k in cnts])
    digits = []
    boxes = []
    cnts2 = []

    for i, c in enumerate(cnts):
        approx = cv2.approxPolyDP(c, 0.08 * cv2.arcLength(c, True), True)
        if cv2.contourArea(c) < avgCntArea / 15 or cv2.contourArea(c) < 5:
            continue
        (x, y, w, h) = cv2.boundingRect(c)

        mask = np.zeros(thresh.shape, dtype="uint8")
        cv2.drawContours(mask, [c], -1, 255, -1)

        mask = cv2.bitwise_and(thresh, thresh, mask=mask)

        digit = mask[y - 8:y + h + 8, x - 8:x + w + 8]

        boxes.append((x, y, w, h))
        digits.append(digit)
        cnts2.append(c)
        ar = round(w / float(h))

        # draw contours
        if draw_contours:
            if im is None:
                raise Exception(
                    'im cannot be None , if draw_contours is True')
            else:
                # cv2.drawContours(im, [c], -1, (255, 255, 255), 1)
                circular = 4 * np.pi * \
                    (cv2.contourArea(c) / np.square(cv2.arcLength(c, True)))

                shape = 'p'
                if 0.55 < circular < 1.2:
                    shape = 'c'
                elif len(approx) == 2 and ar > 1:
                    shape = 'h'
                elif len(approx) == 2 and ar < 1:
                    shape = 'v'
                cv2.putText(im, shape, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)

    # sorted_boxes = []
    # sorted_digits = []

    # for (x, y, w, h), d in sorted(zip(boxes, digits)):
    #     sorted_boxes.append((x, y, w, h))
    #     sorted_digits.append(d)
    if cnts:
        cv2.drawContours(im, [cnts[0]], -1, (255, 255, 255), 1)
    return boxes, digits, cnts


def get_cnts(thresh):
    thresh, cnts, _ = cv2.findContours(
        thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    avgCntArea = np.mean([cv2.contourArea(k) for k in cnts])

    global avgHeight
    avgHeight = np.mean([cv2.boundingRect(k)[-1] for k in cnts])
    cnts2 = []
    boundingBoxes2 = []
    shapes = []
    if len(cnts) > 0:
        cnts, boundingBoxes = sort_contours(cnts)
    else:
        return cnts, boundingBoxes2, []

    # clean
    for i, c in enumerate(cnts):
        approx = cv2.approxPolyDP(c, 0.08 * cv2.arcLength(c, True), True)

        if cv2.contourArea(c) < avgCntArea / 15:
            continue
        cnts2.append(c)
        box = boundingBoxes[i]
        x, y, w, h = box
        ar = w / float(h)

        circular = 4 * np.pi * (cv2.contourArea(c) /
                                np.square(cv2.arcLength(c, True)))

        shape = 'p'
        if 0.7 < circular < 1.2:
            shape = 'c'
        elif len(approx) == 2 and ar > 1:
            shape = 'h'
        elif len(approx) == 2 and ar < 1:
            shape = 'v'

        boundingBoxes2.append(box)
        shapes.append(shape)

    return (cnts2, boundingBoxes2, shapes)


def iseqmark(bb1, bb2, shape1, shape2):
    x1, y1, w1, h1 = bb1
    x2, y2, w2, h2 = bb2

    return shape1 == 'h' and shape2 == 'h' and abs(x1 - x2) < 30 and abs((x1 + w1) - (x2 + w2)) < 30 and abs((y1 + h1) - y2) <= avgHeight


def isdiv(bb1, bb2, bb3, shape1, shape2, shape3):
    x1, y1, w1, h1 = bb1
    x2, y2, w2, h2 = bb2
    x3, y3, w3, h3 = bb3
    return shape1 == 'h' and shape2 == 'c' and shape3 == 'c' and (x1 < x2 < x3 < x1 + w1) and max(y2, y3) > y1 and min(y2, y3) < y1 and max(y2, y3) - min(y2, y3) < 1.2 * abs((x1 + w1) - x1)


def isfraction(bb1, bb2, bb3, shape1, shape2, shape3):
    x1, y1, w1, h1 = bb1
    x2, y2, w2, h2 = bb2
    x3, y3, w3, h3 = bb3

    cenX1 = x1 + w1 / 2
    cenX2 = x2 + w2 / 2
    cenX3 = x3 + w3 / 2

    case1 = shape1 != 'c' and shape2 != 'c' and shape3 == 'h' and (
        y1 < y3 < (y2 + h2) or y2 < y3 < (y1 + h1))

    case2 = shape3 != 'c' and shape1 != 'c' and shape2 == 'h' and (
        y3 < y2 < (y1 + h1) or y1 < y2 < (y3 + h3))

    case3 = shape2 != 'c' and shape3 != 'c' and shape1 == 'h' and (
        y2 < y1 < (y3 + h3) or y3 < y1 < (y2 + h2))

    return (case1 or case2 or case3) and max(cenX1, cenX2, cenX3) - min(cenX1, cenX2, cenX3) < 50


def connect_cnts2(thresh, im):
    cnts, bbs, shapes = get_cnts(thresh)
    i = 0
    digits = []
    while i < len(bbs) - 1:
        x1, y1, w1, h1 = bbs[i]
        x2, y2, w2, h2 = bbs[i + 1]
        equation = iseqmark(bbs[i], bbs[i + 1], shapes[i], shapes[i + 1])
        fraction = False
        div = False

        if i < len(bbs) - 2:
            x3, y3, w3, h3 = bbs[i + 2]
            div = isdiv(bbs[i], bbs[i + 1], bbs[i + 2],
                        shapes[i], shapes[i + 1], shapes[i + 2])

            fraction = isfraction(
                bbs[i], bbs[i + 1], bbs[i + 2], shapes[i], shapes[i + 1], shapes[i + 2])

        if equation and not fraction:

            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [cnts[i], cnts[i + 1]], -1, 255, -1)
            mask = cv2.bitwise_and(thresh, thresh, mask=mask)
            x_min = min(x1, x2)
            y_min = min(y1, y2)

            x_max = max(x1 + w1, x2 + w1)
            y_max = max(y1 + h1, y2 + h2)

            # cv2.imshow('eq_mask', mask)
            digit = mask[y_min - 8:y_max + 8, x_min - 8:x_max + 8]
            # cv2.rectangle(im, (x_min - 8, y_min - 8),
            #               (x_max + 8, y_max + 8), (255, 0, 0), 1)
            digits.append(digit)
            i += 2

        elif div and not fraction:
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(
                mask, [cnts[i], cnts[i + 1], cnts[i + 2]], -1, 255, -1)
            mask = cv2.bitwise_and(thresh, thresh, mask=mask)
            x_min = min(x1, x2, x3)
            y_min = min(y1, y2, y3)

            x_max = max(x1 + w1, x2 + w2, x3 + w3)
            y_max = max(y1 + h1, y2 + h2, y3 + h3)

            cv2.imshow('div_mask', mask)
            digit = mask[y_min - 8:y_max + 8, x_min - 8:x_max + 8]
            cv2.rectangle(im, (x_min - 8, y_min - 8),
                          (x_max + 8, y_max + 8), (255, 0, 0), 1)

            digits.append(digit)
            i += 3

        else:
            x, y, w, h = bbs[i]
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [cnts[i]], -1, 255, -1)
            mask = cv2.bitwise_and(thresh, thresh, mask=mask)
            digit = mask[y - 8:y + h + 8, x - 8:x + w + 8]
            digits.append(digit)
            i += 1

    while i < len(bbs):
        x, y, w, h = bbs[i]
        mask = np.zeros(thresh.shape, dtype="uint8")
        cv2.drawContours(mask, [cnts[i]], -1, 255, -1)
        mask = cv2.bitwise_and(thresh, thresh, mask=mask)
        digit = mask[y - 8:y + h + 8, x - 8:x + w + 8]
        digits.append(digit)
        i += 1

    return digits


def connect_cnts(thresh, im):
    cnts, boundingBoxes, shapes = get_cnts(thresh)
    i = 0
    digits = []
    while i < len(shapes):

        # equal sign
        if i < len(shapes) - 1 and shapes[i] == 'h' and shapes[i + 1] == 'h':
            x1, y1, w1, h1 = boundingBoxes[i]
            x2, y2, w2, h2 = boundingBoxes[i + 1]

            if abs(x1 - x2) < 30 and abs((x1 + w1) - (x2 + w2)) < 30:
                mask = np.zeros(thresh.shape, dtype="uint8")
                cv2.drawContours(mask, [cnts[i], cnts[i + 1]], -1, 255, -1)
                mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                x_min = min(x1, x2)
                y_min = min(y1, y2)

                x_max = max(x1 + w1, x2 + w1)
                y_max = max(y1 + h1, y2 + h2)

                # cv2.imshow('eq_mask', mask)
                digit = mask[y_min - 8:y_max + 8, x_min - 8:x_max + 8]
                # cv2.rectangle(im, (x_min - 8, y_min - 8),
                #               (x_max + 8, y_max + 8), (255, 0, 0), 1)

                digits.append(digit)
                i += 2
                continue

        if i < len(shapes) - 2 and shapes[i] == 'h' and shapes[i + 1] == 'c' and shapes[i + 2] == 'c':
            x1, y1, w1, h1 = boundingBoxes[i]
            x2, y2, w2, h2 = boundingBoxes[i + 1]
            x3, y3, w3, h3 = boundingBoxes[i + 2]
            # and y1 - 3 * w1 / 4 < min(y2, y3) < y1 and y1 < max(y2, y3) < y1
            # + 3 * w1 / 4:
            if (x1 < x2 < x3 < x1 + w1) and max(y2, y3) > y1 and min(y2, y3) < y1 and max(y2, y3) - min(y2, y3) < 1.2 * abs((x1 + w1) - x1):

                mask = np.zeros(thresh.shape, dtype="uint8")
                cv2.drawContours(
                    mask, [cnts[i], cnts[i + 1], cnts[i + 2]], -1, 255, -1)
                mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                x_min = min(x1, x2, x3)
                y_min = min(y1, y2, y3)

                x_max = max(x1 + w1, x2 + w2, x3 + w3)
                y_max = max(y1 + h1, y2 + h2, y3 + h3)

                cv2.imshow('div_mask', mask)
                digit = mask[y_min - 8:y_max + 8, x_min - 8:x_max + 8]
                cv2.rectangle(im, (x_min - 8, y_min - 8),
                              (x_max + 8, y_max + 8), (255, 0, 0), 1)

                digits.append(digit)

                i += 3
                continue

        x, y, w, h = boundingBoxes[i]
        mask = np.zeros(thresh.shape, dtype="uint8")
        cv2.drawContours(mask, [cnts[i]], -1, 255, -1)
        mask = cv2.bitwise_and(thresh, thresh, mask=mask)
        digit = mask[y - 8:y + h + 8, x - 8:x + w + 8]
        digits.append(digit)
        i += 1

    return digits


def stack_digits(digits, resize_f):
    stacked = np.zeros([28, 28], dtype=np.uint8)
    for d in digits:
        if d.size == 0:
            continue
        d = resize_f(d)

        stacked = np.concatenate((stacked, d), axis=1)
    return stacked


def sort_contours(cnts, method="left-to-right"):
        # initialize the reverse flag and sort index
    reverse = False
    i = 0

    # handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True

    # handle if we are sorting against the y-coordinate rather than
    # the x-coordinate of the bounding box
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1

    # construct the list of bounding boxes and sort them from top to
    # bottom
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(
        *sorted(zip(cnts, boundingBoxes), key=lambda b: b[1][i], reverse=reverse))

    # return the list of sorted contours and bounding boxes
    return (cnts, boundingBoxes)
