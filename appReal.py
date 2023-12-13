#working web server 

from flask import Flask, render_template, request, session, redirect, url_for
from azure.cosmos import CosmosClient, exceptions, PartitionKey
import requests
import sys
import time

# create route to access my html files 
app = Flask(__name__, template_folder=r'"C:\Users\colli\OneDrive\Desktop\NFLscores\templates"')
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

    return render_template('home.html')

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

    return render_template('registration.html')


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

    return render_template('login.html')

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

    return render_template('apiinital.html', nfl_scores=nfl_scores, favorite_team=favorite_team)

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
    try:
        app.run(port=500)
    except KeyboardInterrupt:
        sys.exit(0)
