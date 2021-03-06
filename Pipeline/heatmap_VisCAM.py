import matplotlib.pylab as plt

from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from keras.models import Model

from keras.preprocessing.image import img_to_array
from vis.utils import utils
from vis.utils.vggnet import VGG16
from keras.applications.vgg19 import VGG19
from keras.applications.resnet50 import ResNet50
from keras.applications.inception_v3 import InceptionV3
from keras.applications.xception import Xception
from keras.utils.np_utils import to_categorical
#from vis.visualization import visualize_cam
from visualization import visualize_cam # Local copy of visualize_cap.py that returns and separate heatmap and location of maximum
from skimage import io
from scipy.misc import imread, imresize

from imgloader import load_single_img

import cv2
import numpy as np
import os
import time

from VisCAM_NNparams import synset_to_dfs_ids
#from VisCAM_NNparams import detect_configuration


class Heatmap:

    def __init__(self):
        # Build the VGG19 network with ImageNet weights
        self.model = VGG16(weights='imagenet', include_top=True)
        #model = VGG19(weights='imagenet', include_top=True)
        #model = ResNet50(weights='imagenet', include_top=True)
        #model = InceptionV3(weights='imagenet', include_top=True)
        #model = Xception(weights='imagenet', include_top=True)
        

        # The name of the layer we want to visualize
        # (see model definition in vggnet.py)
        layer_name = 'predictions' # VGG16, VGG19, InceptionV3
        #layer_name = 'fc1000' # ResNet50
        self.layer_idx = [idx for idx, layer in enumerate(self.model.layers) if layer.name == layer_name][0]

        #model_type, index = detect_configuration(model)
        #s = "n02512053"  # Imagenet code for "fish"
        #s = "n02545841"  # Imagenet code for "Opah fish"
        #s = "n02626762"  # Imagenet code for "tuna"
        s = "n02536864"  # Imagenet code for "silver salmon" = 391
        self.pred_class = synset_to_dfs_ids(s)
        s = "n01484850"  # Imagenet code for "white shark"
        self.pred_class += synset_to_dfs_ids(s)
        s = "n02514041"  # Imagenet code for "barracoute, snoek"
        self.pred_class += synset_to_dfs_ids(s)
        

    def heatmap(self, img):

        orig_size=img.shape
        target_size=(224,224) # VGG16, VGG19, ResNet50
        seed_img = cv2.resize(img, (target_size[1], target_size[0]))

        seed_array = np.array([img_to_array(seed_img)])

        probs = self.model.predict(seed_array)
        prob_fish = probs[0,self.pred_class]
        heatmap_overlay, heatmap, max_idx = visualize_cam(self.model, self.layer_idx, self.pred_class, seed_img, text=utils.get_imagenet_label(self.pred_class))

        heatmap_overlay_orig = cv2.resize(heatmap_overlay, (orig_size[1], orig_size[0]))
        heatmap_orig = cv2.resize(heatmap, (orig_size[1], orig_size[0]))
        max_orig=np.floor(max_idx[0]*orig_size[0]/target_size[0]), np.floor(max_idx[1]*orig_size[1]/target_size[1])


        return heatmap_orig, max_orig, prob_fish
