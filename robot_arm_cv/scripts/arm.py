import cv2
import mediapipe as mp
from scipy.interpolate import interp1d
import numpy as np
import rospy
from geometry_msgs.msg import Quaternion

rospy.init_node('opencv_node', anonymous=True)
pub = rospy.Publisher('arm_angles', Quaternion, queue_size=1)


def interpolate_x(x):

    upp=[0,1280]
    lpp=[160,50]
    return np.interp(x,upp,lpp)

def interpolate_z(x):
    
    upp=[-90,-20]
    lpp=[120,70]
    return np.interp(x,upp,lpp)

def interpolate_y(x):

    upp=[0,720]
    lpp=[70,40]
    return np.interp(x,upp,lpp)


# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize MediaPipe Drawing module for drawing landmarks
mp_drawing = mp.solutions.drawing_utils

# Initialize variables to store previous index finger positions
prev_index_x = None
prev_index_y = None

# Open the webcam
cap = cv2.VideoCapture(2)

# Set the desired frame width and height
frame_width = 1280
frame_height = 720

# Set the video capture properties to the desired frame width and height
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the index finger tip landmark
            index_tip_landmark = hand_landmarks.landmark[mp_hands.HandLandmark(12).value]
            wrist_landmark = hand_landmarks.landmark[mp_hands.HandLandmark(0).value]
            
            # Calculate the Euclidean distance between index finger tip and wrist
            distance = ((index_tip_landmark.x - wrist_landmark.x)**2 + 
                        (index_tip_landmark.y - wrist_landmark.y)**2)**0.5
            

            x_angle=interpolate_x(index_tip_landmark.x*frame_width)
            y_angle=interpolate_y(index_tip_landmark.y*frame_height)
            z_angle=interpolate_z(index_tip_landmark.z*frame_height)

            #print("actual : ",index_tip_landmark.x*frame_width,index_tip_landmark.y*frame_height," interpolated : ",x_angle,y_angle)
            print(index_tip_landmark.z*frame_height)

            if distance < 0.4:  # Adjust the threshold based on your setup
                gesture = 1 #fist
            else:
                gesture = 0 #palm

            cv2.putText(frame, str(gesture) , (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            p=Quaternion()
            p.x=x_angle
            p.y=y_angle
            p.z=z_angle
            p.w=gesture
            pub.publish(p)

    cv2.imshow('Hand Gestures Recognition', frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()
