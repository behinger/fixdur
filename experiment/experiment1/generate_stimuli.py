import numpy as np
import random
import sys
import scipy
import scipy.io
import os

import tools

from PIL import Image
import PIL.ImageOps
import PIL.ImageDraw

#stuff for uniform poisson
sys.path.append('poisson_disk_python/src')
from poisson_disk import *
from enhanced_grid import *

#set approximate bubble_size radius in visual degree (actual size in mat)
bubble_size = 1.1774

path_to_images = '/net/store/nbp/fixdur/stimuli/'
#path_to_images = '../stimuli/'

 
def makeGaussian(size, fwhm, center=None):
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
    


'''
def get_1_bubble_on_image(image,mat,x_location,y_location):
    """ Set mat on given location (upper left corner) in image
    Return image """

    # create empty mask
    mask = np.zeros((image.size[0],image.size[1]))

    # fill mask with gaussian
    mask[x_location:(x_location+mat.shape[0]),y_location:(y_location+mat.shape[1])] = mat
    # convert mask array to image
    mask_image = Image.fromarray(mask)
    # for some reason Image.fromarray seems to rotate the image, therfore rotate it back
    mask_image = mask_image.rotate(90)
    mask_image = mask_image.convert('L')
    
    # paste mask on image
    masked_image = Image.new('L',(image.size[0],image.size[1]))
    masked_image.paste(image,(0,0))

    # inverse mask for gray background
    inv_mask = PIL.ImageOps.invert(mask_image)
    # paste background masked by inverse mask on the masked image
    masked_image.paste('gray',(0,0),inv_mask)
        
    return masked_image
    
'''


def get_1_bubble_on_image(image,mat,x_location,y_location):
    """ Set mat on given location (upper left corner) in image
    Return bubble """

    # get image array from rotated image since getting the array will rotate it again
    image_array = np.array(image.rotate(-90))
    image_array = image_array[x_location:(x_location+mat.shape[0]),y_location:(y_location+mat.shape[1])]
    #image_array = image_array[int(point[0]):(int(point[0])+mat.shape[0]),int(point[1]):(int(point[1])+mat.shape[1])]
    image = Image.fromarray(image_array)
    # convert mask array to image
    mask_image = Image.fromarray(mat)
    # for some reason Image.fromarray seems to rotate the image, therfore rotate it back
    image = image.rotate(90)
    mask_image = mask_image.convert('L')
    
    # paste mask on image
    masked_image = Image.new('L',(mat.shape[0],mat.shape[1]))
    masked_image.paste(image,(0,0))

    # inverse mask for gray background
    #l,a = mask_image.split()
    #inverted_image = PIL.ImageOps.invert(l)
    #r, g, b = map(invert, (r, g, b))
    #final_transparent_image = Image.merge(mask_image.mode, (r, g, b, a))  
    #final_transparent_image = Image.merge('LA', (l,a))
    #inv_mask = final_transparent_image
    inv_mask = PIL.ImageOps.invert(mask_image)
    # paste background masked by inverse mask on the masked image
    masked_image.paste('gray',(0,0),inv_mask)
    #masked_image = alpha_composite(masked_image, inv_mask)    
    return masked_image

# set parameters for gaussian
size = round(tools.deg_2_px(bubble_size))*3
fwhm = round(tools.deg_2_px(bubble_size))
# create gaussian and normalize to pixel color
mat = makeGaussian(size, fwhm) * 255

# adjust mat size
# find idex of first item in center array of mat that is bigger 0.01(*255)
items_bigger_zero = np.where(mat[(size/2),:]>0.01*255)[0]
# items_bigger_zero[0] gives first instance
# substract index from both sites of size
size = size - (2*items_bigger_zero[0])
# recalculate mat
mat = makeGaussian(size, fwhm) * 255

#load list of images
#all_images = os.listdir(path_to_images+'urban/')
all_images = os.listdir(path_to_images+'noise/post_shine/')

for elem in all_images:

    # load image
    #image = Image.open(path_to_images+'urban/'+elem)
    image = Image.open(path_to_images+'noise/post_shine/'+elem)
    image = image.convert('LA')

    # uniform poisson stuff
    # set parameter (substract margin to make sure there is enough space for bubbles
    w = int(image.size[0] - size)
    h = int(image.size[1] - size)
    min_radius = 35
    max_radius = 100
    # generate sample points
    p = sample_poisson_uniform(w, h, 77, 30)
    # add margin (without sample points) to width and hight
    sample_points = np.empty((len(p),2))
    for a in range(len(p)):
        # add 1/2 size to get empty margin & substract 1/2 size to get corner coordinates instead of center
        sample_points[a][0] = int(p[a][0])
        sample_points[a][1] = int(p[a][1])

    # save sample points and current image for matlab
    # add 1/2 size to get center coordinates instead of upper left corner
    sample_points_mat = sample_points + int(size/2)
    scipy.io.savemat('img_coordinates.mat', mdict={'sample_points': sample_points_mat})
    #scipy.io.savemat('current_image.mat', mdict={'elem': path_to_images+'/urban/'+elem})
    scipy.io.savemat('current_image.mat', mdict={'elem': path_to_images+'/noise/post_shine/'+elem})

    # excecute matlab script to set fovia filter
    if not os.path.exists('fovia_filtered_images'):
        os.system('mkdir fovia_filtered_images')
    os.system('matlab -nodisplay -r foveate_gs_image')
    #os.system('/home/lkaufhol/MATLAB/R2012a/bin/matlab -nodisplay -r foveate_gs_image')

    # generate bubble image for each sample point
    for point in sample_points:
        filepath = 'fovia_filtered_images/img1_'+str(int(point[0]+(size/2)))+'_'+str(int(point[1]+(size/2)))+'.tiff'
        image = Image.open(filepath)
        masked_image = get_1_bubble_on_image(image,mat,int(point[0]),int(point[1]))
        # y-coordinate is lower edge in inverted coordinate system -> set to upper edge
        y = image.size[1] - mat.shape[1] - int(point[1])
        #set outer circle transparent
        bubble_image = masked_image.convert('RGBA')
        r,g,b,a = bubble_image.split()
        draw = PIL.ImageDraw.Draw(a)
        draw.rectangle((0,0,bubble_image.size[0],bubble_image.size[0]),fill=0)
        draw.ellipse((0,0,bubble_image.size[0],bubble_image.size[0]),fill=255)
        trans_image = Image.merge('RGBA', (r,g,b,a))
        # save single bubble images, store location of upper left corner in name
        #if not os.path.exists(path_to_images+'single_bubble_images/'+str(elem)):
        #    os.system('mkdir ./'+path_to_images+'single_bubble_images/'+str(elem))
        #trans_image.save(path_to_images+'single_bubble_images/'+str(elem)+'/bubble_'+str(int(point[0]))+'_'+str(y)+'.tiff','tiff')
        #if not os.path.exists(path_to_images+'noise_single_bubble_images/'+str(elem)):
        os.system('mkdir '+path_to_images+'noise_single_bubble_images/'+str(elem))
        trans_image.save(path_to_images+'noise_single_bubble_images/'+str(elem)+'/bubble_'+str(int(point[0]))+'_'+str(y)+'.tiff','tiff')
         
         

    # delete stuff
    os.system('rm -r fovia_filtered_images')
    os.system('rm current_image.mat')    
    os.system('rm img_coordinates.mat')
