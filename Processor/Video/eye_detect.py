import numpy as np
import cv2
import numpy as np
import time

def calculateDistance(eye_dist_pix):
    F = 1
    eye_dist_cm = .65
    D = (eye_dist_cm * F)/eye_dist_pix
    return D

def gstreamer_pipeline(
    capture_width=3280,
    capture_height=2464,
    display_width=820,
    display_height=616,
    framerate=21,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )
# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades

#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
# eye_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')

# If using jetson, use first line and comment out second line
# cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
cap = cv2.VideoCapture(0)

index = 1
sum_face = 0
sum_eye = 0
window = 10

face_vect = np.zeros(window)
eye_vect = np.zeros(window)

face_check = 0
eye_check_cnt = 0
cnt = 0
face_size= 0
eye_size = 0
count = 0
x_array = np.array([])

while 1:
    ret, img = cap.read()
    start_time = time.time()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    sum_face = sum_face - face_vect[index]
    sum_eye = sum_eye - eye_vect[index]


    #Get Values
    for (x,y,w,h) in faces:
        np.append(x_array, x)
        print(x)
        face_size = w
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        
        eyes = eye_cascade.detectMultiScale(roi_gray)
        temp = 0


        for (ex,ey,ew,eh) in eyes:
            if len(eyes) == 2:
                eye_size = abs(ex - temp)
                temp = ex

            

            #Moving Average Filter for Facial Size
            face_vect[index] = face_size
            sum_face = sum_face + face_size
            face_avg = sum_face/window
            

            #Moving Average Filter for Eye Size
            eye_vect[index] = eye_size
            sum_eye = sum_eye + eye_size
            eye_avg = sum_eye/window
            
            #Increment index and wrap
            index = (index + 1)%window

            #Check for changes 
            diff = abs(face_avg - face_check)
            perc = .1*face_avg
            
            if eye_check_cnt > 10:
                if diff > perc:
                    cam_distance = calculateDistance(eye_avg)

                    

            
            if cnt > 10:
                face_check = face_avg
                cnt = 0
            
            cnt = cnt + 1
            eye_check_cnt = eye_check_cnt + 1

            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
    cv2.circle(roi_color, (int(ex+ew/2),int(ey+eh/2)), 2, (0,0,255))
    cv2.imshow('img',img)

    count = count + 1
    if count == 1000:
        break

cap.release()
