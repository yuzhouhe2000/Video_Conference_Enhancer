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

video_port = 9996

client_video_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


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
while(cap.isOpened()):
    #读取视频帧
    _, img = cap.read()
    
    #转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 人脸检测
    rects = detector(gray, 1)
    
    # 对每个检测到的人脸进行操作
    for i, rect in enumerate(rects):
        # 得到坐标
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

        # 绘制边框，加文字标注
        cv2.rectangle(img, (x_face,y_face), (x_face+w_face,y_face+h_face), (0,255,0), 2)
        cv2.putText(img, "Face #{}".format(i + 1), (x_face - 10, y_face - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        
        # 检测并标注landmarks        
        landmarks = predictor(gray, rect)
        landmarks = landmarks_to_np(landmarks)
        for (x, y) in landmarks:
            cv2.circle(img, (x, y), 2, (0, 0, 255), -1)

        # 线性回归
        LEFT_EYE_CENTER, RIGHT_EYE_CENTER = get_centers(img, landmarks)
        
        Distance = np.sqrt(abs(RIGHT_EYE_CENTER[0] - LEFT_EYE_CENTER[0])^2 + abs(RIGHT_EYE_CENTER[1] - LEFT_EYE_CENTER[1])^2)

        #Get eye width average
        eye_dist = np.append(eye_dist, Distance)
        eye_avg = np.mean(eye_dist)

        if len(eye_dist) == 10:
            eye_dist = np.delete(eye_dist, 0)

        volume = Distance/10.0
   
        volume = (2.2 - volume)

        if volume >= 1.5:
            voume = 1.5
        if volume <= 0.5:
            volume = 0.5
        
        parameters = {"volume": volume}
    
        parameters_json = json.dumps(parameters).encode('utf-8')
        client_video_sender.sendto(parameters_json, ("127.0.0.1", video_port))
        
    
    # 显示结果
    if abs(face_avg - face_check) > 20:
        print("Adjust Gain",  eye_avg)

    cv2.imshow("Result", img)
    
    k = cv2.waitKey(5) & 0xFF
    if k==27:   #按“Esc”退出
        break

cap.release()
cv2.destroyAllWindows()
