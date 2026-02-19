import streamlit as st
import random
import pandas as pd

# --- DATABASE INITIALIZATION ---
def init_teams():
    return [
        # TIER 1: UPS
        {"name": "Havenport Raptors", "tier": 1, "att": 88, "def": 87, "reputation": 95, "budget": 100},
        {"name": "Oakridge Bears", "tier": 1, "att": 85, "def": 90, "reputation": 90, "budget": 80},
        {"name": "Emerald Bay Vipers", "tier": 1, "att": 90, "def": 85, "reputation": 92, "budget": 90},
        {"name": "Silverwood Wolves", "tier": 1, "att": 89, "def": 89, "reputation": 94, "budget": 95},
        {"name": "Stonebridge Sharks", "tier": 1, "att": 91, "def": 88, "reputation": 93, "budget": 100},
        {"name": "Shadowridge Panthers", "tier": 1, "att": 83, "def": 84, "reputation": 80, "budget": 50},
        {"name": "Emberwood Scorpions", "tier": 1, "att": 82, "def": 82, "reputation": 78, "budget": 45},
        {"name": "Goldshore Dragons", "tier": 1, "att": 84, "def": 83, "reputation": 82, "budget": 55},
        {"name": "Havencity Bulls", "tier": 1, "att": 81, "def": 84, "reputation": 75, "budget": 40},
        {"name": "Cresthill Falcons", "tier": 1, "att": 87, "def": 86, "reputation": 88, "budget": 70},
        {"name": "Silverwood Tigers", "tier": 1, "att": 84, "def": 82, "reputation": 81, "budget": 60},
        {"name": "Oakridge Owls", "tier": 1, "att": 80, "def": 81, "reputation": 72, "budget": 35},
        # TIER 2: UChL
        {"name": "Ironcliff Titans", "tier": 2, "att": 78, "def": 79, "reputation": 70, "budget": 30},
        {"name": "Stonebrook Foxes", "tier": 2, "att": 77, "def": 77, "reputation": 68, "budget": 28},
        {"name": "ValesTown Leopards", "tier": 2, "att": 75, "def": 74, "reputation": 65, "budget": 25},
        {"name": "Stonebridge Ravens", "tier": 2, "att": 73, "def": 76, "reputation": 63, "budget": 22},
        {"name": "Cliffside Workers", "tier": 2, "att": 71, "def": 72, "reputation": 60, "budget": 18},
        {"name": "Barreswell Knights", "tier": 2, "att": 72, "def": 73, "reputation": 61, "budget": 19},
        {"name": "Silverwood Hawks", "tier": 2, "att": 74, "def": 74, "reputation": 64, "budget": 24},
        {"name": "Silverpine Cougars", "tier": 2, "att": 73, "def": 73, "reputation": 62, "budget": 20},
        # TIER 3: UNL
        {"name": "Greenpool Hornets", "tier": 3, "att": 68, "def": 69, "reputation": 55, "budget": 12},
        {"name": "Red Gulf Lions", "tier": 3, "att": 67, "def": 67, "reputation": 53, "budget": 10},
        {"name": "Meadowview United", "tier": 3, "att": 69, "def": 68, "reputation": 54, "budget": 11},
        {"name": "Newhaven Mariners", "tier": 3, "att": 66, "def": 65, "reputation": 50, "budget": 8},
        {"name": "Deportivo Puente Nuevo", "tier": 3, "att": 65, "def": 66, "reputation": 49, "budget": 7},
        {"name": "Atletico Puerto Antiguo", "tier": 3, "att": 64, "def": 64, "reputation": 48, "budget": 6},
        {"name": "Emerald City SC", "tier": 3, "att": 63, "def": 63, "reputation": 45, "budget": 5},
        {"name": "Phoenix FC", "tier": 3, "att": 62, "def": 62, "reputation": 44, "budget": 5},
    ]

# --- GAME ENGINE ---
def play_match(home, away, is_neutral=False):
    h_adv = 1.1 if not is_neutral else 1.0
    h_prob = (home['att'] * h_adv) / (away['def'] * 1.1)
    a_prob = (away['att']) / (home['def'] * 1.1 * h_adv)
    
    h_goals = sum(1 for _ in range(6) if random.random() < (h_prob / 4))
    a_goals = sum(1 for _ in range(6) if random.random() < (a_prob / 4))
    return h_goals, a_goals

# --- UI & STATE ---
st.set_page_config(page_title="Unionia Manager Pro28", layout="wide")
st.title("⚽ Unionia Pro28 Manager Engine")

if 'game_state' not in st.session_state:
    st.session_state.game_state = "setup"
    st.session_state.year = 2026
    st.session_state.teams = init_teams()
    st.session_state.job_satisfaction = 100
    st.session_state.history = []

if st.session_state.game_state == "setup":
    st.subheader("Choose Your Club")
    team_names = [t['name'] for t in st.session_state.teams]
    selected = st.selectbox("Select a team to manage:", team_names)
    if st.button("Start Career"):
        st.session_state.my_team = selected
        st.session_state.game_state = "playing"
        st.rerun()

elif st.session_state.game_state == "playing":
    my_team_data = next(t for t in st.session_state.teams if t['name'] == st.session_state.my_team)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Club", my_team_data['name'])
    col2.metric("Tier", my_team_data['tier'])
    col3.metric("Board Trust", f"{st.session_state.job_satisfaction}%")

    if st.button("Simulate Season"):
        # Reset standings
        standings = {t['name']: {"pts": 0, "gf": 0, "ga": 0, "tier": t['tier']} for t in st.session_state.teams}
        
        # 1. UPS Logic (12 teams, Double RR)
        ups_teams = [t for t in st.session_state.teams if t['tier'] == 1]
        for _ in range(2):
            for i, home in enumerate(ups_teams):
                for j, away in enumerate(ups_teams):
                    if i != j:
                        gh, ga = play_match(home, away)
                        standings[home['name']]['gf'] += gh
                        standings[home['name']]['ga'] += ga
                        standings[away['name']]['gf'] += ga
                        standings[away['name']]['ga'] += gh
                        if gh > ga: standings[home['name']]['pts'] += 3
                        elif ga > gh: standings[away['name']]['pts'] += 3
                        else:
                            standings[home['name']]['pts'] += 1
                            standings[away['name']]['pts'] += 1

        # 2. Relegation/Promotion Logic
        ups_sorted = sorted([{"name": k, **v} for k,v in standings.items() if v['tier'] == 1], key=lambda x: x['pts'], reverse=True)
        
        # Board Check
        my_rank = next(i for i, t in enumerate(ups_sorted) if t['name'] == st.session_state.my_team) + 1
        if my_rank > 10:
            st.session_state.job_satisfaction -= 40
        else:
            st.session_state.job_satisfaction = min(100, st.session_state.job_satisfaction + 10)
            
        if st.session_state.job_satisfaction <= 0:
            st.error("❌ YOU HAVE BEEN SACKED!")
            if st.button("Restart"):
                st.session_state.game_state = "setup"
                st.rerun()
        
        st.session_state.last_results = ups_sorted
        st.session_state.year += 1
        st.success(f"Season {st.session_state.year-1} Finished!")

    if 'last_results' in st.session_state:
        st.table(pd.DataFrame(st.session_state.last_results))

    if st.button("Quit Job"):
        st.session_state.game_state = "setup"
        st.rerun()
