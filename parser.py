import re

def parse_rune_text(text):
    # Dictionary to store what we find
    rune_data = {
        "set": None,
        "slot": None,
        "main_stat": None,
        "substats": []
    }
    
    # Common SW Sets to look for
    sets = ["Fatal", "Swift", "Violent", "Will", "Despair", "Blade", "Rage"]
    for s in sets:
        if s.lower() in text.lower():
            rune_data["set"] = s
            break
            
    # Look for the Slot number, usually in format (3) or (6)
    slot_match = re.search(r'\((\d)\)', text)
    if slot_match:
        rune_data["slot"] = slot_match.group(1)

    # Look for stats (Percentage or Flat)
    # This regex looks for things like "DEF +29" or "CRI Dmg +2%"
    stat_pattern = r'([a-zA-Z\s]+)\s?\+(\d+)?%?'
    matches = re.findall(stat_pattern, text)
    
    for label, value in matches:
        label = label.strip()
        if label and value:
            # First stat found is usually the main stat
            if not rune_data["main_stat"]:
                rune_data["main_stat"] = {"label": label, "value": value}
            else:
                rune_data["substats"].append({"label": label, "value": value})

    return rune_data

# Test it
if __name__ == "__main__":
    sample = "Fatal Rune (3) - Rare DEF +29 CRI Dmg +2%"
    print(parse_rune_text(sample))