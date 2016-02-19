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
a = 0
state = 0
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

def check_opencv_version(major, lib=None):
    # if the supplied library is None, import OpenCV
    if lib is None:
        import cv2 as lib
        

    # return whether or not the current OpenCV version matches the
    # major version number
    return lib.__version__.startswith(major)
    
if __name__ == "__main__":
    while 1:
        #get a frame from RGB camera
        # Setup SimpleBlobDetector parameters.
        ##img = np.zeros((1080, 1920))	
        frame = get_video()
        frame=cv2.flip(frame,1)
        big_frame = cv2.resize(frame,(0,0), fx=zoomx, fy=zoomy)
        crop_frame = big_frame[480*(zoomx-1)/2:480+480*(zoomx-1)/2,640*(zoomy-1)/2:640+640*(zoomy-1)/2]
        #blurred_frame = cv2.GaussianBlur(crop_frame, (5, 5), 0)
        #thresh_frame = cv2.threshold(blurred_frame, 60, 255, cv2.THRESH_BINARY)[1]
        ##cv2.namedWindow("RGB image", cv2.WND_PROP_FULLSCREEN)
        ##cv2.setWindowProperty("RGB image", cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
		
        #cv2.rectangle(frame,(200,250),(300,350),(0,255,0),1)
        #cv2.imshow('RGB image',frame)
        cv2.rectangle(crop_frame,(0,0),(100,100),(0,255,0),1)
        
        #get a frame from depth sensor
        depth = get_depth()
        depth=cv2.flip(depth,1)
        depth = 255 * np.logical_and(depth >= current_depth - threshold, depth <= current_depth + threshold)    
        depth = depth.astype(np.uint8)  
		#adject depth data
        blurred = cv2.GaussianBlur(depth, (5, 5), 0)
        thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]	
        boolean = np.equal(thresh[0:100,0:100],255)
        if(np.sum(boolean) > 5000):
            cv2.rectangle(crop_frame,(2,2),(102,102),(0,255,0),5)
        else:
            state = 0

        if(state == 0):
            start_time = time.time()
            if(np.sum(boolean) > 5000):
                state = 1
        elif(state == 1):
            cv2.putText(crop_frame,"1", (300,200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0,0,255),5)
            if(time.time() - start_time >= 1):
                start_time = time.time()
                state = 2
        elif(state == 2):
            cv2.putText(crop_frame,"2", (300,200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0,0,255),5)
            if(time.time() - start_time >= 1):
                start_time = time.time()
                state = 3
        elif(state == 3):
            cv2.putText(crop_frame,"3", (300,200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0,0,255),5)
            if(time.time() - start_time >= 1):
                start_time = time.time()
                state = 4
        elif(state == 4):
            cv2.putText(crop_frame,"4", (300,200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0,0,255),5)
            if(time.time() - start_time >= 1):
                start_time = time.time()
                state = 5
        elif(state == 5):
            cv2.putText(crop_frame,"5", (300,200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0,0,255),5)
            if(time.time() - start_time >= 1):
                start_time = time.time()
                state = 0
		
        #cv2.imshow('RGB image',frame)
        #cv2.imshow('RGB image',big_frame)
        #cv2.namedWindow("RGB image", cv2.WND_PROP_FULLSCREEN)
        #cv2.setWindowProperty("RGB image", cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
        cv2.imshow('RGB image',crop_frame)
        #cv2.imshow('depth img',thresh )
        # quit program when 'esc' key is pressed
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            #cv2.imwrite("test_write.jpg", frame)
            cv2.destroyAllWindows()
            break
