import json
import re
import winsound

# Globalne mape i keš
_cached_data = None
MAX_ROLLS = {1: 375, 2: 8, 3: 100, 4: 8, 5: 100, 6: 8, 8: 6, 9: 6, 10: 7, 11: 8, 12: 8}
SET_MAP = {1: "Energy", 2: "Guard", 3: "Swift", 4: "Fatal", 5: "Blade", 6: "Rage", 7: "Focus", 8: "Endure", 10: "Vampire", 13: "Violent", 14: "Will", 15: "Nemesis", 16: "Shield", 17: "Revenge", 18: "Despair", 21: "Fight"}

# G1 Težinski faktori (Vrednost statova za tvoj nivo)
G1_WEIGHTS = {
    "SPD": 1.5, "CR": 1.1, "CD": 1.1, "ATK%": 1.0, "HP%": 1.0, "DEF%": 1.0, "ACC": 0.7, "RES": 0.5
}

def load_json_once(json_file):
    global _cached_data
    if _cached_data is None:
        with open(json_file, 'r', encoding='utf-8', errors='ignore') as f:
            _cached_data = json.load(f)
    return _cached_data

def get_account_benchmarks(data):
    """Računa prosek tvojih top 15 čudovišta (G1 Benchmark)."""
    units = data.get('unit_list', [])
    # Filtriramo samo 6* lvl 40 jedinice (tvoj core tim)
    top_units = sorted([u for u in units if u.get('unit_level') == 40], 
                       key=lambda x: x.get('con_eff', 0), reverse=True)[:15]
    
    if not top_units: return 85.0 # Default G1 prag ako je nalog prazan
    return sum(u.get('con_eff', 0) / 100 for u in top_units) / len(top_units)

def proveri_unapredjenje_naloga(rune, eff, spd, data):
    upgrade = rune.get('upgrade_curr', 0)
    set_id = rune.get('set_id')
    
    if upgrade < 9: return None

    # 1. SWOP BODOVANJE (Sinergija statova)
    score = 0
    sec_eff = rune.get('sec_eff', [])
    for s in sec_eff:
        val = s[1] + s[3] # Base + Grind
        if s[0] == 8: score += val * G1_WEIGHTS["SPD"]
        elif s[0] == 9: score += val * G1_WEIGHTS["CR"]
        elif s[0] == 10: score += val * G1_WEIGHTS["CD"]
        elif s[0] in [2, 4, 6]: score += val * 1.0 # Procenti

    # 2. DYNAMIC THRESHOLD (Poređenje sa tvojim nalogom)
    acc_avg = get_account_benchmarks(data)
    
    # Projektovana efikasnost za +9 rune
    potential_eff = eff + (1.6 if upgrade == 9 else 0)

    # 3. G1 FILTRACIJA
    # Ako je SPD ekstremno visok (G1-G3 range), uvek KEEP
    if spd >= 22: return f"KEEP (GOD SPD: {spd})"

    # Ako runa ne dostiže 95% proseka tvog top 15 tima -> SELL
    if potential_eff < (acc_avg * 0.95):
        return f"SELL (Low Potential: {potential_eff:.1f}%)"

    # Provera sinergije za specifične setove
    if set_id == 6: # Rage
        has_dmg = any(s[0] in [9, 10] for s in sec_eff)
        if not has_dmg: return "SELL (Rage No Synergy)"

    return f"KEEP (Score: {score:.1f})"

def find_and_decide(ocr_data, json_file):
    data = load_json_once(json_file)
    runes = data.get('runes', [])
    
    det_set = ocr_data.get("set")
    det_slot = str(ocr_data.get("slot"))
    det_values = ocr_data.get("values", [])

    if not det_set or not det_slot: return None, None

    for r in runes:
        if str(r['slot_no']) == det_slot:
            # Koristimo SET_MAP koji je sada sigurno definisan globalno
            if SET_MAP.get(r['set_id'], "").lower() == det_set.lower():
                json_vals = [s[1] + s[3] for s in r.get('sec_eff', [])]
                if len(set(det_values).intersection(set(json_vals))) >= 2:
                    
                    # Efikasnost i Speed
                    current_sum = sum((s[1] + s[3]) / MAX_ROLLS[s[0]] for s in r.get('sec_eff', []) if s[0] in MAX_ROLLS)
                    eff = round(((current_sum + 1) / 5) * 100, 2)
                    spd = next((s[1] + s[3] for s in r.get('sec_eff', []) if s[0] == 8), 0)
                    
                    decision = proveri_unapredjenje_naloga(r, eff, spd, data)
                    return eff, decision
    return None, None

def parse_rune_text(text):
    if not text: return {"set": None, "slot": None, "values": []}
    lines = text.split('\n')
    substats = []
    for line in lines:
        clean = re.sub(r'[^0-9+]', '', line)
        if "+" in clean:
            match = re.search(r'\+(\d+)', clean)
            if match:
                val = int(match.group(1))
                if val < 500: substats.append(val)
    
    det_set = next((s for s in SET_MAP.values() if s.lower() in text.lower()), None)
    slot_match = re.search(r'\((\d)\)', text)
    return {"set": det_set, "slot": slot_match.group(1) if slot_match else None, "values": sorted(substats)}

def play_alert(decision):
    if decision and "KEEP" in decision: winsound.Beep(1000, 250)
    elif decision: winsound.Beep(400, 200)