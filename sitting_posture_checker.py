import mediapipe as mp
import cv2
import math
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

window_name = "physiora"

# Font type.
font = cv2.FONT_HERSHEY_SIMPLEX

# Colors.
blue = (255, 127, 0)
red = (50, 50, 255)
green = (127, 255, 0)
dark_blue = (127, 20, 0)
light_green = (127, 233, 100)
yellow = (0, 255, 255)
pink = (255, 0, 255)

cap = cv2.VideoCapture(2) #"pushup_test2.mp4")


def findPose (img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = holistic.process(imgRGB)
        
        if results.pose_landmarks:
            if draw:
                mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                    )                
        return img

def findPosition(results, width, height):
        lmList = []
        if results.pose_landmarks:
            for id, lm in enumerate(results.pose_landmarks.landmark):
                #Determining the pixels of the landmarks
                cx, cy = int(lm.x * width), int(lm.y * height)
                lmList.append([id, cx, cy])
                
        return lmList

def findAngle(lmList, p1, p2, p3, draw=True):   
        #Get the landmarks
        x1, y1 = lmList[p1][1:]
        x2, y2 = lmList[p2][1:]
        x3, y3 = lmList[p3][1:]
        
        #Calculate Angle
        angle = math.degrees(math.atan2(y3-y2, x3-x2) - 
                             math.atan2(y1-y2, x1-x2))
        if angle < 0:
            angle += 360
            if angle > 180:
                angle = 360 - angle
        elif angle > 180:
            angle = 360 - angle
        # print(angle)
        
        #Draw
        # if draw:
        #     cv2.line(img, (x1, y1), (x2, y2), (255,255,255), 3)
        #     cv2.line(img, (x3, y3), (x2, y2), (255,255,255), 3)

            
        #     cv2.circle(img, (x1, y1), 5, (0,0,255), cv2.FILLED)
        #     cv2.circle(img, (x1, y1), 15, (0,0,255), 2)
        #     cv2.circle(img, (x2, y2), 5, (0,0,255), cv2.FILLED)
        #     cv2.circle(img, (x2, y2), 15, (0,0,255), 2)
        #     cv2.circle(img, (x3, y3), 5, (0,0,255), cv2.FILLED)
        #     cv2.circle(img, (x3, y3), 15, (0,0,255), 2)
            
        #     cv2.putText(img, str(int(angle)), (x2-50, y2+50), 
        #                 cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 2)
        return angle

if cap.isOpened() is False:
    print("error opening camera")

with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        ret, frame = cap.read()

        if ret == False:
            break

        image_height, image_width, _ = frame.shape
            # Recolor Feed
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)   
        image.flags.writeable = False
        
        results = holistic.process(image)
        pose_list = []
        if results.pose_landmarks:
            pose_list = findPosition(results, image_width, image_height)
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                    )
            
            right_knee = findAngle(pose_list, 24, 26, 28)
            left_knee = findAngle(pose_list, 23, 25, 27)
            right_hip = findAngle(pose_list, 12, 24, 26)
            left_hip = findAngle(pose_list, 11, 23, 25)
            right_neck_inclination = findAngle(pose_list, 8, 12, 24)
            left_neck_inclination = findAngle(pose_list, 7, 11, 23)
            neck_inclination = (right_neck_inclination + left_neck_inclination) / 2
            neck_inclination = 180 - neck_inclination
            hip = (right_hip + left_hip) / 2
            action = 0
            
            
            if hip > 163 and hip <= 180:
                action = 1
                print(action)
            elif hip < 150:
                action = 2
                print(action)
            
            
            if action == 2:
                if neck_inclination < 45 and (hip > 85 and hip < 120):
                    cv2.putText(image, "Sitting:", (10, 30), font, 0.9, light_green, 2)
                    cv2.putText(image, "Correct Sitting Posture", (10, 60), font, 0.9, light_green, 2)
                    # cv2.putText(image, "Correct Sitting Posture", (10, 30), font, 0.9, green, 2)
                    print("correct sitting posture")
                else:
                    cv2.putText(image, "Sitting", (10, 30), font, 0.9, red, 2)
                    cv2.putText(image, "Bad Sitting Posture", (10, 60), font, 0.9, red, 2)
                    print("bad sitting posture")
            else:
                if neck_inclination < 40 and (hip > 170):
                    cv2.putText(image, "Standing", (10, 30), font, 0.9, light_green, 2)
                    #cv2.putText(image, "Correct Standing Posture", (10, 60), font, 0.9, light_green, 2)
                    # cv2.putText(image, str(hip), (10, 90), font, 0.9, green, 2)
                    print("correct sitting posture")
                else:
                    cv2.putText(image, "Standing:", (10, 30), font, 0.9, light_green, 2)
                    #cv2.putText(image, "Bad Standing Posture", (10, 60), font, 0.9, red, 2)
                    # cv2.putText(image, str(hip), (10, 90), font, 0.9, green, 2)
                    # cv2.putText(image, str(neck_inclination), (10, 120), font, 0.9, green, 2)
                    print("bad sitting posture")

            
            print("hip", hip)
            print("neck ", neck_inclination)
        cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow(window_name, image)
        

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break