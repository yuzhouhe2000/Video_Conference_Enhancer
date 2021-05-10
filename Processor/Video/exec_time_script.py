# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 22:20:37 2018

@author: James Wu
"""

import dlib
import cv2
import numpy as np
import socket
import json
import time 


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




predictor_path = "shape_predictor_5_face_landmarks.dat"#人脸关键点训练数据路径
detector = dlib.get_frontal_face_detector()#人脸检测器detector
predictor = dlib.shape_predictor(predictor_path)#人脸关键点检测器predictor

cap = cv2.VideoCapture(0)#开启摄像头

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



while(cap.isOpened()):
    #读取视频帧
    _, img = cap.read()
    start_time = time.time()
    #转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 人脸检测
    rects = detector(gray, 1)
    
    # 对每个检测到的人脸进行操作
    for i, rect in enumerate(rects):
        x_face = rect.left()
        y_face = rect.top()
        w_face = rect.right() - x_face
        h_face = rect.bottom() - y_face

        print(x_face)

        cv2.rectangle(img, (x_face,y_face), (x_face+w_face,y_face+h_face), (0,255,0), 2)
        # 检测并标注landmarks        
        landmarks = predictor(gray, rect)

        #print("Execution time", time.time()-start_time)
        landmarks = landmarks_to_np(landmarks)
        for (x, y) in landmarks:
            cv2.circle(img, (x, y), 2, (0, 0, 255), -1)

        # 线性回归

    
    cv2.imshow("Result", img)

    k = cv2.waitKey(5) & 0xFF
    if k==27:   #按“Esc”退出
        break

cap.release()
cv2.destroyAllWindows()
