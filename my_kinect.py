#!/usr/bin/env python
import freenect
import sys
import cv
import cv2
import frame_convert
import numpy as np


threshold = 100
current_depth = 0
depth_image = 0;

# windows and their initial states
depth_window = 0;
threshold_window = 0;

# OPENCV GUI callbacks
def toggle_depth_window(value):
    global depth_window
    
    #window is opened and has to be closed
    if depth_window == 1 and value == 0:
        cv.DestroyWindow('Depth')
        depth_window = 0
    elif depth_window == 0 and value == 1:
        cv.NamedWindow('Depth')
        depth_window = 1
    
def toggle_threshold_window(value):
    global threshold_window
    
    #window is opened and has to be closed
    if threshold_window == 1 and value == 0:
        cv.DestroyWindow('Threshold')
        threshold_window = 0
    elif threshold_window == 0 and value == 1:
        cv.NamedWindow('Threshold')
        cv.CreateTrackbar('threshold', 'Threshold', threshold,     500,  change_threshold)
        cv.CreateTrackbar('depth',     'Threshold', current_depth, 2048, change_depth)
        threshold_window = 1

def change_threshold(value):
    global threshold
    threshold = value
#    print 'threshold changed to: {0}'.format(threshold)

def change_depth(value):
    global current_depth
    current_depth = value
#    print 'depth changed to: {0}'.format(current_depth)








# window content rendering section
def show_depth():
    global depth_image
    
    depth, timestamp = freenect.sync_get_depth()
    depth_image =  frame_convert.pretty_depth_cv(depth);
    cv.ShowImage('Depth', depth_image) 

def show_video():
    cv.ShowImage('Video', frame_convert.video_cv(freenect.sync_get_video()[0]))


def show_threshold():
    global threshold
    global current_depth

    depth, timestamp = freenect.sync_get_depth()
    depth = 255 * np.logical_and(depth >= current_depth - threshold,
                                 depth <= current_depth + threshold)
    depth = depth.astype(np.uint8)
    threshold_image = cv.CreateImageHeader((depth.shape[1], depth.shape[0]),
                                 cv.IPL_DEPTH_8U,
                                 1)
    cv.SetData(threshold_image, depth.tostring(),
              depth.dtype.itemsize * depth.shape[1])
    cv.ShowImage('Threshold', threshold_image)





# parse command line arguments
arguments = sys.argv

if '-h' in arguments or '--help' in arguments:
    #print help/welcome message to command line
    print """
MyKinect v0.0.1 
---------------
Usage:
sudo python my_kinect.py [-h --help -d -t]

-h, --help - display this message
-d - display depth window at start
-t - display threshold window at start

Controls:

- ESC in window to close 
- "s" key to save RGB image to RGB.jpg in current directory
- "d" key to save DEPTH image to DEPTH.jpg in current directory."""

if '-d' in arguments:
    toggle_depth_window(1)
if '-t' in arguments:
    toggle_threshold_window(1)

# open initial window with controls to open additional windows - opencv doesnt have buttons, so we use trackbars
cv.NamedWindow('Video')
cv.CreateTrackbar('Depth Window', 'Video', depth_window, 1, toggle_depth_window)
cv.CreateTrackbar('Threshold Window', 'Video', threshold_window, 1, toggle_threshold_window)

 

# main program loop
while 1:
    if depth_window:
        show_depth()
    
    if threshold_window:
        show_threshold();
    
    show_video()
    
    key = cv.WaitKey(5) & 0xFF
    if key == 27:
        break;
    elif key == 115:
		print '"s" key pressed, saving RGB image to file RGB.jpg'
		cv2.imwrite('RGB.jpg', freenect.sync_get_video()[0]);
    elif key == 100 and depth_window:
        print '"d" key pressed, saving depth image to file DEPTH.jpg'
        cv.SaveImage('DEPTH.jpg', depth_image)
