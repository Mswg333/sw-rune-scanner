import cv2
import mss
import numpy as np
from config import MONITOR_REGION

def live_calibration():
    with mss.mss() as sct:
        print("Live Calibration started. Press 'q' on the image window to quit.")
        while True:
            # Grab the region defined in your config
            screenshot = sct.grab(MONITOR_REGION)
            
            # Convert to numpy array for OpenCV
            frame = np.array(screenshot)
            
            # Show the live feed
            cv2.imshow("OCR Vision - Align this with your Rune Popup", frame)
            
            # Check for 'q' key to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    live_calibration()