
import dlib
import cv2
import numpy as np
import socket
import json
from adafruit_servokit import ServoKit
kit=ServoKit(channels=4)

def setServos(pan,tilt,x_face,w_face,y_face,h_face,width,height):
#Set pan/tilt 
        center_x = x_face + w_face/2
        center_y = y_face + h_face/2

        errorPan = center_x - width/2
        errorTilt = center_y - height/2

        if abs(errorPan)>15:
            pan = pan-errorPan/75
        if abs(errorTilt)>15:
            tilt = tilt - errorTilt/75

        if pan>180:
            pan=180
            print("Pan Out of  Range")   
        if pan<0:
            pan=0
            print("Pan Out of  Range") 
        if tilt>180:
            tilt=180
            print("Tilt Out of  Range") 
        if tilt<0:
            tilt=0
            print("Tilt Out of  Range")                 

        kit.servo[0].angle=pan
        kit.servo[1].angle=tilt

        return pan, tilt

video_port = 9996

client_video_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def digi_zoom(eye_avg,img):
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    width_step = width/5
    height_step = height/5
    
    if np.floor(eye_avg) == 6:
        x1 = int(width_step*1.5)
        x2 = int(width-width_step*1.5)
        y1 = int(height_step*1.5)
        y2 = int(height-height_step*1.5)
        img = img[y1:y2,x1:x2]

    if np.floor(eye_avg) == 7:
        x1 = int(width_step*1.25)
        x2 = int(width-width_step*1.25)
        y1 = int(height_step*1.25)
        y2 = int(height-height_step*1.25)
        img = img[y1:y2,x1:x2]

    if np.floor(eye_avg) == 8: 
        x1 = int(width_step)
        x2 = int(width-width_step)
        y1 = int(height_step)
        y2 = int(height-height_step)
        img = img[y1:y2,x1:x2]
    
    if np.floor(eye_avg) == 9:
        x1 = int(width_step/2)
        x2 = int(width-width_step/2)
        y1 = int(height_step/2) 
        y2 = int(height-height_step/2)
        img = img[y1:y2,x1:x2]
    if np.floor(eye_avg) == 10:
        img = img
    img = cv2.resize(img, (int(width),int(height)),interpolation=cv2.INTER_CUBIC)
    return img


def landmarks_to_np(landmarks, dtype="int"):

    num = landmarks.num_parts
    
    # initialize the list of (x, y)-coordinates
    coords = np.zeros((num, 2), dtype=dtype)
    
    # loop over the 68 facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, num):
        coords[i] = (landmarks.part(i).x, landmarks.part(i).y)
    # return the list of (x, y)-coordinates
    return coords



def get_centers(img, landmarks):

    EYE_LEFT_OUTTER = landmarks[2]
    EYE_LEFT_INNER = landmarks[3]
    EYE_RIGHT_OUTTER = landmarks[0]
    EYE_RIGHT_INNER = landmarks[1]

    x = ((landmarks[0:4]).T)[0]
    y = ((landmarks[0:4]).T)[1]
    A = np.vstack([x, np.ones(len(x))]).T
    k, b = np.linalg.lstsq(A, y, rcond=None)[0]
    
    x_left = (EYE_LEFT_OUTTER[0]+EYE_LEFT_INNER[0])/2
    x_right = (EYE_RIGHT_OUTTER[0]+EYE_RIGHT_INNER[0])/2
    LEFT_EYE_CENTER =  np.array([np.int32(x_left), np.int32(x_left*k+b)])
    RIGHT_EYE_CENTER =  np.array([np.int32(x_right), np.int32(x_right*k+b)])
    
    pts = np.vstack((LEFT_EYE_CENTER,RIGHT_EYE_CENTER))
    cv2.polylines(img, [pts], False, (255,0,0), 1) #画回归线
    cv2.circle(img, (LEFT_EYE_CENTER[0],LEFT_EYE_CENTER[1]), 3, (0, 0, 255), -1)
    cv2.circle(img, (RIGHT_EYE_CENTER[0],RIGHT_EYE_CENTER[1]), 3, (0, 0, 255), -1)
    
    return LEFT_EYE_CENTER, RIGHT_EYE_CENTER




predictor_path = "shape_predictor_5_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)

cap = cv2.VideoCapture(0)

eye_dist = np.array([])
face_dist = np.array([])
face_check = 0
frame = 0

#Get camera parameters 
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(width,height)

#Initialize camera 
pan = 90
tilt = 45
setServos(pan, tilt)


while(cap.isOpened()):

    _, img = cap.read()
    

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    

    rects = detector(gray, 1)
    

    for i, rect in enumerate(rects):

        x_face = rect.left()
        y_face = rect.top()
        w_face = rect.right() - x_face
        h_face = rect.bottom() - y_face

        #Get Face width average 
        if face_check == 0: 
            face_check = w_face
        face_dist = np.append(face_dist, w_face)
        face_avg = np.mean(face_dist)
        if len(face_dist) == 10:
            face_dist = np.delete(face_dist, 0)
        
        
       
        #Adjust frame check
        if frame == 30: 
            face_check = face_avg
            frame = 0
        frame = frame +  1


        cv2.rectangle(img, (x_face,y_face), (x_face+w_face,y_face+h_face), (0,255,0), 2)
        cv2.putText(img, "Face #{}".format(i + 1), (x_face - 10, y_face - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        
    
        landmarks = predictor(gray, rect)
        landmarks = landmarks_to_np(landmarks)
        for (x, y) in landmarks:
            cv2.circle(img, (x, y), 2, (0, 0, 255), -1)


        LEFT_EYE_CENTER, RIGHT_EYE_CENTER = get_centers(img, landmarks)
        
        Distance = np.sqrt(abs(RIGHT_EYE_CENTER[0] - LEFT_EYE_CENTER[0])^2 + abs(RIGHT_EYE_CENTER[1] - LEFT_EYE_CENTER[1])^2)

        #Get eye width average
        eye_dist = np.append(eye_dist, Distance)
        eye_avg = np.mean(eye_dist)

        if len(eye_dist) == 10:
            eye_dist = np.delete(eye_dist, 0)


    if abs(face_avg - face_check) > face_check*.25:
        print("Adjust Gain",  eye_avg)
        volume = Distance/10.0
   
        volume = (2.2 - volume)

        if volume >= 1.5:
            voume = 1.5
        if volume <= 0.5:
            volume = 0.5
        
        parameters = {"volume": volume}
    
        parameters_json = json.dumps(parameters).encode('utf-8')
        client_video_sender.sendto(parameters_json, ("127.0.0.1", video_port))
    
    img = digi_zoom(eye_avg, img)
    cv2.imshow("Result", img)
    
    k = cv2.waitKey(5) & 0xFF
    if k==27:   
        break

cap.release()
cv2.destroyAllWindows()
