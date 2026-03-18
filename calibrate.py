import mss
import pygetwindow as gw
from PIL import Image
import os

def get_sw_window():
    try:
        # Tražimo prozor - koristi isti naziv kao u main.py
        all_windows = gw.getAllWindows()
        for win in all_windows:
            title = win.title.upper()
            if any(key in title for key in ["MUMU", "ANDROID DEVICE", "SUMMONERS"]):
                if win.isMinimized:
                    print("Prozor je minimizovan!")
                    return None
                return {
                    'top': win.top,
                    'left': win.left,
                    'width': win.width,
                    'height': win.height
                }
    except Exception as e:
        print(f"Greška: {e}")
    return None

def calibrate():
    region = get_sw_window()
    
    if not region:
        print("Greška: Ne mogu da pronađem MuMu prozor. Proveri da li je otvoren i da li terminal ima Admin prava.")
        return

    with mss.mss() as sct:
        print(f"Hvatanje prozora na lokaciji: {region}")
        # Uzimamo screenshot samo tog dela ekrana
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        # Čuvamo sliku da proveriš šta skener zapravo vidi
        img.save("calibration_check.png")
        print("Uspešno! Otvori fajl 'calibration_check.png' u folderu.")
        print("Ako je na slici igra, skener je spreman. Ako je slika crna ili pogrešna, proveri Scaling u Windows-u (mora biti 100%).")

if __name__ == "__main__":
    calibrate()