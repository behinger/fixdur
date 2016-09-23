# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 17:11:54 2015

@author: jwu
"""
"""
extract features from sinlge bubbles (154 x 154, grey bg), images shown during
the experiment (1-5 bubbles on grey bg), original grey scale images where
the non bubble regions are cut out afterwards and a gaussian mask applied to 
the bubble regions
"""
"""
call all_images(n) to compute all plots for the row n in the data, e.g. n=149
"""

from pandas import DataFrame
import pickle
import cv
import PIL
import numpy as np
import matplotlib.pyplot as plt
from bifl import my_features as features
from mpl_toolkits.axes_grid1 import make_axes_locatable
import img_reconstruction as irec

home = '/net/store/nbp/users/jwu/fixdur/analysis/'

import os
if not os.path.isdir(home):
    home = 'C:/Users/01/fixdur/analysis/'

def get_data():    
    """ try to load the already generated dataframe
        if failed, generate the data frame """

    path_to_all_res = home + 'all_res.p'
    path_to_my_data = home + 'saliency/all_bubbles_with_path.p'    

    try: 
        all_bubbles = DataFrame(pickle.load(open(path_to_my_data, 'rb')))
        #print "all_bubbles_with_path.p loaded from my dataframe"
    except:
        all_bubbles = create_dataFrame(path_to_all_res)
        generate_path(all_bubbles)      
        print "data imported from 'all_res', path generated"
        all_bubbles.to_pickle(path_to_my_data)
        print "dataframe saved"

    return all_bubbles
 
   
def create_dataFrame(path_to_all_res):
    """ return a dataframe with all relevant information only """    
    all_res = pickle.load(open(path_to_all_res, 'rb'))
    panda_all_res = DataFrame(all_res)
    all_bubbles = panda_all_res.loc[:,['dispX','dispY','image']]
    return all_bubbles


def generate_path(all_bubbles):
    """ for each single bubble generate the according path for further access
        return the dataframe completed with the column 'path' """    
    path = []
    for i in all_bubbles.index:
        path_sub = []
        for k in range(len(all_bubbles.loc[i, 'dispX'])):
            x = int(all_bubbles.loc[i,'dispX'][k])-77-320
            y = int(all_bubbles.loc[i,'dispY'][k])-77-60  
            # update dispX and dispY            
            all_bubbles.loc[i,'dispX'][k] = x
            all_bubbles.loc[i,'dispY'][k] = y
            path_sub.append("/net/store/nbp/projects/fixdur/stimuli/single_bubble_images/" + \
                            str(all_bubbles.loc[i,'image']) + "/" + \
                            "bubble_" + str(x) + "_" + str(y) + ".tiff")
        path.append(path_sub)
    all_bubbles['path'] = path
    return all_bubbles
    

if 'all_bubbles' not in locals():
    all_bubbles = get_data()


#------------------------------------------------------------------------------

def all_images(n=149):    
    """ return for a given row in the dataframe plots for all 3 methods """    
    one_row = all_bubbles.loc[n]
    bIdx = 0 # bubble index
    
    """ single bubble """
    f_single = extract('single bubble', one_row['path'][0])
    dump = plot_all(f_single,'')
    dump[1].suptitle('Method 1')
    dump[1].savefig(home + 'saliency/figures/method1.svg')
    
    """ image shown in the experiment """
    f_expimg = extract('exp img', n) 
    dump = plot_all(f_expimg,'')
    dump[1].suptitle('Method 2')
    dump[1].savefig(home + 'saliency/figures/method2.svg')
    
    """ full image with a mask applied afterwards """
    f_fullimg = extract_full_img(one_row)
    dump = plot_all(f_fullimg,'')
    dump[1].suptitle('Method 3')
    dump[1].savefig(home + 'saliency/figures/method3.svg')

        
    """ plot with 3 methonds together """
    f = [f_single[0], f_expimg[0], f_fullimg[0]]    
    [axes, f] = plot_all(f,'all method')
    
    positions = zip(one_row['dispX'], one_row['dispY'])
    for i in [1,2]:
        for ax in axes[i]:
            ax.set_xlim(positions[bIdx][0],positions[bIdx][0]+154)
            ax.set_ylim(positions[bIdx][1]+154,positions[bIdx][1]) 
    f.savefig(home + 'saliency/figures/methodAll.svg')
                   
def extract(description, arg):
    """ calls the features.extract() function and 
        returns a list containing all feature mats on all 3 levels 
        i.e. [{'feature': feature mat},{},{}]
        applyable for methods: single bubbles, bubbled grey background """    
    if description == 'single bubble':
        img = prepare_bubble(arg)
    elif description == 'exp img':
        img = irec.display_bubbles(all_bubbles, arg)[0]
    img = del_alpha(img)
    #plt.figure()    
    #plt.imshow(img) 
    #plt.axis('off')
    img = array2ipl(img)
       
    img_features = features.extract(img)
    return img_features


def prepare_bubble(path):
    """ load the bubble image as numpy array and set the bg to grey """    
    img = load_ipl_as_array(path)
    img = gray_bg(img)
    return img

    
def load_ipl_as_array(path):
    """ load a .tiff image as numpy array for further processing """    
    img = PIL.Image.open(path).convert('RGBA')
    img = np.array(img)
    return img

    
def gray_bg(img):
    """ set the transparent part of the bubble image to grey """    
    for i in range(len(img)):
        for k in range(len(img[i])):
            if img[i][k][3] == 0:
                img[i][k] = [128, 128, 128, 255]
    return img

    
def del_alpha(img):
    """ delete the alpha channel of a img (numpy array)  
        for some reason features.extract() works only for 3 channel images """    
    img = img[:,:,0:3].copy()
    return img

    
def array2ipl(img):
    """ convert a ndarray image to ipl as
        features.extract*() works only for ipl format """    
    img_new = cv.CreateImageHeader((img.shape[1], img.shape[0]), cv.IPL_DEPTH_8U, 3)
    cv.SetData(img_new, img.copy().data,img.dtype.itemsize*3*img.shape[1])
    img_new[50,75]
    return img_new
    

def extract_full_img(one_row):
    """ call features.extract() for the method: full_img and cut non-bubble-area
        apply the gaussian mask to the bubble regions
        fails for noise condition bcs prepare_full_img failes"""
    # differentiate between noise and urban images
    try:
        path = '/net/store/nbp/projects/fixdur/stimuli/urban/' + str(one_row['image'])
    except:
        path = '/net/store/nbp/projects/fixdur/stimuli/noise/post_shine/' + str(one_row['image'])
    img = prepare_full_img(path)
    img_features = features.extract(img)
    # generate a mask
    positions = zip(one_row['dispX'], one_row['dispY'])
    mask = make_mask(positions) 
    #mask_mat = cv.fromarray(mask)
    i = 0
    #ones = ones_mask(i)
    #inv_mask = np.logical_xor(mask, ones)
    #inv_mask = inv_mask * 128
    #plt.figure(), plt.imshow(inv_mask)
    #plt.colorbar()
    for key in img_features[i]:
        feat_mat = img_features[i][key]
        #plt.figure(), plt.imshow(feat_mat)
        feat_mat = feat_mat * mask
        #plt.figure(), plt.imshow(feat_mat)
        img_features[i][key] = feat_mat
    return img_features
  
  
def prepare_full_img(path):
    """ return a grey image as 3-dimensional np array """    
    img = PIL.Image.open(path).convert('L')
    img = np.array(img)
    image = np.zeros((960, 1280, 3), np.uint8) 
    for i in range(3):
        image[:,:,i] = img.copy()
    #plt.figure()
    #plt.imshow(image)
    #plt.axis('off')
    img = array2ipl(image)
    return img 
       

def make_mask(positions):
    """ create a mask where only the bubble regions have the value [0,1] and the rest value 0 """
    mask = np.zeros((960, 1280))
    mask_bubbles = bubble_mask()
    for x, y in positions:   
        mask[y:y+154, x:x+154] = mask_bubbles
    return mask

                
def bubble_mask():
    """ return a mask in bubble size with the Gaussian mask on top of it """
    
    def makeGaussian(size, fwhm, center=None):  # from Lili
        """ Make a square gaussian kernel.
     
        size is the length of a side of the square
        fwhm is full-width-half-maximum, which
        can be thought of as an effective radius.
        """ 
        x = np.arange(0, size, 1, float)
        y = x[:,np.newaxis]
        
        if center is None:
            x0 = y0 = size // 2
        else:
            x0 = center[0]
            y0 = center[1]
        
        return np.exp(-4*np.log(2) * ((x-x0)**2 + (y-y0)**2) / fwhm**2)

    bubble_mask = makeGaussian(154,77)
    return bubble_mask


#def ones_mask(level):
#    """ make a mask containing only 1 """    
#    mask = np.ones((960 / (2**level), 1280 / (2**level)), np.uint8)
#    return mask

            
def plot_all(img_features, label):    
    """ plot 3x9, levels x features for a given list of feature mats """
    feat_list = img_features[0].keys()
    feat_list.sort()
    f, axes = plt.subplots(nrows=3, ncols=len(feat_list))  
    #f.set_size_inches(8,15)
    for level in range(3):    
        for ax, feature in zip(axes[level],feat_list):            
            im = ax.imshow(img_features[level][feature]) # set vmin, vmax individually
            #ax.axis('off')
            #ax.tick_params(axis='both', left='off', bottom='off')
            ax.set_xticks([])
            ax.set_yticks([])            
            im.set_cmap('YlGnBu')            
            #im.set_cmap('viridis')
            div = make_axes_locatable(ax)
            cax = div.append_axes("bottom", size="10%", pad=0.3)
            plt.colorbar(im, cax=cax, format="%.1g", orientation='horizontal')
    # label rows and colums
    if label == '':
        labels = ['level 0', 'level 1', 'level 2']
    else:
        labels = ['Method 1', 'Method 2', 'Method 3']
    
    for ax, feature in zip(axes[0], feat_list):
        ax.set_title(feature)
    for ax, level in zip(axes[:, 0], labels):
        ax.set_ylabel(level)
    
    
    return(axes,f)
    
def plot_one(img_features, feature):    
    f, axes = plt.subplots(nrows=3, ncols=1)  
    #f.set_size_inches(8,15)
    for level in range(3):             
        im = axes[level].imshow(img_features[level][feature]) # set vmin, vmax individually
        im.set_cmap('YlGnBu')
        #im.set_cmap('viridis')
        div = make_axes_locatable(axes[level])
        cax = div.append_axes("bottom", size="10%", pad=0.3)
        plt.colorbar(im, cax=cax, format="%.1g", orientation='horizontal')
    # label rows and colums

    labels = ['level 0', 'level 1', 'level 2']

    for level in range(3):
        axes[level].set_ylabel(labels[level])
    return(axes,f)
    
#n = 149    
#f_expimg = extract('exp img', n) 
#plot_one(f_expimg, 'lumc')

#------------------------------------------------------------------------------

"""
with the following functions we can test different window size for the feature 
extraction function 'contrast'
"""
def get_means(c, positions):
    """ get the mean contrast value of the bubble at x,y position """
    means = []
    for x,y in positions:        
        bubble = c[y:y+154, x:x+154]
        mean = np.asarray(bubble).mean()
        means.append(mean)
    return means

    
def test_ws(window_sizes): # let ws be a list
    from bifl.cpy import colorsplit as cs
    import random
    # get the image and compute the feature map
    n = 149
    img = irec.display_bubbles(all_bubbles, n)[0]
    img = del_alpha(img)
    img = array2ipl(img)
    img = cs(img)
    img = img[0]
    means_list = []
    for ws in window_sizes:    
        means = get_lumc(img, n, ws)        
        means_list.append(means)
    # plot means sorted by ws    
#    xAxis = [[1,2,3,4,5] for i in range(len(window_sizes))]
#    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'black']
    plt.figure()
    for means in means_list:
        plt.plot([1,2,3,4,5],means,'-o')
    plt.legend(window_sizes)
    #plt.axis([0,6,0,0.2])
    plt.xlabel('bubble number')
    plt.ylabel('mean of contrast')
    plt.title('mean of contrast using different window size')
        
def get_lumc(img, n, ws):        
    from bifl.mods import contrast    
    c = contrast(img, ws=ws)   
#    plt.figure()
#    im = plt.imshow(c)
#    im.set_cmap('YlGnBu')
#    plt.colorbar(im, format="%.1g", orientation='horizontal')
      
    # calculate the mean of each bubble region 
    means = get_means(c, zip(all_bubbles.loc[n,'dispX'], all_bubbles.loc[n,'dispY']))
    print means
#    plt.figure()
#    plt.plot([1,2,3,4,5], means, 'ro')
#    plt.axis([0,6,0,0.2])
    return means
    
#------------------------------------------------------------------------------
# added on 23.5.16 
 
def extract_all_methods(n=149):
    one_row = all_bubbles.loc[n]
    f_single = extract('single bubble', one_row['path'][0])
    f_expimg = extract('exp img', n) 
    f_fullimg = extract_full_img(one_row)
    return f_single, f_expimg, f_fullimg
    
def one_feature(img_features):    
    f, axes = plt.subplots(nrows=3, ncols=1)  
    for level in range(3):             
        im = axes[level].imshow(img_features[level]) # set vmin, vmax individually
        im.set_cmap('YlGnBu')
        #im.set_cmap('viridis')
        div = make_axes_locatable(axes[level])
        cax = div.append_axes("bottom", size="10%", pad=0.3)
        plt.colorbar(im, cax=cax, format="%.1g", orientation='horizontal')
    # label rows and colums
    return(axes,f)
    
def feature_across_methods(feature):
    f_single, f_expimg, f_fullimg = extract_all_methods()

    fmaps = [f_single[0][feature], f_expimg[0][feature], f_fullimg[0][feature]]    
    [axes, f] = one_feature(fmaps)
    
    positions = zip(one_row['dispX'], one_row['dispY'])
    for i in [1,2]:
        for ax in axes[i]:
            ax.set_xlim(positions[bIdx][0],positions[bIdx][0]+154)
            ax.set_ylim(positions[bIdx][1]+154,positions[bIdx][1]) 