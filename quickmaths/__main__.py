from quickmaths.app import App
import logging
import argparse
import os
# set up logging to file
logging.basicConfig(
    filename='quickmaths.log',
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d}\
     %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)


# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,
                help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
                help="Whether or not frames should be displayed")
ap.add_argument("-c", "--camera", type=int, default=1,
                help="Which camera to use")

args = vars(ap.parse_args())

if args["camera"] == 0:
    args["camera"] = "http://10.42.0.83:8080/video"
app = App(logger, args["camera"], ROOT_DIR)
app.run()
