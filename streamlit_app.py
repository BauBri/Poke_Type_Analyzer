"""
Pokemon Team Defensive Coverage Analyzer
Smogon 1v1 Rules - Type-only analysis (MVP)
"""

import streamlit as st
import requests
import pandas as pd
from typing import Dict, List, Tuple, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Pokémon Team Coverage Analyzer",
    page_icon="https://play.pokemonshowdown.com/sprites/itemicons/master-ball.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# ITEM SPRITES URLs (Pokémon Showdown)
# =============================================================================

SPRITES = {
    "master_ball": "https://play.pokemonshowdown.com/sprites/itemicons/master-ball.png",
    "poke_ball": "https://play.pokemonshowdown.com/sprites/itemicons/poke-ball.png",
    "ultra_ball": "https://play.pokemonshowdown.com/sprites/itemicons/ultra-ball.png",
    "great_ball": "https://play.pokemonshowdown.com/sprites/itemicons/great-ball.png",
    "luxury_ball": "https://play.pokemonshowdown.com/sprites/itemicons/luxury-ball.png",
    "premier_ball": "https://play.pokemonshowdown.com/sprites/itemicons/premier-ball.png",
    "search": "https://play.pokemonshowdown.com/sprites/itemicons/scope-lens.png",
    "team": "https://play.pokemonshowdown.com/sprites/itemicons/exp-share.png",
    "warning": "https://play.pokemonshowdown.com/sprites/itemicons/flame-orb.png",
    "shield": "https://play.pokemonshowdown.com/sprites/itemicons/metal-coat.png",
    "pokeball_icon": "https://play.pokemonshowdown.com/sprites/itemicons/poke-ball.png",
    "remove": "https://play.pokemonshowdown.com/sprites/itemicons/eject-button.png",
    "clear": "https://play.pokemonshowdown.com/sprites/itemicons/destiny-knot.png",
    "add": "https://play.pokemonshowdown.com/sprites/itemicons/lucky-egg.png",
    "chart": "https://play.pokemonshowdown.com/sprites/itemicons/expert-belt.png",
}

# =============================================================================
# TYPE CHART - All 18 types effectiveness multipliers
# TYPE_CHART[attack_type][defense_type] = multiplier
# =============================================================================

TYPES = [
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug",
    "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"
]

TYPE_CHART: Dict[str, Dict[str, float]] = {
    "Normal":   {"Normal": 1, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 1, "Fighting": 1, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 1, "Bug": 1, "Rock": 0.5, "Ghost": 0, "Dragon": 1, "Dark": 1, "Steel": 0.5, "Fairy": 1},
    "Fire":     {"Normal": 1, "Fire": 0.5, "Water": 0.5, "Electric": 1, "Grass": 2, "Ice": 2, "Fighting": 1, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 1, "Bug": 2, "Rock": 0.5, "Ghost": 1, "Dragon": 0.5, "Dark": 1, "Steel": 2, "Fairy": 1},
    "Water":    {"Normal": 1, "Fire": 2, "Water": 0.5, "Electric": 1, "Grass": 0.5, "Ice": 1, "Fighting": 1, "Poison": 1, "Ground": 2, "Flying": 1, "Psychic": 1, "Bug": 1, "Rock": 2, "Ghost": 1, "Dragon": 0.5, "Dark": 1, "Steel": 1, "Fairy": 1},
    "Electric": {"Normal": 1, "Fire": 1, "Water": 2, "Electric": 0.5, "Grass": 0.5, "Ice": 1, "Fighting": 1, "Poison": 1, "Ground": 0, "Flying": 2, "Psychic": 1, "Bug": 1, "Rock": 1, "Ghost": 1, "Dragon": 0.5, "Dark": 1, "Steel": 1, "Fairy": 1},
    "Grass":    {"Normal": 1, "Fire": 0.5, "Water": 2, "Electric": 1, "Grass": 0.5, "Ice": 1, "Fighting": 1, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Psychic": 1, "Bug": 0.5, "Rock": 2, "Ghost": 1, "Dragon": 0.5, "Dark": 1, "Steel": 0.5, "Fairy": 1},
    "Ice":      {"Normal": 1, "Fire": 0.5, "Water": 0.5, "Electric": 1, "Grass": 2, "Ice": 0.5, "Fighting": 1, "Poison": 1, "Ground": 2, "Flying": 2, "Psychic": 1, "Bug": 1, "Rock": 1, "Ghost": 1, "Dragon": 2, "Dark": 1, "Steel": 0.5, "Fairy": 1},
    "Fighting": {"Normal": 2, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 2, "Fighting": 1, "Poison": 0.5, "Ground": 1, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0, "Dragon": 1, "Dark": 2, "Steel": 2, "Fairy": 0.5},
    "Poison":   {"Normal": 1, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 2, "Ice": 1, "Fighting": 1, "Poison": 0.5, "Ground": 0.5, "Flying": 1, "Psychic": 1, "Bug": 1, "Rock": 0.5, "Ghost": 0.5, "Dragon": 1, "Dark": 1, "Steel": 0, "Fairy": 2},
    "Ground":   {"Normal": 1, "Fire": 2, "Water": 1, "Electric": 2, "Grass": 0.5, "Ice": 1, "Fighting": 1, "Poison": 2, "Ground": 1, "Flying": 0, "Psychic": 1, "Bug": 0.5, "Rock": 2, "Ghost": 1, "Dragon": 1, "Dark": 1, "Steel": 2, "Fairy": 1},
    "Flying":   {"Normal": 1, "Fire": 1, "Water": 1, "Electric": 0.5, "Grass": 2, "Ice": 1, "Fighting": 2, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 1, "Bug": 2, "Rock": 0.5, "Ghost": 1, "Dragon": 1, "Dark": 1, "Steel": 0.5, "Fairy": 1},
    "Psychic":  {"Normal": 1, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 1, "Fighting": 2, "Poison": 2, "Ground": 1, "Flying": 1, "Psychic": 0.5, "Bug": 1, "Rock": 1, "Ghost": 1, "Dragon": 1, "Dark": 0, "Steel": 0.5, "Fairy": 1},
    "Bug":      {"Normal": 1, "Fire": 0.5, "Water": 1, "Electric": 1, "Grass": 2, "Ice": 1, "Fighting": 0.5, "Poison": 0.5, "Ground": 1, "Flying": 0.5, "Psychic": 2, "Bug": 1, "Rock": 1, "Ghost": 0.5, "Dragon": 1, "Dark": 2, "Steel": 0.5, "Fairy": 0.5},
    "Rock":     {"Normal": 1, "Fire": 2, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 2, "Fighting": 0.5, "Poison": 1, "Ground": 0.5, "Flying": 2, "Psychic": 1, "Bug": 2, "Rock": 1, "Ghost": 1, "Dragon": 1, "Dark": 1, "Steel": 0.5, "Fairy": 1},
    "Ghost":    {"Normal": 0, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 1, "Fighting": 1, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 2, "Bug": 1, "Rock": 1, "Ghost": 2, "Dragon": 1, "Dark": 0.5, "Steel": 1, "Fairy": 1},
    "Dragon":   {"Normal": 1, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 1, "Fighting": 1, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 1, "Bug": 1, "Rock": 1, "Ghost": 1, "Dragon": 2, "Dark": 1, "Steel": 0.5, "Fairy": 0},
    "Dark":     {"Normal": 1, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 1, "Fighting": 0.5, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 2, "Bug": 1, "Rock": 1, "Ghost": 2, "Dragon": 1, "Dark": 0.5, "Steel": 1, "Fairy": 0.5},
    "Steel":    {"Normal": 1, "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Grass": 1, "Ice": 2, "Fighting": 1, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 1, "Bug": 1, "Rock": 2, "Ghost": 1, "Dragon": 1, "Dark": 1, "Steel": 0.5, "Fairy": 2},
    "Fairy":    {"Normal": 1, "Fire": 0.5, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 1, "Fighting": 2, "Poison": 0.5, "Ground": 1, "Flying": 1, "Psychic": 1, "Bug": 1, "Rock": 1, "Ghost": 1, "Dragon": 2, "Dark": 2, "Steel": 0.5, "Fairy": 1},
}

# =============================================================================
# POKEMON DATABASE - Loaded from Pokemon Showdown's Pokedex
# =============================================================================

@st.cache_data(ttl=86400)  # Cache for 24 hours
def load_all_pokemon() -> Dict[str, Dict]:
    """
    Load all Pokemon from Pokemon Showdown's pokedex.
    Includes all forms, megas, regionals, etc.
    """
    import requests
    
    try:
        response = requests.get(
            "https://play.pokemonshowdown.com/data/pokedex.json",
            timeout=30
        )
        response.raise_for_status()
        pokedex = response.json()
    except Exception as e:
        st.error(f"Failed to load Pokemon data: {e}")
        return {}
    
    pokemon_dict = {}
    
    for pokemon_id, data in pokedex.items():
        # Skip if no types (not a real Pokemon)
        if "types" not in data:
            continue
        
        # Skip all non-standard Pokemon (CAP, LGPE, etc.)
        nonstandard = data.get("isNonstandard")
        if nonstandard and nonstandard not in ["Past", "Unobtainable"]:
            continue
        
        # Get the number/generation
        num = data.get("num", 0)
        
        # Skip if num is 0 or negative (not real Pokemon) except for some special cases
        if num <= 0:
            continue
        
        # Determine generation based on dex number
        if num <= 151:
            gen = 1
        elif num <= 251:
            gen = 2
        elif num <= 386:
            gen = 3
        elif num <= 493:
            gen = 4
        elif num <= 649:
            gen = 5
        elif num <= 721:
            gen = 6
        elif num <= 809:
            gen = 7
        elif num <= 905:
            gen = 8
        else:
            gen = 9
        
        # Handle forme/form naming
        name = data.get("name", pokemon_id.title())
        base_species = data.get("baseSpecies", "")
        forme = data.get("forme", "")
        
        # Determine form type for categorization
        form_type = "base"
        if "mega" in pokemon_id.lower() or forme.lower().startswith("mega"):
            form_type = "mega"
            gen = 6  # Megas are Gen 6
        elif "gmax" in pokemon_id.lower() or forme.lower() == "gmax":
            form_type = "gmax"
            gen = 8
        elif "alola" in pokemon_id.lower() or forme.lower() == "alola":
            form_type = "alola"
            gen = 7
        elif "galar" in pokemon_id.lower() or forme.lower() == "galar":
            form_type = "galar"
            gen = 8
        elif "hisui" in pokemon_id.lower() or forme.lower() == "hisui":
            form_type = "hisui"
            gen = 8
        elif "paldea" in pokemon_id.lower() or forme.lower() == "paldea":
            form_type = "paldea"
            gen = 9
        elif forme:
            form_type = "form"
        
        pokemon_dict[pokemon_id] = {
            "name": name,
            "types": data.get("types", []),
            "showdown_id": pokemon_id,
            "num": num,
            "gen": gen,
            "form_type": form_type,
            "base_species": base_species if base_species else name,
            "forme": forme,
        }
    
    return pokemon_dict


def get_pokemon_by_generation(pokemon_dict: Dict[str, Dict]) -> Dict[str, List[Tuple[str, str]]]:
    """
    Organize Pokemon by generation for the selector.
    Returns dict with gen keys and list of (pokemon_id, display_name) tuples.
    """
    generations = {
        "Gen 1 - Kanto": [],
        "Gen 2 - Johto": [],
        "Gen 3 - Hoenn": [],
        "Gen 4 - Sinnoh": [],
        "Gen 5 - Unova": [],
        "Gen 6 - Kalos": [],
        "Gen 7 - Alola": [],
        "Gen 8 - Galar/Hisui": [],
        "Gen 9 - Paldea": [],
    }
    
    gen_map = {
        1: "Gen 1 - Kanto",
        2: "Gen 2 - Johto",
        3: "Gen 3 - Hoenn",
        4: "Gen 4 - Sinnoh",
        5: "Gen 5 - Unova",
        6: "Gen 6 - Kalos",
        7: "Gen 7 - Alola",
        8: "Gen 8 - Galar/Hisui",
        9: "Gen 9 - Paldea",
    }
    
    for pokemon_id, data in pokemon_dict.items():
        gen = data.get("gen", 1)
        gen_key = gen_map.get(gen, "Gen 1 - Kanto")
        generations[gen_key].append((pokemon_id, data["name"]))
    
    # Sort each generation by dex number then name
    for gen_key in generations:
        generations[gen_key].sort(key=lambda x: (pokemon_dict[x[0]]["num"], x[1]))
    
    return generations


# Load Pokemon data
POKEMON = load_all_pokemon()

# Type colors for badges
TYPE_COLORS: Dict[str, str] = {
    "Normal": "#A8A878", "Fire": "#F08030", "Water": "#6890F0", "Electric": "#F8D030",
    "Grass": "#78C850", "Ice": "#98D8D8", "Fighting": "#C03028", "Poison": "#A040A0",
    "Ground": "#E0C068", "Flying": "#A890F0", "Psychic": "#F85888", "Bug": "#A8B820",
    "Rock": "#B8A038", "Ghost": "#705898", "Dragon": "#7038F8", "Dark": "#705848",
    "Steel": "#B8B8D0", "Fairy": "#EE99AC"
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def normalize_sprite_id(showdown_id: str, pokemon_data: Dict = None) -> str:
    """
    Normalize the showdown ID for sprite URLs.
    Showdown sprites use hyphenated form names like 'pikachu-alola', 'charizard-megax'.
    But pokedex IDs are like 'pikachualola', 'charizardmegax'.
    """
    # If we have pokemon data, use base_species and forme to build proper sprite name
    if pokemon_data:
        base_species = pokemon_data.get("base_species", "")
        forme = pokemon_data.get("forme", "")
        
        if base_species and forme:
            # Convert base species to lowercase, remove special chars
            base_clean = base_species.lower().replace(" ", "").replace("-", "").replace("'", "").replace(".", "")
            forme_clean = forme.lower().replace(" ", "").replace("-", "").replace("'", "").replace(".", "")
            return f"{base_clean}-{forme_clean}"
    
    # Fallback: just return the showdown_id as-is
    return showdown_id.lower()


def get_sprite_html(showdown_id: str, pokemon_data: Dict = None, size: int = 48) -> str:
    """
    Generate HTML for a Pokemon sprite with fallback to base species.
    Tries specific form sprite first, falls back to base species if it fails.
    """
    # Get base species ID for fallback
    base_id = showdown_id.lower()
    
    if pokemon_data:
        base = pokemon_data.get("base_species", "")
        if base and base != pokemon_data.get("name", ""):
            base_id = base.lower().replace(" ", "").replace("-", "").replace("'", "").replace(".", "")
    
    # Try the specific form sprite first
    sprite_id = normalize_sprite_id(showdown_id, pokemon_data)
    primary_url = f"https://play.pokemonshowdown.com/sprites/gen5/{sprite_id}.png"
    
    # Fallback: base species
    fallback_url = f"https://play.pokemonshowdown.com/sprites/gen5/{base_id}.png"
    
    # Final fallback: pokeball
    final_fallback = "https://play.pokemonshowdown.com/sprites/itemicons/poke-ball.png"
    
    # onerror: try base species, then pokeball
    onerror = f"this.onerror=function(){{this.src='{final_fallback}'}};this.src='{fallback_url}'"
    
    return f'<img src="{primary_url}" onerror="{onerror}" style="width:{size}px;height:{size}px;object-fit:contain;">'


def get_base_species_id(pokemon_data: Dict) -> str:
    """Get the base species ID for fallback sprites."""
    if pokemon_data:
        base = pokemon_data.get("base_species", "")
        if base and base != pokemon_data.get("name", ""):
            return base.lower().replace(" ", "").replace("-", "").replace("'", "").replace(".", "")
    return ""


def calc_multiplier(attack_type: str, pokemon_types: List[str]) -> float:
    """Calculate damage multiplier for an attack type vs a Pokemon's types."""
    multiplier = 1.0
    for def_type in pokemon_types:
        multiplier *= TYPE_CHART[attack_type].get(def_type, 1.0)
    return multiplier


def summarize_team(team: List[str]) -> pd.DataFrame:
    """
    Generate a summary table of type effectiveness against the team.
    Returns DataFrame with columns for each multiplier count and risk score.
    """
    if not team:
        return pd.DataFrame()
    
    results = []
    
    for atk_type in TYPES:
        multipliers = []
        for pokemon_id in team:
            if pokemon_id in POKEMON:
                poke_types = POKEMON[pokemon_id]["types"]
                mult = calc_multiplier(atk_type, poke_types)
                multipliers.append(mult)
        
        # Count multipliers
        counts = {
            "x0": multipliers.count(0),
            "x0.25": multipliers.count(0.25),
            "x0.5": multipliers.count(0.5),
            "x1": multipliers.count(1),
            "x2": multipliers.count(2),
            "x4": multipliers.count(4),
        }
        
        # Calculate risk score
        risk = (counts["x2"] + 2 * counts["x4"] 
                - counts["x0.5"] - 2 * counts["x0.25"] - 3 * counts["x0"])
        
        worst = max(multipliers) if multipliers else 1
        best = min(multipliers) if multipliers else 1
        
        results.append({
            "Type": atk_type,
            "x0": counts["x0"],
            "x0.25": counts["x0.25"],
            "x0.5": counts["x0.5"],
            "x1": counts["x1"],
            "x2": counts["x2"],
            "x4": counts["x4"],
            "Worst": worst,
            "Best": best,
            "Risk": risk,
        })
    
    return pd.DataFrame(results)


def get_risk_color(risk: int) -> str:
    """Return color based on risk score."""
    if risk <= -3:
        return "#22c55e"
    elif risk <= -1:
        return "#86efac"
    elif risk <= 1:
        return "#fef08a"
    elif risk <= 3:
        return "#fca5a5"
    else:
        return "#ef4444"


# =============================================================================
# CUSTOM CSS
# =============================================================================

def inject_custom_css():
    """Inject custom CSS for styling."""
    st.markdown("""
    <style>
        /* Import arcade font */
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Bungee&display=swap');
        
        /* Main container */
        .main-header {
            text-align: center;
            padding: 1.5rem 0;
            border-bottom: 3px solid #3b82f6;
            margin-bottom: 1.5rem;
            background: linear-gradient(180deg, rgba(59,130,246,0.1) 0%, transparent 100%);
        }
        
        .main-header h1 {
            font-family: 'Bungee', 'Press Start 2P', cursive;
            font-size: 1.6rem;
            color: #ffcb05;
            text-shadow: 2px 2px 0 #3466af, 3px 3px 0 #2a5298, 4px 4px 8px rgba(0,0,0,0.5);
            letter-spacing: 2px;
            margin: 0;
        }
        
        .main-header p {
            font-family: 'Press Start 2P', cursive;
            font-size: 0.5rem;
            margin-top: 0.5rem;
        }
        
        .header-icon {
            width: 40px;
            height: 40px;
            vertical-align: middle;
            margin-right: 12px;
        }
        
        .section-icon {
            width: 20px;
            height: 20px;
            vertical-align: middle;
            margin-right: 6px;
        }
        
        /* Section headers with arcade font */
        .section-header {
            font-family: 'Press Start 2P', cursive;
            color: #f3f4f6;
            font-size: 0.65rem;
            font-weight: 700;
            padding: 0.75rem 0;
            border-bottom: 2px solid #3b82f6;
            margin-bottom: 1rem;
            letter-spacing: 1px;
        }
        
        /* Type badges */
        .type-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.55rem;
            font-weight: 700;
            color: white;
            margin: 2px;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.4);
            font-family: 'Press Start 2P', monospace;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        /* Empty slot placeholder */
        .empty-placeholder {
            width: 64px;
            height: 64px;
            border: 2px dashed #4b5563;
            border-radius: 50%;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: #6b7280;
        }
        
        /* Button icons */
        .btn-icon {
            width: 16px;
            height: 16px;
            vertical-align: middle;
            margin-right: 4px;
        }
        
        /* Table styling */
        .coverage-header {
            font-family: 'Press Start 2P', cursive;
            font-size: 0.45rem;
            color: #9ca3af;
            letter-spacing: 0.5px;
        }
        
        .stat-value {
            font-family: 'Press Start 2P', cursive;
            font-size: 0.65rem;
        }
        
        .rating-badge {
            font-family: 'Press Start 2P', cursive;
            font-size: 0.5rem;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 700;
        }
        
        /* Pokemon name in team details */
        .poke-name-arcade {
            font-family: 'Press Start 2P', cursive;
            font-size: 0.55rem;
            color: #fff;
        }
        
        /* Table headers for weakness/resistance */
        .table-header-arcade {
            font-family: 'Press Start 2P', cursive;
            font-size: 0.55rem;
            color: #fff;
            letter-spacing: 0.5px;
        }
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

def render_type_badge(type_name: str) -> str:
    """Render a type badge HTML."""
    color = TYPE_COLORS.get(type_name, "#888")
    return f'<span class="type-badge" style="background-color: {color};">{type_name}</span>'


def get_pokemon_weaknesses_resistances(pokemon_types: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """
    Calculate weaknesses, resistances and immunities for a Pokemon based on its types.
    Returns (weaknesses, resistances, immunities) as lists of type names.
    """
    weaknesses = []
    resistances = []
    immunities = []
    
    for atk_type in TYPES:
        mult = calc_multiplier(atk_type, pokemon_types)
        if mult == 0:
            immunities.append(atk_type)
        elif mult < 1:
            resistances.append(atk_type)
        elif mult > 1:
            weaknesses.append(atk_type)
    
    return weaknesses, resistances, immunities


def analyze_team_by_type(team: List[str]) -> List[Dict]:
    """
    Analyze team vulnerabilities by attacking type.
    Returns list of dicts with detailed type analysis data.
    """
    results = []
    team_size = len(team)
    
    for atk_type in TYPES:
        immune_count = 0      # x0
        resist_4x_count = 0   # x0.25
        resist_2x_count = 0   # x0.5
        neutral_count = 0     # x1
        weak_2x_count = 0     # x2
        weak_4x_count = 0     # x4
        
        for pokemon_id in team:
            if pokemon_id in POKEMON:
                poke_types = POKEMON[pokemon_id]["types"]
                mult = calc_multiplier(atk_type, poke_types)
                
                if mult == 0:
                    immune_count += 1
                elif mult == 0.25:
                    resist_4x_count += 1
                elif mult == 0.5:
                    resist_2x_count += 1
                elif mult == 1:
                    neutral_count += 1
                elif mult == 2:
                    weak_2x_count += 1
                elif mult >= 4:
                    weak_4x_count += 1
        
        # Calculate score for rating
        # Positive = good coverage, Negative = vulnerable
        defense_score = immune_count * 4 + resist_4x_count * 3 + resist_2x_count * 2
        offense_score = weak_2x_count * 2 + weak_4x_count * 4
        net_score = defense_score - offense_score
        
        # Rating system with more granularity
        # S+ to F scale
        if immune_count >= 2 or (immune_count >= 1 and resist_2x_count + resist_4x_count >= 2):
            rating = "S+"
            rating_color = "#22c55e"  # Bright green
        elif immune_count >= 1 and weak_2x_count == 0 and weak_4x_count == 0:
            rating = "S"
            rating_color = "#4ade80"  # Green
        elif net_score >= 6:
            rating = "A+"
            rating_color = "#86efac"  # Light green
        elif net_score >= 4:
            rating = "A"
            rating_color = "#a3e635"  # Lime
        elif net_score >= 2:
            rating = "B+"
            rating_color = "#bef264"  # Yellow-green
        elif net_score >= 0:
            rating = "B"
            rating_color = "#fde047"  # Yellow
        elif net_score >= -2:
            rating = "C+"
            rating_color = "#fbbf24"  # Amber
        elif net_score >= -4:
            rating = "C"
            rating_color = "#fb923c"  # Orange
        elif net_score >= -6:
            rating = "D"
            rating_color = "#f87171"  # Light red
        elif weak_4x_count >= 2 or (weak_4x_count >= 1 and weak_2x_count >= 2):
            rating = "F"
            rating_color = "#dc2626"  # Red
        else:
            rating = "E"
            rating_color = "#ef4444"  # Red
        
        results.append({
            "type": atk_type,
            "immune": immune_count,
            "resist_4x": resist_4x_count,
            "resist_2x": resist_2x_count,
            "neutral": neutral_count,
            "weak_2x": weak_2x_count,
            "weak_4x": weak_4x_count,
            "rating": rating,
            "rating_color": rating_color,
            "net_score": net_score
        })
    
    # Sort alphabetically by type name
    results.sort(key=lambda x: x["type"])
    
    return results


def render_coverage_table(team: List[str]):
    """Render a table showing type risk analysis for the team."""
    if not team:
        st.info("Add Pokemon to your team to see the analysis.")
        return
    
    st.markdown(
        f'<div class="section-header">'
        f'<img src="{SPRITES["chart"]}" class="section-icon">Coverage Analysis</div>',
        unsafe_allow_html=True
    )
    
    # Get analysis data
    analysis = analyze_team_by_type(team)
    
    if not analysis:
        st.info("Add more Pokemon to see the type analysis.")
        return
    
    # Table header
    header_cols = st.columns([1.1, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.9])
    headers = ["Type", "Immune", "4x Res", "2x Res", "Neutral", "2x Weak", "4x Weak", "Rating"]
    
    for i, header in enumerate(headers):
        with header_cols[i]:
            st.markdown(f'<span class="coverage-header">{header}</span>', unsafe_allow_html=True)
    
    st.markdown('<hr style="margin:8px 0;border:none;border-top:1px solid rgba(255,255,255,0.2);">', unsafe_allow_html=True)
    
    # Data rows
    for item in analysis:
        row_cols = st.columns([1.1, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.9])
        
        with row_cols[0]:
            type_badge = render_type_badge(item["type"])
            st.markdown(f'{type_badge}', unsafe_allow_html=True)
        
        with row_cols[1]:
            color = "#22c55e" if item["immune"] > 0 else "#6b7280"
            st.markdown(f'<span class="stat-value" style="color:{color};">{item["immune"]}</span>', unsafe_allow_html=True)
        
        with row_cols[2]:
            color = "#4ade80" if item["resist_4x"] > 0 else "#6b7280"
            st.markdown(f'<span class="stat-value" style="color:{color};">{item["resist_4x"]}</span>', unsafe_allow_html=True)
        
        with row_cols[3]:
            color = "#86efac" if item["resist_2x"] > 0 else "#6b7280"
            st.markdown(f'<span class="stat-value" style="color:{color};">{item["resist_2x"]}</span>', unsafe_allow_html=True)
        
        with row_cols[4]:
            st.markdown(f'<span class="stat-value" style="color:#9ca3af;">{item["neutral"]}</span>', unsafe_allow_html=True)
        
        with row_cols[5]:
            color = "#fca5a5" if item["weak_2x"] > 0 else "#6b7280"
            st.markdown(f'<span class="stat-value" style="color:{color};">{item["weak_2x"]}</span>', unsafe_allow_html=True)
        
        with row_cols[6]:
            color = "#ef4444" if item["weak_4x"] > 0 else "#6b7280"
            st.markdown(f'<span class="stat-value" style="color:{color};">{item["weak_4x"]}</span>', unsafe_allow_html=True)
        
        with row_cols[7]:
            st.markdown(
                f'<span class="rating-badge" style="background-color:{item["rating_color"]}20;color:{item["rating_color"]};">'
                f'{item["rating"]}</span>',
                unsafe_allow_html=True
            )


def render_team_details_table(team: List[str]):
    """Render a table showing each Pokemon with their individual weaknesses and resistances."""
    if not team:
        return
    
    # Table header
    header_cols = st.columns([1.3, 1.5, 1.5])
    with header_cols[0]:
        st.markdown('<span class="table-header-arcade">POKEMON</span>', unsafe_allow_html=True)
    with header_cols[1]:
        st.markdown('<span class="table-header-arcade">WEAKNESS</span>', unsafe_allow_html=True)
    with header_cols[2]:
        st.markdown('<span class="table-header-arcade">RESISTANCE</span>', unsafe_allow_html=True)
    
    st.markdown('<hr style="margin:8px 0;border:none;border-top:1px solid rgba(255,255,255,0.3);">', unsafe_allow_html=True)
    
    for pokemon_id in team:
        pokemon = POKEMON.get(pokemon_id, {})
        name = pokemon.get("name", "Unknown")
        types = pokemon.get("types", [])
        showdown_id = pokemon.get("showdown_id", pokemon_id)
        
        weaknesses, resistances, immunities = get_pokemon_weaknesses_resistances(types)
        
        # Pokemon types badges
        types_html = " ".join([render_type_badge(t) for t in types])
        
        # Weakness badges
        weakness_html = " ".join([render_type_badge(w) for w in weaknesses]) if weaknesses else '<span style="color:#666;font-family:Press Start 2P;font-size:0.5rem;">—</span>'
        
        # Resistance badges (immunities with special border)
        resistance_parts = []
        for r in resistances:
            resistance_parts.append(render_type_badge(r))
        for i in immunities:
            resistance_parts.append(f'<span class="type-badge" style="background-color: {TYPE_COLORS.get(i, "#888")}; border: 2px solid #ffd700; box-shadow: 0 0 4px #ffd700;">{i}</span>')
        resistance_html = " ".join(resistance_parts) if resistance_parts else '<span style="color:#666;font-family:Press Start 2P;font-size:0.5rem;">—</span>'
        
        # Sprite with fallbacks
        sprite_html = get_sprite_html(showdown_id, pokemon, size=40)
        
        # Row
        row_cols = st.columns([1.3, 1.5, 1.5])
        with row_cols[0]:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;min-height:45px;">'
                f'{sprite_html}'
                f'<div>'
                f'<div class="poke-name-arcade">{name}</div>'
                f'<div style="margin-top:4px;">{types_html}</div>'
                f'</div></div>',
                unsafe_allow_html=True
            )
        with row_cols[1]:
            st.markdown(f'<div style="line-height:2.2;min-height:45px;display:flex;align-items:center;flex-wrap:wrap;gap:3px;">{weakness_html}</div>', unsafe_allow_html=True)
        with row_cols[2]:
            st.markdown(f'<div style="line-height:2.2;min-height:45px;display:flex;align-items:center;flex-wrap:wrap;gap:3px;">{resistance_html}</div>', unsafe_allow_html=True)


# =============================================================================
# MAIN APP
# =============================================================================

def main():
    inject_custom_css()
    
    # Initialize session state
    if "team" not in st.session_state:
        st.session_state.team = []
    
    # Header
    st.markdown(
        f'<div class="main-header">'
        f'<h1 style="margin:0;">'
        f'<img src="{SPRITES["master_ball"]}" class="header-icon">'
        f'Pokémon Team Coverage Analyzer</h1>'
        f'<p style="color:#6b7280;margin:0.5rem 0 0 0;">Defensive Type Analysis - Smogon 1v1</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # =========================================================================
    # SECTION 1: Pokemon Selector with Generation Filter
    # =========================================================================
    st.markdown(
        f'<div class="section-header">'
        f'<img src="{SPRITES["search"]}" class="section-icon">Pokemon Selector</div>',
        unsafe_allow_html=True
    )
    
    # Check if Pokemon data loaded successfully
    if not POKEMON:
        st.error("Failed to load Pokemon data. Please refresh the page.")
        return
    
    # Get Pokemon organized by generation
    pokemon_by_gen = get_pokemon_by_generation(POKEMON)
    
    # Generation selector and Pokemon selector
    gen_col, pokemon_col = st.columns([1, 2])
    
    with gen_col:
        selected_gen = st.selectbox(
            "Generation",
            options=["All Generations"] + list(pokemon_by_gen.keys()),
            key="gen_selector",
            label_visibility="collapsed"
        )
    
    # Build Pokemon options based on selected generation
    if selected_gen == "All Generations":
        pokemon_options = {data["name"]: pid for pid, data in POKEMON.items()}
        pokemon_list = sorted(pokemon_options.keys())
    else:
        pokemon_options = {name: pid for pid, name in pokemon_by_gen.get(selected_gen, [])}
        pokemon_list = [name for _, name in pokemon_by_gen.get(selected_gen, [])]
    
    with pokemon_col:
        selected_name = st.selectbox(
            "Search Pokemon",
            options=[""] + pokemon_list,
            format_func=lambda x: "Select a Pokemon..." if x == "" else x,
            key="pokemon_selector",
            label_visibility="collapsed"
        )
    
    # Action buttons
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
    
    with btn_col1:
        if st.button("Add to Team", use_container_width=True, type="primary"):
            if selected_name and selected_name in pokemon_options:
                pokemon_id = pokemon_options[selected_name]
                if len(st.session_state.team) < 6:
                    if pokemon_id not in st.session_state.team:
                        st.session_state.team.append(pokemon_id)
                        st.rerun()
                    else:
                        st.toast(f"{selected_name} is already on your team.")
                else:
                    st.toast("Team is full (max 6)")
    
    with btn_col2:
        if st.button("Clear Team", use_container_width=True):
            st.session_state.team = []
            st.rerun()
    
    with btn_col3:
        st.markdown(
            f'<div style="text-align:center;padding:8px;color:#9ca3af;font-family:Press Start 2P;font-size:0.7rem;">'
            f'{len(st.session_state.team)}/6</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("<div style='margin:1.5rem 0;'></div>", unsafe_allow_html=True)
    
    # =========================================================================
    # SECTION 2: Team Display with Weaknesses/Resistances
    # =========================================================================
    if st.session_state.team:
        st.markdown(
            f'<div class="section-header">'
            f'<img src="{SPRITES["team"]}" class="section-icon">Your Team</div>',
            unsafe_allow_html=True
        )
        
        # Team slots (compact horizontal view with remove buttons)
        slot_cols = st.columns(6)
        for i in range(6):
            with slot_cols[i]:
                if i < len(st.session_state.team):
                    pokemon_id = st.session_state.team[i]
                    pokemon = POKEMON.get(pokemon_id, {})
                    name = pokemon.get("name", "?")
                    showdown_id = pokemon.get("showdown_id", pokemon_id)
                    sprite_html = get_sprite_html(showdown_id, pokemon, size=48)
                    
                    st.markdown(
                        f'<div style="text-align:center;">'
                        f'{sprite_html}'
                        f'<div style="font-size:0.75rem;color:#fff;margin-top:2px;">{name}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    if st.button("Remove", key=f"rm_{i}", use_container_width=True):
                        st.session_state.team.remove(pokemon_id)
                        st.rerun()
                else:
                    st.markdown(
                        f'<div style="text-align:center;opacity:0.3;">'
                        f'<img src="{SPRITES["poke_ball"]}" style="width:32px;height:32px;margin:8px 0;">'
                        f'<div style="font-size:0.75rem;color:#666;">Empty</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
        
        st.markdown("<div style='margin:1.5rem 0;'></div>", unsafe_allow_html=True)
        
        # Weaknesses/Resistances table
        st.markdown(
            f'<div class="section-header">'
            f'<img src="{SPRITES["shield"]}" class="section-icon">Weaknesses & Resistances</div>',
            unsafe_allow_html=True
        )
        
        render_team_details_table(st.session_state.team)
        
        st.markdown("<div style='margin:2rem 0;'></div>", unsafe_allow_html=True)
        
        # =====================================================================
        # SECTION 3: Coverage Analysis Table
        # =====================================================================
        render_coverage_table(st.session_state.team)
    
    else:
        # Empty state
        st.markdown(
            '<div style="text-align:center;padding:3rem;color:#6b7280;">'
            '<p style="font-size:1.1rem;">Select Pokemon to start the analysis</p>'
            '</div>',
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()