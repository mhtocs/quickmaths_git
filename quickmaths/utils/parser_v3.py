# parser using prebuilt binary from DRACULAE
# this will be used untill parser_v2 is completed
import shlex
import re
import numpy as np
from subprocess import Popen, PIPE
from sympy.parsing.latex import *
from sympy import Basic, preview, pprint, sympify
from keras.models import load_model
import traceback
from quickmaths.utils.misc import latex_to_img
import cv2
import io
import os
from quickmaths.utils.parser import BSTNode

# disable tf warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

dictionary = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', 'x', '-', '(', ')', 'sqrt']


class Symbol:
    def __init__(self, label, x_min, y_min, x_max, y_max):
        self.label = label
        self.min_x = x_min
        self.min_y = y_min
        self.max_x = x_max
        self.max_y = y_max
        self.width = self.max_x - self.min_x
        self.height = self.max_y - self.min_y
        if 'sqrt' in label:
            label = '√'

    def __str__(self):
        return self.label


class Predictor:

    def __init__(self, model_path="", root_dir=""):
        print("loading model...")
        self.ROOT_DIR = root_dir
        print(f"root_dir is: {self.ROOT_DIR}")
        self.model = load_model(model_path)
        self.prev_res = None
        self.prev_label_list = None
        self.latex_img = np.zeros([123, 359], dtype=np.uint8) + 255
        self.none_img = np.zeros([123, 359], dtype=np.uint8) + 255
        self.res = "None"

    def get_exitcode_stdout_stderr(self, cmd, input_):
        """
        Execute the external command and get its exitcode, stdout and stderr.
        """
        args = shlex.split(cmd)

        proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        output, err = proc.communicate(input=input_)
        exitcode = proc.returncode
        #
        return exitcode, output, err

    def parse(self, symbols, boxes):
        string = ""
        processed_labels = []
        try:

            labels = self.model.predict_classes(symbols.reshape(-1, 28, 28, 1))
            string += f"Number of Symbols: {len(symbols)}\n"
            label_list = ""  # a string consisting all labels
            for label, (pre_label, x_min, y_min, x_max, y_max) in zip(labels, boxes):
                label = dictionary[int(label)]
                # if pre_label exists use it instead
                if pre_label:
                    label = pre_label
                processed_labels.append(label)
                string += (f'{label}     <{x_min,y_min},{x_max,y_max}>\n')
                label_list += label
            # print(string)

            if label_list != self.prev_label_list:
                # print("String not matched, recalculating!")

                self.prev_label_list = label_list
                cmd = f"/home/kayshu/documents/bin/GetTeX.x  /dev/stdin "  # arbitrary external command, e.g. "python mytest.py"
                exitcode, output, err = self.get_exitcode_stdout_stderr(cmd, f"{string}")

                # find the text inside the two dollar signs in text
                output = re.findall('\$(.*?)\$', output, re.DOTALL)

                # if list is not empty
                if [] != output:
                    output = output[0]
                    output = output.replace('\n', '')
                    output = output.replace(' ', '')
                    output = output.replace('\\limits', '')
                    output = output.replace('overline', '')
                    print(f'latex is: {output}')

                    # generate image

                    try:
                        buf = io.BytesIO()
                        preview(f"${output}$", viewer='BytesIO', outputbuffer=buf, euler=False)
                        buf.seek(0)
                        img_bytes = np.asarray(bytearray(buf.read()), dtype=np.uint8)
                        self.latex_img = cv2.imdecode(img_bytes, 0)
                    except Exception as e:
                        print('Error in preview,using previous image')

                    # parse latex result using sympy.parser
                    self.res = sympify(parse_latex(output))
                    pprint(self.res, use_unicode=True)

                    # if isinstance(res, Basic):
                    self.res = round(float(self.res.n()), 2)

            # show the result on console
            return f"Result: {self.res}", self.latex_img, processed_labels
        except Exception as e:
            print(traceback.format_exc())
            return f"Result: {self.res}", self.none_img, processed_labels

    def parsev2(self, symbols, boxes):
        try:
            tree = BSTNode()
            labels = self.model.predict_classes(symbols.reshape(-1, 28, 28, 1))
            for label, (pre_label, x_min, y_min, x_max, y_max) in zip(labels, boxes):
                label = dictionary[int(label)]
                # if pre_label exists use it instead
                if pre_label:
                    label = pre_label
                tree.insert(BSTNode(Symbol(label, x_min, y_min, x_max, y_max)))
            return str(tree)
        except Exception as e:
            print(e)
            return str(e)
