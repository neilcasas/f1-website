from flask import Flask, render_template, request
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
        host="localhost",
        user="root",
        password="Password1!",
        database="mode_push"
    )

@app.route("/")
def index():
    return render_template("index.html")

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
    mycursor.execute("SELECT first_year, last_year, points, wins, championships FROM driver_profile WHERE driver_id = %s", (driver_id,))
    result = mycursor.fetchone()
    first_year, last_year, points, wins, championships = result if result else (None, None, 0, 0, 0)
    driver_db_data = {"first_year": first_year, "last_year": last_year, "points": points, "wins": wins, "championships": championships}

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
    mycursor.execute("SELECT first_year, last_year, points, wins, championships FROM team_profile WHERE team_id = %s", (constructor_id,))
    result = mycursor.fetchone()
    first_year, last_year, points, wins, championships = result if result else (None, None, 0, 0, 0)
    constructor_db_data = {"first_year": first_year, "last_year": last_year, "points": points, "wins": wins, "championships": championships}

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

# TODO: Add news api for homepage
# TODO: Add pictures for constructors and drivers
# TODO: Fix bugs for some drivers profiles returning more than one query