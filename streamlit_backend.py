
import streamlit as st
import random
from collections import defaultdict

# Import the actual draft engine logic here (placeholder)
from fantasy_draft_sim import run_draft, PLAYER_POOL, KEEPERS, STRATEGY, choose_best_player, Team

# Constants
NUM_TEAMS = 12
DRAFT_ROUNDS = 15

def generate_draft_order(num_teams, rounds):
    order = []
    for rnd in range(rounds):
        this_round = list(range(num_teams))
        if rnd % 2 == 1:
            this_round.reverse()
        order.append(this_round)
    return order

# Inject dummy player pool if needed
if not PLAYER_POOL:
    PLAYER_POOL.extend([
        {"name": f"Player {i}", "position": random.choice(["QB", "RB", "WR", "TE", "K", "DEF"]), "o_rank": i, "tags": []}
        for i in range(200)
    ])

PLAYER_POOL.sort(key=lambda x: x['o_rank'])

st.set_page_config(page_title="Fantasy Draft Simulator", layout="wide")
st.title("🏈 Fantasy Football Draft Simulator")

# Sidebar settings
st.sidebar.header("Draft Strategy Settings")
STRATEGY['early_dual_threat_qb'] = st.sidebar.checkbox("Prioritize Early Dual-Threat QB", value=True)
STRATEGY['wr_lean'] = st.sidebar.checkbox("Lean WR Early", value=True)
STRATEGY['handcuff_rbs'] = st.sidebar.checkbox("Draft Handcuff RBs Late", value=True)
STRATEGY['value_te'] = st.sidebar.checkbox("Target Value TEs", value=True)
STRATEGY['stream_def'] = st.sidebar.checkbox("Stream DEF/K Late", value=True)
STRATEGY['late_dual_threat_qb_target'] = st.sidebar.text_input("Late Round Dual-Threat QB Target", "Caleb Williams")

uploaded_file = st.sidebar.file_uploader("Upload Custom Player Pool (CSV)", type=["csv"])
if uploaded_file:
    import pandas as pd
    df = pd.read_csv(uploaded_file)
    PLAYER_POOL.clear()
    PLAYER_POOL.extend(df.to_dict(orient="records"))
    PLAYER_POOL.sort(key=lambda x: x['o_rank'])
    st.sidebar.success("Custom player pool loaded!")

st.header("Interactive Draft Mode")

user_team_index = 0
teams = [Team(f"Team {i+1}") for i in range(NUM_TEAMS)]
draft_order = generate_draft_order(NUM_TEAMS, DRAFT_ROUNDS)
available_players = PLAYER_POOL.copy()
current_round = st.session_state.get("round", 0)
current_pick_index = st.session_state.get("pick_index", 0)

if "draft_log" not in st.session_state:
    st.session_state.draft_log = []

if current_round < DRAFT_ROUNDS:
    current_order = draft_order[current_round]
    if current_pick_index < NUM_TEAMS:
        team_idx = current_order[current_pick_index]
        current_team = teams[team_idx]

        if team_idx == user_team_index:
            st.subheader(f"Your Pick - Round {current_round + 1}")
            choices = [f"{p['name']} ({p['position']})" for p in available_players[:20]]
            choice = st.selectbox("Select your pick:", choices)
            if st.button("Draft Player"):
                selected = available_players.pop(choices.index(choice))
                current_team.draft_player(selected, current_round)
                st.session_state.draft_log.append((current_team.name, current_round + 1, selected['name']))
                st.session_state.pick_index = current_pick_index + 1
                st.experimental_rerun()
        else:
            auto_pick = choose_best_player(current_team, available_players, current_round)
            current_team.draft_player(auto_pick, current_round)
            st.session_state.draft_log.append((current_team.name, current_round + 1, auto_pick['name']))
            st.session_state.pick_index = current_pick_index + 1
            st.experimental_rerun()
    else:
        st.session_state.round = current_round + 1
        st.session_state.pick_index = 0
        st.experimental_rerun()
else:
    st.success("Draft Complete!")
    st.subheader("Draft Summary")
    for team in teams:
        with st.expander(team.name):
            for rnd in sorted(team.picks_by_round):
                pick = team.picks_by_round[rnd]
                st.markdown(f"**Round {rnd+1}:** {pick['name']} ({pick.get('position', 'N/A')})")

    st.subheader("Draft Log")
    for log in st.session_state.draft_log:
        st.markdown(f"**{log[0]}** - Round {log[1]}: {log[2]}")
