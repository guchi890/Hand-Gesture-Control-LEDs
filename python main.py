import cv2
import mediapipe as mp
import serial
import time

# --- Arduino Serial Setup ---
# Change 'COM3' to the COM port of your Arduino (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux/Mac)
try:
    ser = serial.Serial('COM3', 9600, timeout=1) 
    time.sleep(2) # Give Arduino time to reset and connect
    print("Arduino connected successfully!")
except serial.SerialException:
    print("Error: Could not open serial port. Check if Arduino is connected and the port is correct.")
    print("Exiting...")
    exit()

# --- MediaPipe Hand Detection Setup ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# --- Webcam Setup ---
cap = cv2.VideoCapture(0) # 0 for default webcam

if not cap.isOpened():
    print("Error: Could not open webcam.")
    print("Exiting...")
    ser.close()
    exit()

# --- Finger Counting Logic ---
# Tip IDs for each finger (from MediaPipe hand landmark model)
TIP_IDS = [4, 8, 12, 16, 20] # Thumb, Index, Middle, Ring, Pinky

def count_fingers(hand_landmarks_list):
    fingers_up = 0
    if not hand_landmarks_list:
        return 0

    # Assume only one hand for simplicity for now
    hand_landmarks = hand_landmarks_list[0].landmark

    # Check Thumb
    if hand_landmarks[TIP_IDS[0]].x < hand_landmarks[TIP_IDS[0] - 1].x: # For right hand, thumb tip is usually left of its base
        fingers_up += 1
    
    # Check other 4 fingers (Index, Middle, Ring, Pinky)
    for i in range(1, 5): # Iterate for index, middle, ring, pinky
        if hand_landmarks[TIP_IDS[i]].y < hand_landmarks[TIP_IDS[i] - 2].y: # Finger tip is above the knuckle
            fingers_up += 1
    return fingers_up

prev_fingers_up = -1 # To detect change and avoid sending redundant data

print("\n--- Hand Gesture LED Control ---")
print("Show 1 to 5 fingers to control LEDs.")
print("Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1) # Mirror the webcam feed for intuitive display
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    current_fingers_up = 0
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            current_fingers_up = count_fingers(results.multi_hand_landmarks)
            # You might need to adjust thumb detection logic based on left/right hand and camera angle
            # For simplicity, this assumes a consistent hand orientation.

    # Display finger count on screen
    cv2.putText(frame, f"Fingers: {current_fingers_up}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    
    # Send data to Arduino only if finger count changes
    if current_fingers_up != prev_fingers_up:
        print(f"Detected: {current_fingers_up} fingers up. Sending to Arduino...")
        ser.write(str(current_fingers_up).encode()) # Send as string (e.g., "1", "2", "0")
        prev_fingers_up = current_fingers_up
        time.sleep(0.1) # Small delay to prevent spamming Arduino

    cv2.imshow("Hand Gesture LED Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
print("\nExiting program. Turning off all LEDs.")
ser.write(b'0') # Send '0' to turn off all LEDs on exit
cap.release()
cv2.destroyAllWindows()
ser.close()
print("Resources released.")
