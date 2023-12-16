#working web server 
import os
from flask import Flask, render_template_string, redirect, url_for, request, session
from azure.cosmos import CosmosClient, exceptions, PartitionKey
import requests
import sys
import time
home_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Networking Project NFL Web Server Scoreboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
            text-align: center;
        }

        h1 {
            color: #333;
        }

        h2 {
            color: #555;
            margin-bottom: 30px;
        }

        .button-container {
            display: flex;
            justify-content: center;
        }

        button {
            padding: 15px 30px;
            font-size: 18px;
            margin: 0 10px;
            cursor: pointer;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }

        button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>Networking Project NFL Web Server Scoreboard</h1>
    <h2>by Collin Easley, Christian Lindo, and Angel Santiago</h2>

    <div class="button-container">
        <button onclick="window.location.href='/register'">Register</button>
        <button onclick="window.location.href='/login'">Login</button>
    </div>
</body>
</html>
"""
registration_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Registration</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }

        h1 {
            text-align: center;
            color: #333;
        }

        form {
            text-align: center;
        }

        label {
            display: block;
            margin-bottom: 10px;
        }

        input {
            padding: 8px;
            font-size: 16px;
            margin-bottom: 15px;
        }

        select {
            padding: 8px;
            font-size: 16px;
            margin-bottom: 15px;
        }

        button {
            padding: 8px 16px;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <h1>User Registration</h1>

    <form method="post" action="{{ url_for('register') }}">
        <label for="username">Username:</label>
        <input type="text" name="username" id="username" required>

        <label for="password">Password:</label>
        <input type="password" name="password" id="password" required>

        <label for="favorite_team">Select Your Favorite NFL Team:</label>
        <select name="favorite_team" id="favorite_team">
            <option value="None">None</option>
            <option value="Arizona Cardinals">Arizona Cardinals</option>
            <option value="Atlanta Falcons">Atlanta Falcons</option>
            <option value="Baltimore Ravens">Baltimore Ravens</option>
            <option value="Buffalo Bills">Buffalo Bills</option>
            <option value="Carolina Panthers">Carolina Panthers</option>
            <option value="Chicago Bears">Chicago Bears</option>
            <option value="Cincinnati Bengals">Cincinnati Bengals</option>
            <option value="Cleveland Browns">Cleveland Browns</option>
            <option value="Dallas Cowboys">Dallas Cowboys</option>
            <option value="Denver Broncos">Denver Broncos</option>
            <option value="Detroit Lions">Detroit Lions</option>
            <option value="Green Bay Packers">Green Bay Packers</option>
            <option value="Houston Texans">Houston Texans</option>
            <option value="Indianapolis Colts">Indianapolis Colts</option>
            <option value="Jacksonville Jaguars">Jacksonville Jaguars</option>
            <option value="Kansas City Chiefs">Kansas City Chiefs</option>
            <option value="Las Vegas Raiders">Las Vegas Raiders</option>
            <option value="Los Angeles Chargers">Los Angeles Chargers</option>
            <option value="Los Angeles Rams">Los Angeles Rams</option>
            <option value="Miami Dolphins">Miami Dolphins</option>
            <option value="Minnesota Vikings">Minnesota Vikings</option>
            <option value="New England Patriots">New England Patriots</option>
            <option value="New Orleans Saints">New Orleans Saints</option>
            <option value="New York Giants">New York Giants</option>
            <option value="New York Jets">New York Jets</option>
            <option value="Philadelphia Eagles">Philadelphia Eagles</option>
            <option value="Pittsburgh Steelers">Pittsburgh Steelers</option>
            <option value="San Francisco 49ers">San Francisco 49ers</option>
            <option value="Seattle Seahawks">Seattle Seahawks</option>
            <option value="Tampa Bay Buccaneers">Tampa Bay Buccaneers</option>
            <option value="Tennessee Titans">Tennessee Titans</option>
            <option value="Washington Commanders">Washington Commanders</option>
        </select>

        <button type="submit">Register</button>
    </form>
</body>
</html>
"""

login_html = """
<!-- login.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
</head>
<body>
    <h1>Login</h1>
    <form method="post" action="{{ url_for('login') }}">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
        <br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
"""
apiinital_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NFL Scores</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }

        h1 {
            text-align: center;
            color: #333;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px; /* Adjust the gap as needed */
        }

        .score-card {
            border: 1px solid #ccc;
            border-radius: 8px;
            margin: 10px;
            padding: 15px;
            background-color: #fff;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .team {
            font-size: 18px;
            font-weight: bold;
            display: flex;
            align-items: center;
        }

        .star {
            color: gold;
            margin-right: 5px;
        }

        .score {
            font-size: 24px;
            margin-top: 5px;
        }

        .completed {
            color: #28a745;
        }

        .not-completed {
            color: #ffc107;
        }
    </style>
</head>
<body>

    <h1>NFL Scores</h1>
	<h2>Powered by The Odds API on Rapid API</h2>

    {% if nfl_scores %}
        {% for game in nfl_scores %}
            <div class="score-card">
                <div class="team">
                    {% if game.is_favorite %}
                        <span class="star">★</span>
                    {% endif %}
                    {{ game.home_team }} vs {{ game.away_team }}
                </div>
                <div class="score">
                    {% if game.completed %}
                        {{ game.home_score | default("N/A") }} - {{ game.away_score | default("N/A") }}
                        <span class="completed">Completed</span>
                    {% else %}
                        Game in progress
                        <span class="not-completed">In Progress</span>
                    {% endif %}
                </div>
                <div>Last Update: {{ game.last_update | default("N/A") }}</div>
            </div>
        {% endfor %}
    {% else %}
        <p>No NFL scores available.</p>
    {% endif %}
</body>
</html>
"""
#script_path = os.path.dirname(os.path.abspath(__file__))

# Create a Flask app
#app = Flask(__name__, template_folder=os.path.join(script_path, 'templates'))
app = Flask(__name__)
app.secret_key = 'f3f3034a1526efae434e38aaade8c28e'

# requirments to access my azure cosmos database and conatainer 
endpoint = "https://fgcyascecl.documents.azure.com:443/"
key = "8MSWmqzEVgffuuTM0Q51mQQu5tCDatEPJF5JVvAnm1PpEHwYSHvEaEUmxhSX0mMluzUrkFxvVtieACDbQoL5yQ=="
database_name = "userRegister"
container_name = "userContainer1"


client = CosmosClient(endpoint, key)


database = client.get_database_client(database_name)


container = database.get_container_client(container_name)

# retrys till cosmos database is connected 
max_retries = 3
retry_interval = 1 

def create_item_with_retry(container, user_data):
    retries = 0
    while retries < max_retries:
        try:
            container.create_item(body=user_data)
            print("Item created successfully.")
            break  
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 429: 
                print(f"Rate limited. Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
                retries += 1
            else:
                raise  

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'register' in request.form:
            return redirect(url_for('register'))
        elif 'login' in request.form:
            return redirect(url_for('login'))

    return render_template_string(home_html)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        favorite_team = request.form['favorite_team']

        user_data = {
            'id': username, 
            'username': username,
            'password': password,
            'favorite_team': favorite_team
        }

        create_item_with_retry(container, user_data)

       
        session['favorite_team'] = favorite_team

        
        return redirect(url_for('home'))

    return render_template_string(registration_html)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = f"SELECT * FROM c WHERE c.id = '{username}' AND c.password = '{password}'"
        result = list(container.query_items(query, enable_cross_partition_query=True))

        if result:
            session['username'] = username

            session['favorite_team'] = result[0]['favorite_team']

            return redirect(url_for('display_scores'))

    return render_template_string(login_html)

@app.route('/display_scores')
def display_scores():
    if 'username' not in session or 'favorite_team' not in session:
        return redirect(url_for('login'))

    favorite_team = session['favorite_team']

    url = 'https://odds.p.rapidapi.com/v4/sports/americanfootball_nfl/scores'
    params = {'daysFrom': '3'}

    headers = {
        'X-RapidAPI-Key': '6008a05bf3msh9fd81ec9a947856p13238ejsn0e67478ed50e',
        'X-RapidAPI-Host': 'odds.p.rapidapi.com',
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        if 'message' in data:
            print(f"API Error: {data['message']}")
            nfl_scores = []
        else:
            nfl_scores = extract_nfl_scores(data, favorite_team)
    except Exception as error:
        print(f"An error occurred: {error}")
        nfl_scores = []

    return render_template_string(apiinital_html, nfl_scores=nfl_scores, favorite_team=favorite_team)

def extract_nfl_scores(data, favorite_team):
    nfl_scores = []

    for game in data:
        print(f"Unraveling the mysteries of 'game': {game}")

        home_team = game['home_team']
        away_team = game['away_team']

        print(f"Processing game: {home_team} vs {away_team}")

       
        if 'scores' in game and game['scores'] is not None:
            home_score = next((score['score'] for score in game['scores'] if score['name'] == home_team), None)
            away_score = next((score['score'] for score in game['scores'] if score['name'] == away_team), None)
        else:
            home_score, away_score = None, None

        nfl_scores.append({
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'completed': game.get('completed', False),
            'last_update': game.get('last_update', ''),
            'is_favorite': home_team == favorite_team or away_team == favorite_team,
        })

    # Move the scores of the favorite team to the front
    nfl_scores.sort(key=lambda x: x['is_favorite'], reverse=True)

    return nfl_scores

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000)
