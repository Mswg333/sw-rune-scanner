import json
import winsound
import re

_cached_data = None

SET_MAP = {
    1: "Energy", 2: "Guard", 3: "Swift", 4: "Fatal", 5: "Blade", 
    6: "Rage", 7: "Focus", 8: "Endure", 10: "Vampire", 13: "Violent", 
    14: "Will", 15: "Nemesis", 16: "Shield", 17: "Revenge", 18: "Despair"
}

def load_json_once(json_file):
    global _cached_data
    if _cached_data is None:
        with open(json_file, 'r', encoding='utf-8', errors='ignore') as f:
            _cached_data = json.load(f)
    return _cached_data

def play_alert(decision):
    if decision == "KEEP":
        winsound.Beep(1200, 400)
    else:
        winsound.Beep(300, 200)

def parse_rune_text(text):
    # Izvlači brojeve iz teksta (npr. +20, +46...)
    numbers = re.findall(r'\+(\d+)', text)
    rune_data = {
        "set": None, 
        "slot": None, 
        "values": [int(n) for n in numbers if int(n) < 500] # ignorišemo velike ID brojeve
    }
    
    sets = ["Fatal", "Swift", "Violent", "Will", "Despair", "Blade", "Rage", "Energy", "Shield", "Revenge"]
    for s in sets:
        if s.lower() in text.lower():
            rune_data["set"] = s
            break
            
    slot_match = re.search(r'\((\d)\)', text)
    if slot_match:
        rune_data["slot"] = slot_match.group(1)
    
    return rune_data

def calculate_efficiency(rune):
    max_rolls = {1: 375, 2: 40, 3: 100, 4: 40, 5: 100, 6: 40, 8: 30, 9: 30, 10: 35, 11: 40, 12: 40}
    current_sum = 0
    for stat in rune.get('sec_eff', []):
        stat_type, stat_value = stat[0], stat[1] + stat[3]
        if stat_type in max_rolls:
            current_sum += (stat_value / max_rolls[stat_type])
    return round(((current_sum + 1) / 5) * 100, 2)

def find_and_decide(ocr_data, json_file):
    data = load_json_once(json_file)
    runes = data.get('runes', [])
    
    det_set = ocr_data.get("set")
    det_slot = str(ocr_data.get("slot"))
    det_values = ocr_data.get("values", [])

    candidates = []

    for r in runes:
        if str(r['slot_no']) == det_slot:
            rune_set_name = SET_MAP.get(r['set_id'], "Unknown")
            
            if rune_set_name.lower() == det_set.lower():
                # Uzmi vrednosti iz JSON-a
                json_values = [s[1] + s[3] for s in r.get('sec_eff', [])]
                
                # Proveri koliko se brojeva poklapa
                matches = len(set(det_values) & set(json_values))
                eff = calculate_efficiency(r)
                
                # Ako se poklapaju bar 2 broja, to je 99% ta runa
                if matches >= 2:
                    has_high_spd = any(s[0] == 8 and (s[1]+s[3]) >= 18 for s in r.get('sec_eff', []))
                    decision = "KEEP" if (eff >= 85 or has_high_spd) else "SELL"
                    return eff, decision
                
                # Ako se brojevi ne poklapaju (loš OCR), dodajemo je u listu kandidata
                candidates.append((eff, r))

    # Ako nismo našli savršen meč po brojevima, uzmi najjaču takvu runu koju imaš
    if candidates:
        # Sortiraj po efikasnosti i uzmi najbolju
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_eff, best_rune = candidates[0]
        
        has_high_spd = any(s[0] == 8 and (s[1]+s[3]) >= 18 for s in best_rune.get('sec_eff', []))
        decision = "KEEP" if (best_eff >= 80 or has_high_spd) else "SELL"
        return best_eff, decision
            
    return None, None