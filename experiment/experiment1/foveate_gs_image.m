function foveate_gs_image(elem)
% FOVEATE_GS_IMAGE   Realtime foveation of a static, grayscale image
%
% Press ESC to end the demo and close the window.

% Copyright (C) 2004-2006
% Center for Perceptual Systems
% University of Texas at Austin
%
% jsp Wed Sep 20 17:24:30 CDT 2006
addpath('~/lib/matlab/svistoolbox-1.0.5');
load 'img_coordinates.mat';
load 'current_image.mat';

%set parameter
halfres = 2.3;
%image covers about 25degree horizontally -> horizontal map has to be twice as big
maparc = 50;

% Read in the file
img = imread(elem);
if size(img,3) == 3
    img = rgb2gray(img);
    %warning('picture converted from RGB to gray')
end
rows=size(img,1);
cols=size(img,2);

% Initialize the library
svisinit

% Create a resmap
%fprintf('Creating resolution map...\n');
resmap=svisresmap(rows*2,cols*2,'halfres',halfres,'maparc',maparc);

% Create 3 codecs for r, g, and b
%fprintf('Creating codec...\n');
c=sviscodec(img);

% The masks get created when you set the map
%fprintf('Creating blending masks...\n');
svissetresmap(c,resmap);

for a=1:length(sample_points)
    
    x = sample_points(a,1);
    y = sample_points(a,2);
    
    % Encode
    img=svisencode(c,rows-y,x);

    %save image
    filename = ['img1_',num2str(x),'_',num2str(y)];
    imwrite(img, ['fovia_filtered_images/' filename '.tiff']);
    
end

% Free resources
svisrelease
exit
end
