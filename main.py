import mss
import time
import pygetwindow as gw
from PIL import Image
from ocr_engine import extract_text
from logic_engine import find_and_decide, parse_rune_text, play_alert
from config import JSON_FILE

def get_sw_window():
    """
    Pronalazi koordinate MuMu Player prozora koristeći logiku iz kalibracije.
    """
    try:
        all_windows = gw.getAllWindows()
        # Lista ključnih reči koja provereno radi u calibrate.py
        possible_titles = ["MUMU", "ANDROID DEVICE", "SUMMONERS WAR"]
        
        for win in all_windows:
            title_upper = win.title.upper()
            if any(p_title in title_upper for p_title in possible_titles):
                if win.isMinimized:
                    return None
                
                # Provera da li prozor ima validnu veličinu (da ne uhvati neki sistemski proces)
                if win.width > 200 and win.height > 200:
                    return {
                        'top': win.top,
                        'left': win.left,
                        'width': win.width,
                        'height': win.height
                    }
    except Exception as e:
        print(f"Greška pri traženju prozora: {e}")
    return None

def start_scanner():
    last_rune_id = None
    window_found = False
    
    print("\n--- MuMu Player G1 Scanner Aktivan ---")
    
    with mss.mss() as sct:
        while True:
            region = get_sw_window()
            
            if region:
                if not window_found:
                    print(f"Prozor pronađen! Lokacija: {region['left']}, {region['top']}")
                    window_found = True

                # Slikamo tačno definisan region emulatora
                try:
                    screenshot = sct.grab(region)
                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                    
                    raw_text = extract_text(img).strip()
                    
                    # Provera da li na ekranu ima dovoljno teksta za runu
                    if len(raw_text) > 15:
                        rune_info = parse_rune_text(raw_text)
                        
                        if rune_info["set"] and rune_info["slot"]:
                            # ID se pravi od seta, slota i svih substatova radi 100% preciznosti
                            current_id = f"{rune_info['set']}_{rune_info['slot']}_{sum(rune_info['values'])}"
                            
                            if current_id != last_rune_id:
                                # Pozivamo logiku koja proverava JSON
                                eff, decision = find_and_decide(rune_info, JSON_FILE)
                                
                                if eff is not None:
                                    print("-" * 30)
                                    print(f"[ {rune_info['set'].upper()} Slot {rune_info['slot']} ]")
                                    print(f"Efikasnost: {eff}%")
                                    print(f"ODLUKA: {decision}")
                                    print("-" * 30)
                                    
                                    play_alert(decision)
                                    last_rune_id = current_id 
                    else:
                        # Resetujemo ID čim sklonimo miša sa rune (prazan prostor)
                        last_rune_id = None
                        
                except Exception as e:
                    print(f"Greška tokom skeniranja: {e}")
                    
            else:
                if window_found:
                    print("\nIzgubljen kontakt sa prozorom!")
                    window_found = False
                print("Tražim prozor (Proveri da li je MuMu otvoren i terminal pokrenut kao Admin)...", end='\r')
            
            # Pauza da ne opterećujemo procesor
            time.sleep(0.4)

if __name__ == "__main__":
    try:
        start_scanner()
    except KeyboardInterrupt:
        print("\n\nSkener ugašen korisničkom komandom.")
    except Exception as e:
        print(f"\nKritična greška: {e}")