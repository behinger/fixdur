"""
Extract feature batteries from gauss pyramids
"""

import cv
from utils import saveIm
from mods import *
from cpy import *


def stage(lum,):
    lumc = contrast(lum) # local contrast
    lumt = contrast(lumc, 251) # texture contrast
    sob = sobel(lum)
    sobs = smooth(sob)
    lums = smooth(lum) # Gaussian filter
    id0, id1, id2 = intdim(lum)
    idX = add(zscale(id0), zscale(id2))
    return dict(lumc=lumc, lumt=lumt, sobs=sobs, lums=lums, id0=id0, id1=id1, id2=id2, idX=idX,sob=sob)


def pyramid(lsrb, count=3):
    """
    run stage in a downwards pyramid for ``count`` times,
    scale each map with ``scaler``,
    return list with one dict per pyramid level
    """
    features = [stage(lsrb)]
    if count == 1:
        return features
    lsrb = pyrdown(lsrb)
    features += pyramid(lsrb, count - 1)
    return features


def extract(image, pyr_levels=3):
    """extract features from ``image``"""
    lsrb = colorsplit(image)
    return pyramid(lsrb[0], pyr_levels)