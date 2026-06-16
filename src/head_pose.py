from audioop import avg
from glob import glob
from itertools import count
import cv2
import mediapipe as mp
import numpy as np
import threading as th
import sounddevice as sd
import audio

# place holders and global variables
x = 0                                       # X axis head pose
y = 0                                       # Y axis head pose

X_AXIS_CHEAT = 0
Y_AXIS_CHEAT = 0
LIP_MOVEMENT_CHEAT = 0

# Lip movement variables
LIP_OPENING_THRESHOLD = 0.03                # Threshold for lip opening detection
LIP_MOVEMENT_HISTORY = []
LIP_MOVEMENT_HISTORY_SIZE = 15
LIP_OPENING_HISTORY = []
LIP_OPENING_CONSECUTIVE_FRAMES = 0
LAST_LIP_OPENING = 0

def calculate_lip_opening(landmarks, img_w, img_h):
    """Calculate the lip opening distance using multiple MediaPipe landmarks."""
    try:
        # Use multiple lip landmarks for more robust detection
        # Top lip: landmark 13 (center)
        # Bottom lip: landmark 14 (center)
        # Left corner: landmark 61
        # Right corner: landmark 291
        
        top_lip = landmarks.landmark[13]      # Upper lip inner
        bottom_lip = landmarks.landmark[14]   # Lower lip inner
        left_corner = landmarks.landmark[61]  # Left lip corner
        right_corner = landmarks.landmark[291] # Right lip corner
        
        # Calculate vertical distance (mouth opening)
        vertical_dist = abs(bottom_lip.y - top_lip.y)
        
        # Calculate horizontal distance (mouth width)
        horizontal_dist = abs(right_corner.x - left_corner.x)
        
        # Combined mouth activity score (weighted)
        mouth_opening = (vertical_dist * 0.7 + horizontal_dist * 0.3)
        
        return mouth_opening
    except:
        return 0

def detect_lip_movement(current_opening):
    """Detect significant lip movement with improved sensitivity."""
    global LIP_MOVEMENT_CHEAT, LIP_OPENING_HISTORY, LIP_OPENING_CONSECUTIVE_FRAMES, LAST_LIP_OPENING
    
    LIP_OPENING_HISTORY.append(current_opening)
    
    # Keep history limited
    if len(LIP_OPENING_HISTORY) > LIP_MOVEMENT_HISTORY_SIZE:
        LIP_OPENING_HISTORY.pop(0)
    
    # Detection logic improved - more sensitive
    if len(LIP_OPENING_HISTORY) >= 3:
        # Check for significant change from previous frame
        frame_change = abs(current_opening - LAST_LIP_OPENING)
        
        # Calculate recent average
        recent_avg = sum(LIP_OPENING_HISTORY[-3:]) / 3
        
        # ADJUSTED THRESHOLDS based on actual values:
        # Open mouth: ~0.074, Closed mouth: ~0.023
        # Trigger if mouth is open (avg > 0.05) OR significant change (change > 0.003)
        if frame_change > 0.003 or recent_avg > 0.05:
            LIP_OPENING_CONSECUTIVE_FRAMES += 1
        else:
            LIP_OPENING_CONSECUTIVE_FRAMES = max(0, LIP_OPENING_CONSECUTIVE_FRAMES - 1)
        
        # Trigger alert faster (2 frames instead of 3)
        if LIP_OPENING_CONSECUTIVE_FRAMES >= 2:
            LIP_MOVEMENT_CHEAT = 1
        else:
            LIP_MOVEMENT_CHEAT = 0
        
        # Debug: print every frame to see what's happening
        print(f"LIP DEBUG | Opening: {current_opening:.5f} | Change: {frame_change:.5f} | Avg: {recent_avg:.5f} | Consecutive: {LIP_OPENING_CONSECUTIVE_FRAMES} | CHEAT: {LIP_MOVEMENT_CHEAT}")
    
    LAST_LIP_OPENING = current_opening
    return LIP_MOVEMENT_CHEAT

def pose():
    global VOLUME_NORM, x, y, X_AXIS_CHEAT, Y_AXIS_CHEAT, LIP_MOVEMENT_CHEAT, LIP_OPENING_CONSECUTIVE_FRAMES, LAST_LIP_OPENING
    try:
        print("Initializing camera...")
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Cannot open camera")
            return
        
        print("✓ Camera opened successfully")
        mp_drawing = mp.solutions.drawing_utils

        frame_count = 0
        while cap.isOpened():
            success, image = cap.read()
            
            if not success:
                print("Failed to read frame")
                continue
                
            # Flip the image horizontally for a later selfie-view display
            # Also convert the color space from BGR to RGB
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

            # To improve performance
            image.flags.writeable = False
            
            # Get the result
            results = face_mesh.process(image)
            
            # To improve performance
            image.flags.writeable = True
            
            # Convert the color space from RGB to BGR
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            img_h, img_w, img_c = image.shape
            face_3d = []
            face_2d = []
            
            face_ids = [33, 263, 1, 61, 291, 199]

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    try:
                        # Calculate lip opening for lip movement detection
                        lip_opening = calculate_lip_opening(face_landmarks, img_w, img_h)
                        detect_lip_movement(lip_opening)
                    except Exception as e:
                        print(f"Error in lip detection: {e}")
                
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None)
                for idx, lm in enumerate(face_landmarks.landmark):
                    # print(lm)
                    if idx in face_ids:
                        if idx == 1:
                            nose_2d = (lm.x * img_w, lm.y * img_h)
                            nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 8000)

                        x, y = int(lm.x * img_w), int(lm.y * img_h)

                        # Get the 2D Coordinates
                        face_2d.append([x, y])

                        # Get the 3D Coordinates
                        face_3d.append([x, y, lm.z])       
                
                # Convert it to the NumPy array
                face_2d = np.array(face_2d, dtype=np.float64)

                # Convert it to the NumPy array
                face_3d = np.array(face_3d, dtype=np.float64)

                # The camera matrix
                focal_length = 1 * img_w

                cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                        [0, focal_length, img_w / 2],
                                        [0, 0, 1]])

                # The Distance Matrix
                dist_matrix = np.zeros((4, 1), dtype=np.float64)

                # Solve PnP
                success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

                # Get rotational matrix
                rmat, jac = cv2.Rodrigues(rot_vec)

                # Get angles
                angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

                # Get the y rotation degree
                x = angles[0] * 360
                y = angles[1] * 360

                # print(y)

                # See where the user's head tilting
                if y < -10:
                    text = "Looking Left"
                elif y > 10:
                    text = "Looking Right"
                elif x < -10:
                    text = "Looking Down"
                else:
                    text = "Forward"
                text = str(int(x)) + "::" + str(int(y)) + text
                # print(str(int(x)) + "::" + str(int(y)))
                # print("x: {x}   |   y: {y}  |   sound amplitude: {amp}".format(x=int(x), y=int(y), amp=audio.SOUND_AMPLITUDE))
                
                # Y is left / right
                # X is up / down
                if y < -10 or y > 10:
                    X_AXIS_CHEAT = 1
                else:
                    X_AXIS_CHEAT = 0

                if x < -5:
                    Y_AXIS_CHEAT = 1
                else:
                    Y_AXIS_CHEAT = 0

                if frame_count % 15 == 0:
                    print(f"HEAD DEBUG | X-angle={x:.1f} | Y-angle={y:.1f} | X_CHEAT={X_AXIS_CHEAT} | Y_CHEAT={Y_AXIS_CHEAT} | LIP_CHEAT={LIP_MOVEMENT_CHEAT}")

                # Display the nose direction
                nose_3d_projection, jacobian = cv2.projectPoints(nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)

                p1 = (int(nose_2d[0]), int(nose_2d[1]))
                p2 = (int(nose_3d_projection[0][0][0]), int(nose_3d_projection[0][0][1]))
                   

                # Add the text on the image
                cv2.putText(image, text, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            cv2.imshow('Head Pose Estimation', image)

            if cv2.waitKey(5) & 0xFF == 27:
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"Error in pose detection: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            cap.release()
            cv2.destroyAllWindows()
        except:
            pass

#############################
if __name__ == "__main__":
    t1 = th.Thread(target=pose)

    t1.start()

    t1.join()