import math
from collections import Counter

# ==========================================
# 1. JOUW LAYOUT CONFIGURATIE
# ==========================================
# Vul hier jouw layout in (kleine letters).
# Gebruik tekens die op een standaard toetsenbord staan.
# Voorbeeld is QWERTY. Pas dit aan naar jouw eigen layout!

#oud
# row_top    = "qwfpbjluy;" 
# row_home   = "arstgmneio'"
# row_bottom = "\zxcvdkh,./"

#nieuwe
row_top    = "qwvpbjluy;" 
row_home   = "aretgsnido'"
row_bottom = "\zxcfmkh,./"

# Naam van je tekstbestand met de dataset (zorg dat dit bestand in dezelfde map staat)
DATASET_BESTAND = "input.txt" 

# ==========================================
# 2. CONFIGURATIE VAN VINGERS (Standaard Touch Typing)
# ==========================================
# Dit bepaalt welke kolom bij welke vinger hoort.
# 0=Pinky L, 1=Ring L, 2=Middle L, 3=Index L, 4=Index L (inner)
# 5=Index R (inner), 6=Index R, 7=Middle R, 8=Ring R, 9=Pinky R
finger_map = [0, 1, 2, 3, 3, 6, 6, 7, 8, 9, 9, 9] # Extra 9's voor brede layouts

def get_finger_hand(col_index):
    # Geeft terug: (vinger_id, hand_kant)
    # Vinger ID: 0-3 (Pinky-Index)
    # Hand: 'L' of 'R'
    
    # Simpele mapping voor standaard borden
    if col_index > len(finger_map) - 1:
        f_val = 9 # Fallback naar rechter pink
    else:
        f_val = finger_map[col_index]
        
    if f_val < 5:
        return f_val, 'L' # 0=Pinky, 1=Ring, 2=Mid, 3=Index
    else:
        return (9 - f_val), 'R' # 0=Pinky, 1=Ring, 2=Mid, 3=Index

# ==========================================
# 3. DE ANALYSE LOGICA
# ==========================================

def analyze_layout():
    # 1. Bouw de lookup table voor de layout
    key_map = {} # char -> (row, col, finger, hand)
    
    rows = [row_top, row_home, row_bottom]
    
    print("--- Layout wordt geladen ---")
    for r_idx, row_str in enumerate(rows):
        for c_idx, char in enumerate(row_str):
            finger, hand = get_finger_hand(c_idx)
            # Row 1 (index 1) is home row. 
            # We slaan op: (rij_index, kolom_index, vinger, hand)
            key_map[char] = (r_idx, c_idx, finger, hand)
            print(f"Toets '{char}' -> Rij {r_idx}, Vinger {finger}, Hand {hand}")

    print("\n--- Analyse start op dataset ---")
    
    try:
        with open(DATASET_BESTAND, 'r', encoding='utf-8') as f:
            text = f.read().lower()
    except FileNotFoundError:
        print(f"FOUT: Kan bestand '{DATASET_BESTAND}' niet vinden.")
        return

    # Statistieken tellers
    total_chars = 0
    home_row_count = 0
    hand_count = {'L': 0, 'R': 0}
    sfb_count = 0 # Same Finger Bigram
    distance_score = 0
    
    # Filter tekst zodat we alleen karakters hebben die in de layout staan
    clean_text = [c for c in text if c in key_map]
    total_chars = len(clean_text)

    if total_chars == 0:
        print("Geen geldige karakters gevonden in dataset die matchen met layout.")
        return

    # Loop door de tekst
    for i in range(total_chars):
        current_char = clean_text[i]
        cur_r, cur_c, cur_f, cur_h = key_map[current_char]
        
        # 1. Hand Balance
        hand_count[cur_h] += 1
        
        # 2. Home Row Usage (Rij index 1 is home row)
        if cur_r == 1:
            home_row_count += 1
            
        # 3. Distance (Versimpeld: afstand tot (1, 3) en (1, 6) - de rustposities)
        # We straffen verticale beweging zwaarder
        base_row = 1
        dist = abs(cur_r - base_row) * 1.5 
        if cur_r == 1 and (cur_c == 3 or cur_c == 6):
            dist = 0 # Rustpositie kost niks
        distance_score += dist

        # 4. Same Finger Bigram (SFB)
        if i < total_chars - 1:
            next_char = clean_text[i+1]
            if next_char != current_char: # Herhalen van letter (aa) tellen we vaak niet als SFB straf
                nxt_r, nxt_c, nxt_f, nxt_h = key_map[next_char]
                
                # Als hand hetzelfde is EN vinger hetzelfde
                if cur_h == nxt_h and cur_f == nxt_f:
                    sfb_count += 1

    # ==========================================
    # 4. RESULTATEN PRINTEN
    # ==========================================
    print("\n" + "="*40)
    print(f"RESULTATEN VOOR JOUW LAYOUT")
    print("="*40)
    
    # SFB
    sfb_percentage = (sfb_count / total_chars) * 100
    print(f"SFB (Same Finger Bigram): {sfb_percentage:.2f}%")
    print("  -> Doel: < 1.5% is excellent, > 5% is slecht.")
    
    # Home Row
    home_row_percentage = (home_row_count / total_chars) * 100
    print(f"Home Row Usage:           {home_row_percentage:.2f}%")
    print("  -> Doel: Hoe hoger hoe beter (vaak > 50-60%).")
    
    # Hand Balance
    left_p = (hand_count['L'] / total_chars) * 100
    right_p = (hand_count['R'] / total_chars) * 100
    print(f"Hand Balans (L / R):      {left_p:.1f}% / {right_p:.1f}%")
    print("  -> Doel: Zo dicht mogelijk bij 50/50.")
    
    # Distance
    avg_dist = distance_score / total_chars
    print(f"Distance Score (avg):     {avg_dist:.2f}")
    print("  -> Doel: Zo laag mogelijk.")

if __name__ == "__main__":
    analyze_layout()