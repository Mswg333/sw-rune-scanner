import cv2
import numpy as np
from PIL import Image
import pytesseract

def preprocess_for_ocr(img):
    # Convert to grayscale and increase contrast
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    # Binary threshold makes text pop against the dark SW background
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    return thresh

def extract_text(image):
    processed_img = preprocess_for_ocr(image)
    # PSM 6 is optimized for uniform blocks of text
    text = pytesseract.image_to_string(processed_img, config='--psm 6')
    return text