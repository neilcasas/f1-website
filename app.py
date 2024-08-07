from flask import Flask, render_template, request
from newsapi import NewsApiClient
from operator import itemgetter
import ergast_py
import asyncio
import aiohttp
import mysql.connector

app = Flask(__name__, template_folder='templates')

# Initialize Ergast API
e = ergast_py.Ergast()

# Connect DB
def create_db_connection():
    return mysql.connector.connect(
        host="db_host",
        user="db_user",
        password="db_password",
        database="db_name"
    )

@app.route("/")
def index():
    # Initializing news api 
    newsapi = NewsApiClient(api_key='NEWS_API_KEY_HERE')

    # Get top headlines about F1
    f1_articles = newsapi.get_everything(q="formula+1+race+results",
                                          language='en', 
                                          page_size=8, 
                                          sort_by='relevancy',
                                          )['articles']
    # Get latest results
    race = e.season().round().get_race()
    latest_results = e.season().round().get_result()
    
    # Get podium
    podium = create_podium(latest_results.results)

    # Check if latest round in db, if not latest then update
    check_db(latest_results)

    return render_template("index.html", articles=f1_articles, race_results=latest_results, race=race, podium=podium)

# Driver standings
@app.route("/drivers", methods=["GET", "POST"])
def drivers(year=2024):
    if request.method == "POST":
        year = request.form.get("year", 2024, type=int)
    driver_standings = e.season(year).get_driver_standing().driver_standings
    return render_template("drivers.html", driver_standings = driver_standings, year = year, selected_year = year)

# Driver details
@app.route("/drivers/<string:driver_id>", methods=["GET", "POST"])
def driver_profile(driver_id):
    db = create_db_connection()
    mycursor = db.cursor()

    # Get driver's rookie year and final year
    mycursor.execute("SELECT pic, first_year, last_year, points, wins, championships FROM driver_profile WHERE driver_id = %s", (driver_id,))
    result = mycursor.fetchone()
    fallback_pic = """https://yt3.googleusercontent.com/ytc/AIdro_mmKAqlB_4g8BlELUXEIvVMW7P93zqX9warUvTXda3cN0Q=s900-c-k-c0x00ffffff-no-rj"""
    pic, first_year, last_year, points, wins, championships = result if result else (None, None, None, 0, 0, 0)
    driver_db_data = {"pic": pic if pic else fallback_pic, "first_year": first_year, "last_year": last_year, "points": points, "wins": wins, "championships": championships}

    # Close cursor and conection
    mycursor.close()
    db.close()

    # Get driver data
    driver_profile = e.driver(driver_id).get_driver()
    driver_standing = e.driver(driver_id).season(last_year).get_driver_standing()

    # If filtered by year
    if request.method == "POST":
        year = request.form.get("year", last_year, type=int) # year filter
        driver_standing = e.driver(driver_id).season(year).get_driver_standing()
        return render_template("driver-profile.html", driver=driver_profile, standing=driver_standing, 
                               driver_db_data = driver_db_data, selected_year = year)

    return render_template("driver-profile.html", driver=driver_profile, standing=driver_standing, 
                           driver_db_data=driver_db_data, selected_year = last_year)

# Constructor standings
@app.route("/constructors", methods=["GET", "POST"])
def constructors(year=2024): 
    if request.method == "POST":
        year = request.form.get("year", 2024, type=int)
    constructor_standings = e.season(year).get_constructor_standing().constructor_standings
    print(e.season(2024).round(1).get_results())
    return render_template("constructors.html", constructor_standings = constructor_standings, year = year, selected_year = year)

# Constructor details
@app.route("/constructors/<string:constructor_id>", methods=["GET", "POST"])
def constructor_profile(constructor_id):
    db = create_db_connection()
    mycursor = db.cursor()

    # Get team's first year and final year
    mycursor.execute("SELECT pic, first_year, last_year, points, wins, championships FROM team_profile WHERE team_id = %s", (constructor_id,))
    result = mycursor.fetchone()
    pic, first_year, last_year, points, wins, championships = result if result else (None, None, None, 0, 0, 0)
    fallback_pic = """https://132slotcar.us/images/products/CAR07-white_01.jpg"""
    constructor_db_data = {"pic": pic if pic else fallback_pic, "first_year": first_year, "last_year": last_year, "points": points, "wins": wins, "championships": championships}

    # Close cursor and conection
    mycursor.close()
    db.close()

    # Get constructor data
    constructor_data = e.constructor(constructor_id).get_constructor()
    constructor_standing = e.constructor(constructor_id).season(last_year).get_constructor_standing().constructor_standings[0]

    # If filtered by year
    if request.method == "POST":
        year = request.form.get("year", last_year, type=int) # year filter
        constructor_standing = e.constructor(constructor_id).season(year).get_constructor_standing().constructor_standings[0]
        return render_template("constructor-profile.html", constructor=constructor_data, standing=constructor_standing, 
                               constructor_db_data = constructor_db_data, selected_year = year)
    return render_template("constructor-profile.html", constructor=constructor_data, standing = constructor_standing, 
                           constructor_db_data = constructor_db_data, selected_year = last_year)

# All winners of all races within a season
@app.route("/races", methods=["GET", "POST"])
def races(year=2024):
    if request.method == "POST":
        year = request.form.get("year", 2024, type=int)

    race_results = asyncio.run(get_race_results(year))

    # Convert each 'round' into an int
    for result in race_results:
        try:
            result['round'] = int(result['round'])
        except ValueError:
            # Handle cases where 'round' is not a valid integer
            pass
    
    # Sort by round
    race_results.sort(key=itemgetter('round'))
    return render_template("races.html", race_results=race_results, year=year, selected_year=year)

# Race results
@app.route("/races/<int:year>/<int:round>")
def race_results(year, round):
    race_results = e.season(year).round(round).get_result()
    return render_template("race-results.html", race_results=race_results, year=year)

# Method for fetching race result per circuit in a season
async def fetch_race_result(session, year, circuit_id):
    url = f"https://ergast.com/api/f1/{year}/circuits/{circuit_id}/results.json?limit=5"

    # Access the Ergast API URL and wait for a response
    async with session.get(url) as response:
        # If response is successful
        if response.status == 200:
            # Wait for JSON data and return it, if there's no JSON data then return None
            data = await response.json()
            return data['MRData']['RaceTable']['Races'][0] if data['MRData']['RaceTable']['Races'] else None
        # Return none if request failed
        return None

# Perform the fetch requests concurrently 
async def get_race_results(year):
    async with aiohttp.ClientSession() as session:
        tasks = [] # List of fetch requests
        season_circuits = e.season(year).get_circuits() # Get all circuits within that season

        # For every circuit within that season
        for circuit in season_circuits:

            # Create a fetch request for its race result
            tasks.append(fetch_race_result(session, year, circuit.circuit_id))
        
        # Perform the fetch requests in the tasks list concurrently
        race_results = await asyncio.gather(*tasks)
        return [result for result in race_results if result]
    

# Create podium out of latest results, return list of driver dictionaries
def create_podium(latest_results):
    podium = []
    list = latest_results[:3]

    # Create db
    db = create_db_connection()
    cursor = db.cursor()
    for item in list:
        # Get info
        given_name = item.driver.given_name
        family_name = item.driver.family_name
        driver_id = item.driver.driver_id

        # Get image from driver_id
        cursor.execute("SELECT pic FROM driver_profile WHERE driver_id = %s", (driver_id,))
        result = cursor.fetchone()

        # Check if the result is None
        if result is None:
            pic = None
        else:
            pic = result[0]

        # Create driver dictionary
        driver = {'driver_id':driver_id, 'given_name':given_name, 'family_name': family_name, 'pic':pic}
        podium.append(driver)

    cursor.close()
    db.close()
    return podium

# Check db if it has the latest round
def check_db(latest_results):
    db = create_db_connection()
    cursor = db.cursor()

    updated_round = latest_results.round_no

    cursor.execute("SELECT round FROM current_season")
    result = cursor.fetchone()
    saved_round = result[0] if result else 0

    if updated_round > saved_round:
        update_db(updated_round, db)
    else:
        print('db is updated')

    cursor.close()
    db.close()

# Update drivers and teams based on latest race results
def update_db(updated_round, db):
    # Get first ten results only
    results = e.season().round(updated_round).get_result().results[:10]
    
    cursor = db.cursor()
    
    for result in results:
        driver_id = result.driver.driver_id
        team_id = result.constructor.constructor_id
        points = int(result.points)
        
        # Update driver and team wins if driver won
        if result.position == 1:
            update_driver_wins(driver_id, db, cursor)
            update_team_wins(team_id, db, cursor)

        update_driver(driver_id, db, cursor, points)
        update_team(team_id, db, cursor, points)

    cursor.execute('UPDATE current_season SET round = %s', (updated_round,))
    db.commit()
    cursor.close()

# Update driver's entry in database after new round
def update_driver(driver_id, db, cursor, round_points):
    cursor.execute('SELECT points FROM driver_profile WHERE driver_id = %s', (driver_id,))
    result = cursor.fetchone()
    old_points = result[0] if result else 0

    new_points = old_points + round_points

    cursor.execute('UPDATE driver_profile SET points = %s WHERE driver_id = %s', (new_points, driver_id))
    db.commit()

# Update team's entry in database after new round
def update_team(team_id, db, cursor, round_points):
    cursor.execute('SELECT points FROM team_profile WHERE team_id = %s', (team_id,))
    result = cursor.fetchone()
    old_points = result[0] if result else 0

    new_points = old_points + round_points

    cursor.execute('UPDATE team_profile SET points = %s WHERE team_id = %s', (new_points, team_id))
    db.commit()

# Update a driver if he won the round
def update_driver_wins(driver_id, db, cursor):
    cursor.execute('SELECT wins FROM driver_profile WHERE driver_id = %s', (driver_id,))
    result = cursor.fetchone()
    old_wins = result[0] if result else 0
    new_wins = old_wins + 1
    cursor.execute('UPDATE driver_profile SET wins = %s WHERE driver_id = %s', (new_wins, driver_id))
    db.commit()

# Update team if their driver won a round
def update_team_wins(team_id, db, cursor):
    cursor.execute('SELECT wins FROM team_profile WHERE team_id = %s', (team_id,))
    result = cursor.fetchone()
    old_wins = result[0] if result else 0
    new_wins = old_wins + 1
    cursor.execute('UPDATE team_profile SET wins = %s WHERE team_id = %s', (new_wins, team_id))
    db.commit()
