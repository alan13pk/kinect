#import the necessary modules
import freenect
import cv2
import numpy as np
import time
threshold = 100
current_depth = 650
adj = 8
zoomy = 1.1
zoomx = 1.13
state_rect = "start_rect"
state_num = "start_num"
rectxy = [[2,2],[102,2],[202,2]]
rectw = 100
recth = 100
number_rect = 0
check_rect = rectw*recth/2
sum_boolean = 0
# Create a detector with the parameters
ver = (cv2.__version__).split('.')
#print ver

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
    ( cnts, _) = cv2.findContours(depth.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours( frame, cnts, -1, (255,0,255), 5 )
    return frame

def check_boolean(thresh,rectx,recty):
    boolean = np.equal(thresh[recty:(recty+recth),rectx:(rectx+rectw)],255)
    return np.sum(boolean)

def draw_rect(frame,depth):
    global number_rect
    global state_rect
    global start_time
    rectx = rectxy[number_rect][0]
    recty = rectxy[number_rect][1]
    sum_boolean =  check_boolean(depth,rectx,recty) 
    if(state_rect == "start_rect"):
        #print("asd")
        if(sum_boolean > check_rect):
            cv2.rectangle(frame,(rectx,recty),(rectx+rectw,rectx+recth),(0,255,0),3)
            if(time.time() - start_time >= 1) :
                number_rect = number_rect+1
                if(number_rect < len(rectxy)):
                    state_rect = "draw_rect"
                else:
                    number_rect = 0
                    state_rect = "end_rect"
        else:
            cv2.rectangle(frame,(rectx,recty),(rectx+rectw,recty+recth),(0,0,255),3)
            start_time = time.time()

    elif(state_rect == "draw_rect"):
        cv2.rectangle(frame,(rectx,recty),(rectx+rectw,recty+recth),(0,0,255),3)
        if(time.time() - start_time >= 3):
            number_rect = 0        
            state_rect = "start_rect"
        elif(sum_boolean > check_rect):
            start_time = time.time()
            state_rect = "check_rect"

    elif(state_rect == "check_rect"):
        cv2.rectangle(frame,(rectx,recty),(rectx+rectw,recty+recth),(0,255,0),3)
        if(time.time() - start_time >= 1):
            number_rect = number_rect+1
            if(number_rect < len(rectxy)):         
                state_rect = "draw_rect"
            else:
                number_rect = 0
                state_rect = "end_rect"
        elif(not(sum_boolean > check_rect)):
            number_rect = 0
            state_rect = "start_rect"
    return frame

def draw_num(frame,depth):
    global state_num
    


if __name__ == "__main__":
    while 1:
        crop_frame = rgb_change_size()
        #get a frame from depth sensor
		#adject depth data
        thresh = adject_depth()
        
        #draw contours
        contours_frame = draw_contours(crop_frame,thresh)

        #draw rect
        rect_frame = draw_rect(contours_frame,thresh)

        cv2.imshow('RGB image',rect_frame)
        #cv2.imshow('depth img',thresh )
        # quit program when 'esc' key is pressed
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            #cv2.imwrite("test_write.jpg", frame)
            cv2.destroyAllWindows()
            break
