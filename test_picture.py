#!/usr/bin/env python

######################################################################
# import the necessary modules
import sys,os,time
import freenect
import cv2
import numpy as np
from random import randint 
import subprocess 
import serial

######################################################################

threshold     = 100
current_depth = 650
adj           = 8
zoomy         = 1.1
zoomx         = 1.13
state       = "idel"
rectxy = [ [randint(2,102), randint(2,302)],
           [randint(202,302),randint(2,302)],
           [randint(402,502),randint(2,302)] ]
rectw       = 65
recth       = 80
resetxy = [50,50]
resetwh = [90,90]
photoxy = [0,0]
photowh = [640,480]
ximgxy =  [resetxy[0]+7,resetxy[1]-17]
#ximgxy =  [resetxy[0]+7,resetxy[1]-7]
number_rect = 0
check_rect  = rectw*recth*2/5
sum_boolean = 0
count_down  = 5
start_time  = 0
image       = None
hand_img = cv2.resize(cv2.imread("hand.png",-1),(0,0), fx=0.4, fy=0.5)
photo_img = cv2.imread("camera.png",-1)
photo_img = cv2.resize(photo_img,(0,0), fx=0.3, fy=0.3)
x_img = cv2.imread("x.png",-1)
#x_img = v2.resize(cv2.imread("back.png",-1),(0,0), fx=0.6, fy=0.8)

ver = (cv2.__version__).split('.')
cap = cv2.VideoCapture(0)         # open /dev/video0


# open serial port 
ser_portname = '/dev/ttyACM0'
ser = serial.Serial(
    port=ser_portname,
    baudrate=115200,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)

def random_number():
    global rectxy 
    start = 2
    end = int(580/len(rectxy))
    for row in range(len(rectxy)):
        rectxy[row][0] = randint(start,end)
        rectxy[row][1] = randint(2,302)
        start = end
        end = start +int(580/len(rectxy))

#function to get RGB image from kinect
def get_video():
    array,_ = freenect.sync_get_video()
    array = cv2.cvtColor(array,cv2.COLOR_RGB2BGR)
    return array
 
#function to get depth image from kinect
def get_depth():
    array,_ = freenect.sync_get_depth()
    #array = array.astype(np.uint8)
    return array

def rgb_change_size():
    #resize and crop
    frame = get_video()
    frame=cv2.flip(frame,1)
    big_frame = cv2.resize(frame,(0,0), fx=zoomx, fy=zoomy)
    crop_frame = big_frame[480*(zoomx-1)/2:480+480*(zoomx-1)/2,640*(zoomy-1)/2:640+640*(zoomy-1)/2]
    return crop_frame

def adject_depth():
    depth = get_depth()
    depth=cv2.flip(depth,1)
    depth = 255 * np.logical_and(depth >= current_depth - threshold, depth <= current_depth + threshold)    
    depth = depth.astype(np.uint8)
    blurred = cv2.GaussianBlur(depth, (5, 5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    return thresh

def draw_contours(frame,depth):
    #( cnts, _) = cv2.findContours(depth.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    (_, cnts, _) = cv2.findContours(depth.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours( frame, cnts, -1, (255,0,255), 5 )
    return frame

#count white area
def check_boolean(thresh,rectx,recty,rectw,recth):
    boolean = np.equal(thresh[recty:(recty+recth),rectx:(rectx+rectw)],255)
    return np.sum(boolean)

# insert small image in big image
def insert_img(frame,s_img,x_offset,y_offset):
    for c in range(0,3):
        frame[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1], c] =  s_img[:,:,c] * (s_img[:,:,3]/255.0) +  frame[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1], c] * (1.0 - s_img[:,:,3]/255.0)
    return frame

def state_pic(frame,depth):
    global count_down
    global number_rect
    global start_time
    global state
    global rectxy
    rectx = rectxy[number_rect][0]
    recty = rectxy[number_rect][1]
    if(state == "idel"):
        # picture in idel
        frame = insert_img(frame,photo_img,photoxy[0],photoxy[1])
        sum_boolean =  check_boolean(depth,photoxy[0],photoxy[1],photowh[0],photoxy[1])
        if(sum_boolean > check_rect):
            state = "shuter"
            start_time = time.time()
    elif(state == "shuter"):
        #picture hand when no touch
        cv2.rectangle(frame,(rectx,recty),(rectx+rectw,recty+recth),(0,0,255),3)
        frame = insert_img(frame,hand_img,rectx+5,recty+10)
        #number hand
        cv2.putText(frame,str(number_rect+1), (rectx+25,recty+recth-15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),3)
        state = shuter(depth)
    elif(state == "check_touch"):
        #picture hand when touch
        cv2.rectangle(frame,(rectx,recty),(rectx+rectw,recty+recth),(0,255,0),3)
        frame = insert_img(frame,hand_img,rectx+5,recty+10)
        #number hand
        cv2.putText(frame,str(number_rect+1), (rectx+25,recty+recth-15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),3)
        state = check(depth)
    elif(state == "count_down"):
        #show number countdown
        cv2.putText(frame,str(count_down), (300,200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0,0,255),5)
        #picture reset 
        frame = insert_img(frame,x_img,ximgxy[0],ximgxy[1])
        state = count_num(depth)
    elif(state == "check_reset"):
        rectx = resetxy[0]
        recty = resetxy[1]
        #picture reset when touch
        cv2.putText(crop_frame,"RESET", (300,200), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,0,255),3)
        cv2.rectangle(frame,(rectx,recty),(rectx+resetwh[0],recty+resetwh[1]),(0,255,0),3)
        frame = insert_img(frame,x_img,ximgxy[0],ximgxy[1])
        state = reset(depth)
    return frame

def shuter(depth):
    global start_time
    global number_rect
    global rectxy
    rectx = rectxy[number_rect][0]
    recty = rectxy[number_rect][1]
    sum_boolean =  check_boolean(depth,rectx,recty,rectw,recth)
    if(time.time() - start_time >= 3):
        number_rect = 0
        random_number()
        return "idel"
    elif(sum_boolean > check_rect):
        start_time = time.time()
        return "check_touch"
    return "shuter"

def check(depth):
    global start_time
    global number_rect
    global rectxy
    rectx = rectxy[number_rect][0]
    recty = rectxy[number_rect][1]
    sum_boolean =  check_boolean(depth,rectx,recty,rectw,recth)
    if(time.time() - start_time >= 0.5):
        number_rect = number_rect+1
        if(number_rect < len(rectxy)): 
            random_number()
            return "shuter"
        else:
            number_rect = 0
            start_time = time.time()
            return "count_down"
    elif(not(sum_boolean > check_rect)):
        start_time = time.time()
        return "shuter"
    return "check_touch"


def count_num(depth):
    global count_down
    global start_time
    rectx = resetxy[0]
    recty = resetxy[1]
    sum_boolean =  check_boolean(depth,rectx,recty,90,90)
    if(sum_boolean > check_rect):
        count_down = 5
        start_time = time.time()
        return "check_reset"
    elif(time.time() - start_time >= 1):
        if(count_down == 5):
            ser.write('arm\n')
        start_time = time.time()
        count_down = count_down-1
        if(count_down == 0):
            count_down = 5
            capVideo()
            start_time = time.time()
            return "idel"
    return "count_down"

def reset(depth):
    global start_time
    rectx = resetxy[0]
    recty = resetxy[1]
    sum_boolean =  check_boolean(depth,rectx,recty,90,90)
    if(sum_boolean > check_rect):
        if(time.time() - start_time >= 1):
            ser.write('ready\n')
            return "shuter"
    else:
        return "count_down"
    return "check_reset"


def capVideo():
    global image, ser

    p = subprocess.Popen(["espeak", "-s", "100", "-g", "0.9", "-v", "en-us+f3", 'capture'])

    ser.write('capture\n')
    line = ser.readline()
    print line

    name = time.strftime("%d_%m_%Y_%H_%M_%S")
    name = "pic/"+name+".jpg"

    #cv2.imwrite(name,crop_frame)
    print 'save file: %s' % name
    cv2.imwrite(name,image)
    cmd_save = "./submit.py "+name
    os.system(cmd_save)

    print 'submit photo to server...'
    time.sleep(1)
    ser.write('ready\n')
    line = ser.readline()
    print line
        if p != None:
        p.terminate()

def speak(word):
    pass


if __name__ == "__main__":

        print 'Enter main loop...'

        window_title = 'Photo Capture'

    while 1:
        value,image = cap.read()       # read the next image from camera
        crop_frame = rgb_change_size() # resize the image
        thresh = adject_depth()        # get an image from the depth camera 
        
        # draw contours
        contours_frame = draw_contours(crop_frame,thresh)

        rect_frame = state_pic(contours_frame,thresh)

        cv2.namedWindow( window_title, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty( window_title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        cv2.imshow( window_title, rect_frame)
        #cv2.imshow('depth img',thresh )

        # quit program when 'esc' key is pressed
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            #cv2.imwrite("test_write.jpg", frame)
            cv2.destroyAllWindows()
            break

#########################################################################
