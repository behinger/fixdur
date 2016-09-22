import numpy as np
import os, math
import tools_gist as tools

#paths
path_to_fixdur_files, path_to_fixdur_code = tools.paths()

MAT = 154

'''check if minimal needed distance between new point and old points is given'''
def get_distance(point_a,point_b):
    distance = math.sqrt((((point_a[0])-(point_b[0]))**2) + (((point_a[1])-(point_b[1]))**2))    
    return distance
    
all_images = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/') 
training = os.listdir(path_to_fixdur_files+'stimuli/training/single_bubbles/')
for image in training:
    all_images.append(image)

for image in all_images: 
    #store bubble_locations
    bubble_locations = []
    
    #load bubbles
    if ((image == 'image_28.bmp') or (image == 'noise_train_shine.bmp')):     
        all_bubbles = os.listdir(path_to_fixdur_files+'stimuli/training/single_bubbles/'+image)
    else:  
        all_bubbles = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/'+image)
    for bubble in all_bubbles:
        #get location of bubble from file name
        bubble_location = [int(bubble.split('_',1)[1].split('_')[0])+(MAT/2),int(bubble.split('_',1)[1].split('_')[1].split('.')[0])+(MAT/2)]
        bubble_locations.append(bubble_location)
    #create matrix to store distances
    distance_mat = np.empty(shape=(len(all_bubbles),len(all_bubbles)))
    for a in range(len(bubble_locations)):
        for b in range(len(bubble_locations)):
            distance_mat[a][b] = get_distance(bubble_locations[a],bubble_locations[b])
                
    #np.save(path_to_fixdur_files+'distances/'+str(image)+'.npy',distance_mat)
    np.save(path_to_fixdur_code+'distances/'+str(image),distance_mat)


''' create matrix containing all bubbles with information of source image'''
images = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/')
np.random.shuffle(images)    
    
image = []
bubble = []    
    
for img in images:
    all_bubbles = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/' + img)
    for bb in all_bubbles:
        bubble = np.append(bubble,bb)
        image = np.append(image,img)

image = np.reshape(image,(len(image),1))
bubble = np.reshape(bubble,(len(bubble),1))        
bubble_mat = np.append(image,bubble,axis=1)

np.save('all_bubble_mat',bubble_mat)
