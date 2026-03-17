import mss
import time
import pygetwindow as gw
from PIL import Image
from ocr_engine import extract_text
from logic_engine import find_and_decide, parse_rune_text, play_alert
from config import JSON_FILE

def get_sw_window():
    try:
        # Steam verzija obično ima naslov "Summoners War"
        # Tražimo bilo koji prozor koji sadrži to ime
        windows = gw.getWindowsWithTitle("Summoners War")
        if windows:
            win = windows[0]
            # Vraćamo samo regiju gde je prozor
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
    print("--- Steam G1 Scanner Aktivan ---")
    print("Tražim Summoners War prozor...")
    
    with mss.mss() as sct:
        while True:
            region = get_sw_window()
            
            if region:
                # Slikamo samo Summoners War prozor
                screenshot = sct.grab(region)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                raw_text = extract_text(img).strip()
                
                # Ako vidimo dovoljno teksta, krećemo u analizu
                if len(raw_text) > 15:
                    rune_info = parse_rune_text(raw_text)
                    
                    if rune_info["set"] and rune_info["slot"]:
                        current_id = f"{rune_info['set']}_{rune_info['slot']}"
                        
                        if current_id != last_rune_id:
                            eff, decision = find_and_decide(rune_info, JSON_FILE)
                            
                            if eff is not None:
                                print(f"\n[ {rune_info['set']} Slot {rune_info['slot']} ]")
                                print(f"Efikasnost: {eff}% | Odluka: {decision}")
                                play_alert(decision)
                                last_rune_id = current_id 
                else:
                    # Resetujemo id ako sklonimo miša sa rune
                    last_rune_id = None
            else:
                print("Summoners War (Steam) nije pronađen. Otvori igru!", end='\r')
            
            time.sleep(0.5)

if __name__ == "__main__":
    try:
        start_scanner()
    except KeyboardInterrupt:
        print("\nSkener ugašen.")