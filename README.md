# Summoners War G1 Rune Scanner (Steam Version)

A Python-based tool that uses OCR to scan runes in real-time from the Steam version of Summoners War, calculates their efficiency based on G1 standards, and provides audio feedback (Keep/Sell).

## Features
- **Window Tracking:** Automatically attaches to the "Summoners War" Steam window.
- **OCR Engine:** Uses Tesseract to read rune sets, slots, and substats.
- **Smart Matching:** Matches screen data with your exported JSON to ensure 100% accuracy.
- **Audio Alerts:** High-pitch beep for KEEP, Low-pitch for SELL.
- **Efficiency Logic:** Uses G1-tier formulas including speed-check overrides.

## Setup
1. Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki).
2. Clone the repo: `git clone https://github.com/TVOJ-PROFIL/sw-rune-scanner.git`
3. Install dependencies: `pip install -r requirements.txt`
4. Place your SW Exporter JSON in the root folder.
5. Update `config.py` with your JSON filename.

## Usage
Run `python main.py` and hover over runes in-game.