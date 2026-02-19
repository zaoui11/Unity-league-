from flask import Flask, request, redirect, url_for, render_template_string, session
import random
import uuid

app = Flask(__name__)
app.secret_key = "unionia_secret_key"

# --- GAME CONSTANTS ---
TACTICS = {
    "Gegenpress": {"power": 1.1, "fitness_drain": 15, "description": "High risk, high reward. Boosts attack but kills fitness."},
    "Catenaccio": {"power": 0.9, "fitness_drain": 5, "description": "Solid defense. Low fitness drain, harder to score against."},
    "Tiki-Taka": {"power": 1.0, "fitness_drain": 8, "description": "Balanced possession. Stable performance."}
}

# --- CLUB DATA (Historical 28) ---
CLUBS_RAW = [
    ("Havenport Raptors", 1887, 86, 12, 33, 6), ("Oakridge Bears", 1890, 83, 6, 15, 1),
    ("Emerald Bay Vipers", 1893, 86, 14, 12, 3), ("Silverwood Wolves", 1895, 85, 16, 21, 4),
    ("Stonebridge Sharks", 1897, 87, 16, 11, 3), ("Shadowridge Panthers", 1899, 74, 0, 1, 0),
    ("Emberwood Scorpions", 1908, 72, 0, 1, 0), ("Goldshore Dragons", 1914, 75, 0, 3, 0),
    ("Havencity Bulls", 1918, 71, 0, 2, 0), ("Cresthill Falcons", 1920, 82, 3, 8, 2),
    ("Silverwood Tigers", 1921, 78, 2, 4, 0), ("Oakridge Owls", 1930, 76, 0, 2, 0),
    ("Ironcliff Titans", 1935, 80, 1, 5, 0), ("Stonebrook Foxes", 1940, 77, 1, 4, 0),
    ("ValesTown Leopards", 1948, 75, 0, 0, 0), ("Stonebridge Ravens", 1955, 74, 0, 1, 0),
    ("Cliffside Workers", 1955, 70, 0, 0, 0), ("Barreswell Knights", 1955, 70, 0, 0, 0),
    ("Silverwood Hawks", 1955, 73, 0, 2, 0), ("Silverpine Cougars", 1955, 71, 0, 1, 0),
    ("Greenpool Hornets", 1958, 72, 0, 0, 0), ("Red Gulf Lions", 1962, 72, 0, 0, 0),
    ("Meadowview United", 1965, 71, 0, 0, 0), ("Newhaven Mariners", 1969, 70, 0, 0, 0),
    ("Deportivo Puente Nuevo", 1972, 70, 0, 0, 0), ("Atletico Puerto Antiguo", 1979, 70, 0, 0, 0),
    ("Emerald City SC", 2006, 70, 0, 0, 0), ("Phoenix FC", 2006, 70, 0, 0, 0)
]

class GameState:
    def __init__(self):
        self.year = 2026
        self.clubs = []
        for name, year, rating, l_wins, c_wins, p_wins in CLUBS_RAW:
            self.clubs.append({
                "name": name, "founded": year, "rating": rating,
                "league_titles": l_wins, "cup_titles": c_wins, "pc_titles": p_wins,
                "points": 0, "gf": 0, "ga": 0, "played": 0,
                "budget": 1000000, "fans": 75, "board": 80, "prestige": rating // 2
            })
        
        # Initial Tiers
        self.ups = self.clubs[0:12]
        self.uchl = self.clubs[12:20]
        self.unl = self.clubs[20:28]
        self.player_club = None
        self.tactic = "Tiki-Taka"
        self.week = 1
        self.logs = ["Welcome to the Unionia Pro28 System."]

    def get_club(self, name):
        return next((c for c in self.clubs if c['name'] == name), None)

# Global storage (in-memory for demo, resets on restart)
games = {}

def get_game():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    uid = session['user_id']
    if uid not in games:
        games[uid] = GameState()
    return games[uid]

# --- MATCH ENGINE ---
def run_match(home, away, game, neutral=False):
    tactic_mod = TACTICS[game.tactic] if home['name'] == game.player_club else {"power": 1.0, "fitness_drain": 8}
    
    h_pwr = (home['rating'] * tactic_mod['power']) + (0 if neutral else 3)
    a_pwr = away['rating']
    
    h_score = max(0, int(random.gauss(h_pwr/25, 1)))
    a_score = max(0, int(random.gauss(a_pwr/25, 1)))

    home['gf'] += h_score; home['ga'] += a_score; home['played'] += 1
    away['gf'] += a_score; away['ga'] += h_score; away['played'] += 1

    if h_score > a_score:
        home['points'] += 3
        if home['name'] == game.player_club: game.logs.append(f"VICTORY! {home['name']} {h_score}-{a_score} {away['name']}")
    elif a_score > h_score:
        away['points'] += 3
        if home['name'] == game.player_club: game.logs.append(f"DEFEAT! {home['name']} {h_score}-{a_score} {away['name']}")
    else:
        home['points'] += 1; away['points'] += 1
        if home['name'] == game.player_club: game.logs.append(f"DRAW. {home['name']} {h_score}-{a_score} {away['name']}")
    
    # Financials (Attendance)
    revenue = (home['prestige'] * 1000) + (h_score * 500)
    home['budget'] += revenue

# --- TEMPLATES ---
BASE_HTML = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
    <title>Unionia Manager Pro</title>
</head>
<body class="container">
    <nav>
        <ul><li><strong>Unionia Pro28</strong></li></ul>
        <ul>
            <li><a href="/">Dashboard</a></li>
            <li><a href="/table">Tables</a></li>
            <li><a href="/history">History</a></li>
        </ul>
    </nav>
    {% block content %}{% endblock %}
    <footer style="margin-top: 2rem; font-size: 0.8rem; text-align: center;">
        Republic of Unionia Football System &copy; {{ year }}
    </footer>
</body>
</html>
"""

@app.route("/")
def index():
    game = get_game()
    if not game.player_club:
        return render_template_string(BASE_HTML + """
        {% block content %}
        <h1>Select Your Club</h1>
        <div class="grid">
        {% for club in clubs %}
            <form action="/select" method="post">
                <input type="hidden" name="name" value="{{club.name}}">
                <button type="submit" class="secondary">{{club.name}} (R{{club.rating}})</button>
            </form>
        {% endfor %}
        </div>
        {% endblock %}
        """, clubs=game.clubs, year=game.year)

    me = game.get_club(game.player_club)
    return render_template_string(BASE_HTML + """
    {% block content %}
    <div class="grid">
        <article>
            <h5>{{ me.name }}</h5>
            <p>💰 Budget: ${{ "{:,}".format(me.budget) }}<br>
            📈 Rating: {{ me.rating }} | 🏟️ Week: {{ week }}</p>
            <progress value="{{ me.board }}" max="100"></progress>
            <small>Board Trust: {{ me.board }}%</small>
        </article>
        <article>
            <h5>Tactics</h5>
            <form action="/set_tactic" method="post">
                <select name="tactic" onchange="this.form.submit()">
                    {% for t in tactics %}<option value="{{t}}" {% if t == current_t %}selected{% endif %}>{{t}}</option>{% endfor %}
                </select>
            </form>
            <small>{{ tactics[current_t].description }}</small>
        </article>
    </div>
    <form action="/play" method="post"><button class="contrast">Play Next Gameweek</button></form>
    <article style="height: 200px; overflow-y: scroll;">
        <h6>Match Reports</h6>
        <ul>{% for log in logs[::-1] %}<li>{{ log }}</li>{% endfor %}</ul>
    </article>
    {% endblock %}
    """, me=me, week=game.week, tactics=TACTICS, current_t=game.tactic, logs=game.logs, year=game.year)

@app.route("/select", methods=["POST"])
def select():
    game = get_game()
    game.player_club = request.form.get("name")
    game.logs.append(f"You have been appointed manager of {game.player_club}.")
    return redirect("/")

@app.route("/set_tactic", methods=["POST"])
def set_tactic():
    game = get_game()
    game.tactic = request.form.get("tactic")
    return redirect("/")

@app.route("/play", methods=["POST"])
def play_week():
    game = get_game()
    # Simplified week logic: simulate all tiers
    for tier in [game.ups, game.uchl, game.unl]:
        random.shuffle(tier)
        for i in range(0, len(tier), 2):
            run_match(tier[i], tier[i+1], game)
    
    game.week += 1
    # Adjust Board Trust based on points/played
    me = game.get_club(game.player_club)
    target = 1.2 # points per game expected
    actual = me['points'] / me['played']
    me['board'] = max(0, min(100, me['board'] + int((actual - target) * 10)))
    
    if me['board'] <= 0:
        game.logs.append("YOU HAVE BEEN FIRED!")
        # Reset game for this user
        games.pop(session['user_id'])
    
    return redirect("/")

@app.route("/table")
def table():
    game = get_game()
    def sort_t(t): return sorted(t, key=lambda x: (x['points'], x['gf']-x['ga']), reverse=True)
    return render_template_string(BASE_HTML + """
    {% block content %}
    <h3>Unity Premiership (UPS)</h3>
    <table>
        <thead><tr><th>Club</th><th>P</th><th>Pts</th><th>GD</th></tr></thead>
        {% for c in ups %}<tr><td>{{c.name}}</td><td>{{c.played}}</td><td>{{c.points}}</td><td>{{c.gf-c.ga}}</td></tr>{% endfor %}
    </table>
    {% endblock %}
    """, ups=sort_t(game.ups), year=game.year)

@app.route("/history")
def history():
    game = get_game()
    return render_template_string(BASE_HTML + """
    {% block content %}
    <h3>Historical Records</h3>
    <table>
        <thead><tr><th>Club</th><th>League</th><th>Unity Cup</th><th>Prem Cup</th></tr></thead>
        {% for c in clubs %}
        <tr><td>{{c.name}}</td><td>{{c.league_titles}}</td><td>{{c.cup_titles}}</td><td>{{c.pc_titles}}</td></tr>
        {% endfor %}
    </table>
    {% endblock %}
    """, clubs=game.clubs, year=game.year)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
