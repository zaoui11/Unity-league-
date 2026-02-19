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
        return self.goals_for - self.goals_against

    def record_match(self, gf, ga):
        self.goals_for += gf
        self.goals_against += ga
        self.played += 1

    def __repr__(self):
        return f"{self.name} (R{self.rating})"

# Initial clubs and exact starting ratings
club_names = [
    "Havenport Raptors", "Oakridge Bears", "Emerald Bay Vipers", "Silverwood Wolves",
    "Stonebridge Sharks", "Shadowridge Panthers", "Emberwood Scorpions", "Goldshore Dragons",
    "Havencity Bulls", "Cresthill Falcons", "Silverwood Tigers", "Oakridge Owls",
    "Ironcliff Titans", "Stonebrook Foxes", "ValesTown Leopards", "Stonebridge Ravens",
    "Cliffside Workers", "Barreswell Knights", "Silverwood Hawks", "Silverpine Cougars",
    "Greenpool Hornets", "Red Gulf Lions", "Meadowview United", "Newhaven Mariners",
    "Deportivo Puente Nuevo", "Atletico Puerto Antiguo", "Emerald City SC", "Phoenix FC"
]

club_ratings = [
    86, 83, 86, 85,   # 1-4
    87, 74, 72, 75,   # 5-8
    71, 82, 78, 76,   # 9-12
    80, 77, 75, 74,   # 13-16
    70, 70, 73, 71,   # 17-20
    72, 72, 71, 70,   # 21-24
    70, 70, 70, 70    # 25-28
]

MASTER_CLUBS = [Team(n, r) for n, r in zip(club_names, club_ratings)]

# Initial tier assignment: first 12 UPS, next 8 UChL, last 8 UNL
UPS = [deepcopy(t) for t in MASTER_CLUBS[0:12]]
UChL = [deepcopy(t) for t in MASTER_CLUBS[12:20]]
UNL = [deepcopy(t) for t in MASTER_CLUBS[20:28]]

# Web state
season_year = 2026
logs = []
player_club_name = None
# Week schedules and index for week mode
schedules = {"ups": [], "uchl": [], "unl": []}
week_index = 0

# Simulation core functions
def simulate_match(home, away, neutral=False):
    # home advantage if not neutral
    home_adv = 3 if not neutral else 0
    p_home = home.power() + home_adv
    p_away = away.power()
    xg_home = max(0.1, p_home / 25.0)
    xg_away = max(0.1, p_away / 25.0)
    goals_home = max(0, int(round(random.gauss(xg_home, 0.8))))
    goals_away = max(0, int(round(random.gauss(xg_away, 0.8))))
    # reduce zero-zero frequency slightly
    if goals_home == 0 and goals_away == 0:
        chance = (xg_home + xg_away) / 10.0
        if random.random() < chance:
            if random.random() < 0.6:
                goals_home += 1
            else:
                goals_away += 1
    home.record_match(goals_home, goals_away)
    away.record_match(goals_away, goals_home)
    if goals_home > goals_away:
        home.points += 3
        home.morale = min(100, home.morale + 3)
        away.morale = max(0, away.morale - 3)
        outcome = "H"
    elif goals_home < goals_away:
        away.points += 3
        away.morale = min(100, away.morale + 3)
        home.morale = max(0, home.morale - 3)
        outcome = "A"
    else:
        home.points += 1
        away.points += 1
        home.morale = min(100, home.morale + 1)
        away.morale = min(100, away.morale + 1)
        outcome = "D"
    home.fitness = max(30, home.fitness - random.randint(6, 12))
    away.fitness = max(30, away.fitness - random.randint(6, 12))
    return goals_home, goals_away, outcome

# Scheduling helpers
def round_robin_rounds(teams):
    n = len(teams)
    order = teams[:]
    if n % 2 == 1:
        order = order + [None]
        n += 1
    rounds = []
    for r in range(n - 1):
        pairs = []
        for i in range(n // 2):
            a = order[i]
            b = order[n - 1 - i]
            if a is not None and b is not None:
                pairs.append((a, b))
        rounds.append(pairs)
        order = [order[0]] + [order[-1]] + order[1:-1]
    return rounds

def double_round_robin_pairs(teams):
    rounds = round_robin_rounds(teams)
    pairs = []
    for r in rounds:
        pairs.extend(r)
    for r in rounds:
        pairs.extend([(b, a) for (a, b) in r])
    return pairs

def triple_round_robin_pairs(teams):
    pairs = double_round_robin_pairs(teams)
    extra_rounds = round_robin_rounds(teams)
    chosen = random.choice(extra_rounds)
    pairs.extend(chosen)
    return pairs

def sorted_table(teams):
    return sorted(teams, key=lambda t: (t.points, t.gd(), t.goals_for), reverse=True)

# Cup helpers
def single_knockout(pairs, neutral=False):
    winners = []
    for home, away in pairs:
        h, a, _ = simulate_match(home, away, neutral=neutral)
        if h > a:
            winners.append(home)
        elif a > h:
            winners.append(away)
        else:
            winners.append(home if random.random() < 0.5 else away)
    return winners

def two_leg_tie(a, b):
    g1a, g1b, _ = simulate_match(a, b)
    g2b, g2a, _ = simulate_match(b, a)
    agg_a = g1a + g2a
    agg_b = g1b + g2b
    if agg_a > agg_b:
        return a
    if agg_b > agg_a:
        return b
    return a if random.random() < 0.5 else b

# League simulation
def simulate_UPS():
    for t in UPS:
        t.reset_for_season()
    for home, away in double_round_robin_pairs(UPS):
        simulate_match(home, away)
    return sorted_table(UPS)

def simulate_UChL():
    for t in UChL:
        t.reset_for_season()
    for home, away in triple_round_robin_pairs(UChL):
        simulate_match(home, away)
    return sorted_table(UChL)

def simulate_UNL():
    for t in UNL:
        t.reset_for_season()
    for home, away in double_round_robin_pairs(UNL):
        simulate_match(home, away)
    standings1 = sorted_table(UNL)
    top4 = standings1[:4]
    for t in top4:
        t.points = 0
        t.goals_for = 0
        t.goals_against = 0
        t.played = 0
    for home, away in double_round_robin_pairs(top4):
        simulate_match(home, away)
    standings2 = sorted_table(top4)
    champion = standings2[0]
    champion.seasons_won += 1
    return standings1, champion

# Cups
def run_premiership_cup(ups_standings):
    qualifiers = ups_standings[4:12]
    pairs_q = [
        (qualifiers[0], qualifiers[7]),
        (qualifiers[1], qualifiers[6]),
        (qualifiers[2], qualifiers[5]),
        (qualifiers[3], qualifiers[4])
    ]
    q_winners = single_knockout(pairs_q)
    top4 = ups_standings[:4]
    qf_pool = top4 + q_winners
    random.shuffle(qf_pool)
    qf_pairs = [(qf_pool[i], qf_pool[i+1]) for i in range(0, 8, 2)]
    qf_winners = [two_leg_tie(a, b) for (a, b) in qf_pairs]
    sf_pairs = [(qf_winners[0], qf_winners[1]), (qf_winners[2], qf_winners[3])]
    sf_winners = [two_leg_tie(a, b) for (a, b) in sf_pairs]
    final_winner = single_knockout([(sf_winners[0], sf_winners[1])], neutral=True)[0]
    return final_winner

def run_unity_trophy():
    entrants = UChL + UNL
    random.shuffle(entrants)
    r16_pairs = [(entrants[i], entrants[i+1]) for i in range(0, 16, 2)]
    r16_w = single_knockout(r16_pairs)
    qf_pairs = [(r16_w[i], r16_w[i+1]) for i in range(0, 8, 2)]
    qf_w = single_knockout(qf_pairs)
    sf_pairs = [(qf_w[0], qf_w[1]), (qf_w[2], qf_w[3])]
    sf_w = [two_leg_tie(a, b) for (a, b) in sf_pairs]
    final = single_knockout([(sf_w[0], sf_w[1])], neutral=True)[0]
    return final

def run_unity_cup():
    pool = UChL + UNL
    random.shuffle(pool)
    r1_pairs = [(pool[i], pool[i+1]) for i in range(0, 16, 2)]
    r1 = single_knockout(r1_pairs)
    r2_pairs = [(r1[i], r1[i+1]) for i in range(0, 8, 2)]
    r2 = single_knockout(r2_pairs)
    qualifiers = r2  # four qualifiers
    ro16_pool = UPS[:] + qualifiers
    random.shuffle(ro16_pool)
    ro16_pairs = [(ro16_pool[i], ro16_pool[i+1]) for i in range(0, 16, 2)]
    r16 = single_knockout(ro16_pairs)
    qf_pairs = [(r16[i], r16[i+1]) for i in range(0, 8, 2)]
    qf = single_knockout(qf_pairs)
    sf_pairs = [(qf[0], qf[1]), (qf[2], qf[3])]
    sf = [two_leg_tie(a, b) for (a, b) in sf_pairs]
    final = single_knockout([(sf[0], sf[1])], neutral=True)[0]
    return final

# Promotion and relegation
def promotion_relegation(ups_table, uchl_table, unl_champion):
    global UPS, UChL, UNL
    relegated_from_UPS = ups_table[-2:]
    promoted_auto = uchl_table[0]
    playoff_pair = (uchl_table[1], uchl_table[2])
    playoff_winner = single_knockout([playoff_pair], neutral=True)[0]
    relegated_from_UChL = [uchl_table[-1]]
    promoted_from_UNL = unl_champion
    next_UPS = [t for t in UPS if t not in relegated_from_UPS]
    next_UPS.extend([promoted_auto, playoff_winner])
    next_UChL = [t for t in UChL if t not in ([promoted_auto, playoff_winner] + relegated_from_UChL)]
    next_UChL.extend(relegated_from_UPS)
    next_UChL.append(promoted_from_UNL)
    next_UNL = [t for t in UNL if t != promoted_from_UNL]
    next_UNL.extend(relegated_from_UChL)
    # validate sizes
    if not (len(next_UPS) == 12 and len(next_UChL) == 8 and len(next_UNL) == 8):
        raise RuntimeError("Tier sizes invalid after promotion/relegation")
    UPS[:] = next_UPS
    UChL[:] = next_UChL
    UNL[:] = next_UNL
    logs.append(f"Promotion/relegation applied. Promoted to UPS: {promoted_auto.name} and {playoff_winner.name}.")

# Rating adjustment based on expected vs actual positions
def adjust_ratings_postseason(league_teams, league_table):
    # expected_rank: sort pre-season by rating (1 best)
    pre_sorted = sorted(league_teams, key=lambda t: t.rating, reverse=True)
    expected_rank_map = {t.name: (pre_sorted.index(t) + 1) for t in pre_sorted}
    for pos, team in enumerate(league_table, start=1):
        expected_rank = expected_rank_map.get(team.name, len(league_teams))
        actual_rank = pos
        raw_delta = (expected_rank - actual_rank) * ADJUST_FACTOR
        delta = int(round(raw_delta))
        if delta > MAX_DELTA:
            delta = MAX_DELTA
        if delta < -MAX_DELTA:
            delta = -MAX_DELTA
        old = team.rating
        team.rating = max(MIN_RATING, min(MAX_RATING, team.rating + delta))
        if delta != 0:
            logs.append(f"Rating change: {team.name}: {old} -> {team.rating} (delta {delta})")

# Season runner
def run_one_season():
    global season_year
    logs.append(f"Season {season_year} start")
    ups_table = simulate_UPS()
    uchl_table = simulate_UChL()
    unl_table, unl_champion = simulate_UNL()
    pc = run_premiership_cup(ups_table)
    ut = run_unity_trophy()
    uc = run_unity_cup()
    promotion_relegation(ups_table, uchl_table, unl_champion)
    # apply rating adjustments
    adjust_ratings_postseason(UPS + UChL + UNL, ups_table)
    adjust_ratings_postseason(UChL, uchl_table)
    adjust_ratings_postseason(UNL, unl_table)
    logs.append(f"Season {season_year} complete. PC: {pc.name}, UT: {ut.name}, UC: {uc.name}, UNLchamp: {unl_champion.name}")
    season_year += 1

# Week mode helpers
def prepare_week_schedules():
    global schedules, week_index
    schedules['ups'] = double_round_robin_pairs(UPS)
    schedules['uchl'] = triple_round_robin_pairs(UChL)
    schedules['unl'] = double_round_robin_pairs(UNL)
    week_index = 0
    logs.append("Week schedules prepared")

def advance_week():
    global week_index
    if not schedules['ups']:
        prepare_week_schedules()
    max_len = max(len(schedules['ups']), len(schedules['uchl']), len(schedules['unl']))
    if week_index >= max_len:
        # finalize season
        run_one_season()
        prepare_week_schedules()
        return "season_finalized"
    if week_index < len(schedules['ups']):
        h, a = schedules['ups'][week_index]
        g1, g2, _ = simulate_match(h, a)
        logs.append(f"UPS: {h.name} {g1}-{g2} {a.name}")
    if week_index < len(schedules['uchl']):
        h, a = schedules['uchl'][week_index]
        g1, g2, _ = simulate_match(h, a)
        logs.append(f"UChL: {h.name} {g1}-{g2} {a.name}")
    if week_index < len(schedules['unl']):
        h, a = schedules['unl'][week_index]
        g1, g2, _ = simulate_match(h, a)
        logs.append(f"UNL: {h.name} {g1}-{g2} {a.name}")
    week_index += 1
    return "week_played"

# Minimal simple HTML templates
INDEX_HTML = """
<!doctype html>
<title>CyberFoot Pro28</title>
<h1>CyberFoot Pro28</h1>
<p>Season: {{ season }}</p>

<form action="/choose" method="post">
  <label>Choose club name (exact):</label>
  <input name="club" placeholder="Club name">
  <button type="submit">Select club</button>
</form>

<p>Selected club: {{ player or 'None' }}</p>

<form action="/run_season" method="post">
  <button type="submit">Run one season</button>
</form>

<form action="/run_loop" method="post">
  <label>Run N seasons:</label>
  <input name="n" value="1" size="3">
  <button type="submit">Run</button>
</form>

<form action="/prepare_weeks" method="post">
  <button type="submit">Prepare week schedules</button>
</form>

<form action="/advance_week" method="post">
  <button type="submit">Advance one week</button>
</form>

<p><a href="/tiers">Show tiers and ratings</a> | <a href="/logs">Show logs</a></p>

<h3>Top of each tier</h3>
<div style="display:flex;gap:30px">
  <div>
    <h4>UPS</h4>
    <ul>{% for t in ups %}<li>{{t.name}} (R{{t.rating}})</li>{% endfor %}</ul>
  </div>
  <div>
    <h4>UChL</h4>
    <ul>{% for t in uchl %}<li>{{t.name}} (R{{t.rating}})</li>{% endfor %}</ul>
  </div>
  <div>
    <h4>UNL</h4>
    <ul>{% for t in unl %}<li>{{t.name}} (R{{t.rating}})</li>{% endfor %}</ul>
  </div>
</div>
"""

TIERS_HTML = """
<!doctype html>
<title>Tiers</title>
<h1>Current tiers and ratings</h1>
<h2>UPS</h2>
<ul>{% for t in ups %}<li>{{t.name}} - R{{t.rating}}</li>{% endfor %}</ul>
<h2>UChL</h2>
<ul>{% for t in uchl %}<li>{{t.name}} - R{{t.rating}}</li>{% endfor %}</ul>
<h2>UNL</h2>
<ul>{% for t in unl %}<li>{{t.name}} - R{{t.rating}}</li>{% endfor %}</ul>
<p><a href="/">Back</a></p>
"""

LOGS_HTML = """
<!doctype html>
<title>Logs</title>
<h1>Event log</h1>
<pre style="white-space:pre-wrap;max-height:70vh;overflow:auto;border:1px solid #ccc;padding:8px;">
{% for line in logs %}{{line}}
{% endfor %}
</pre>
<p><a href="/">Back</a></p>
"""

app = Flask(__name__)

@app.route("/")
def index():
    return render_template_string(INDEX_HTML, season=season_year, ups=UPS, uchl=UChL, unl=UNL, player=player_club_name)

@app.route("/choose", methods=["POST"])
def choose():
    global player_club_name
    name = request.form.get("club","").strip()
    if name:
        player_club_name = name
        logs.append(f"Player selected: {name}")
    return redirect(url_for("index"))

@app.route("/run_season", methods=["POST"])
def run_season_route():
    run_one_season()
    return redirect(url_for("index"))

@app.route("/run_loop", methods=["POST"])
def run_loop_route():
    try:
        n = int(request.form.get("n","1"))
    except:
        n = 1
    for _ in range(max(1, n)):
        run_one_season()
    return redirect(url_for("index"))

@app.route("/prepare_weeks", methods=["POST"])
def prepare_weeks_route():
    prepare_week_schedules()
    return redirect(url_for("index"))

@app.route("/advance_week", methods=["POST"])
def advance_week_route():
    status = advance_week()
    if status == "season_finalized":
        logs.append("Season finalized by week advance.")
    return redirect(url_for("index"))

@app.route("/tiers")
def tiers_route():
    return render_template_string(TIERS_HTML, ups=UPS, uchl=UChL, unl=UNL)

@app.route("/logs")
def logs_route():
    return render_template_string(LOGS_HTML, logs=logs)

if __name__ == "__main__":
    prepare_week_schedules()
    print("Starting CyberFoot Pro28 app on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
