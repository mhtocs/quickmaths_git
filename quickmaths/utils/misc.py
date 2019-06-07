import matplotlib.pyplot as plt
import cv2
import io
import numpy as np
from PIL import Image, ImageChops


class DotDict(dict):
    """dot.notation access to dictionary attributes"""

    def __getattr__(self, attr):
        return self.get(attr)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = self


def list_splice(target, start, delete_count=None, *items):
    """Remove existing elements and/or add new elements to a list.

    target        the target list (will be changed)
    start         index of starting position
    delete_count  number of items to remove (default: len(target) - start)
    *items        items to insert at start index

    Returns a new list of removed items (or an empty list)
    """
    if delete_count == None:
        delete_count = len(target) - start

    # store removed range in a separate list and replace with *items
    total = start + delete_count
    removed = target[start:total]
    target[start:total] = items

    return removed


def listsub(x, y):
    """Does set like substraction on x and y,
    Removes y from x, doesnt affect the original
    list

    x           list from which elements to be subtrated
    y           list to be subtracted


    Returns a new list x-y

    """
    return [item for item in x if item not in y]


def latex_to_img(tex):
    white = (255, 255, 255, 255)
    buf = io.BytesIO()
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.axis('off')
    plt.text(0.0, 0.0, f'${tex}$', size=30)
    plt.savefig(buf, format='png')
    plt.close()
    im = Image.open(buf)
    bg = Image.new(im.mode, im.size, white)
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    im = cv2.cvtColor(np.array(im.crop(bbox)), cv2.COLOR_RGB2BGR)
    return im
