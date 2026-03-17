import pytesseract
import os

# 1. Tesseract Path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 2. JSON Filename
JSON_FILE = '~VolimKaleta~-8031166.json'

# 3. Scaling Logic (Centered 40% of screen)
BASE_WIDTH = 1920 
BASE_HEIGHT = 1080
SCALE = 0.4 

width = int(BASE_WIDTH * SCALE)
height = int(BASE_HEIGHT * SCALE)
left = int((BASE_WIDTH - width) / 2)
top = int((BASE_HEIGHT - height) / 2)

MONITOR_REGION = {
    'top': 100,    # Move up to catch the top of the rune card
    'left': 550,   # Move right to align with the popup
    'width': 600,  # Wide enough for the stats
    'height': 700  # Tall enough for all substats
}