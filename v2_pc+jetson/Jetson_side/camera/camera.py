import cv2
import dlib

face_cascade=cv2.CascadeClassifier("camera/haarcascade_frontalface_alt2.xml")
predictor = dlib.shape_predictor("camera/shape_predictor_68_face_landmarks.dat")
detector = dlib.get_frontal_face_detector()

ds_factor=0.6
class VideoCamera(object):
    def __init__(self):
       #capturing video
       self.video = cv2.VideoCapture(0)
    
    def close(self):
        #releasing camera
        # self.video.stop()
        self.video.release()
        # self.output.release()

    def get_frame(self):
        #extracting frames
        ret, frame = self.video.read()
        frame=cv2.resize(frame,None,fx=ds_factor,fy=ds_factor,
        interpolation=cv2.INTER_AREA)         
        # self.write_to_video(frame)           
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        face_rects = detector(gray, 0)

        # face_rects=face_cascade.detectMultiScale(gray,1.3,5)
        

        # for (x,y,w,h) in face_rects:
        #     cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

        if str(face_rects) != "rectangles[]":
            for face_rect in face_rects:
                # assign the facial landmarks
                landmarks = predictor(gray, face_rect)
                # unpack the 68 landmark coordinates from the dlib object into a list 
                landmarks_list = []
                for i in range(0, landmarks.num_parts):
                    landmarks_list.append((landmarks.part(i).x, landmarks.part(i).y))
                # for each landmark, plot and write number
                for landmark_num, xy in enumerate(landmarks_list, start = 1):
                    cv2.circle(frame, (xy[0], xy[1]), 12, (168, 0, 20), -1)
                    cv2.putText(frame, str(landmark_num),(xy[0]-7,xy[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255,255,255), 1)
        
        # encode OpenCV raw frame to jpg and displaying it  
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def write_to_video(self,frame):
        # codec = cv2.VideoWriter_fourcc(*'DIVX')  # for windows   
        codec = cv2.VideoWriter_fourcc(*'DIVX')  # for mac OSX
        self.output = cv2.VideoWriter('video.avi',codec,30,(640, 480))
        self.output.write(frame)