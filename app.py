from flask import Flask, render_template, request
from operator import itemgetter
import ergast_py
import asyncio
import aiohttp

app = Flask(__name__)

e = ergast_py.Ergast()

@app.route("/")
def index():
    return render_template("index.html")

# Driver standings
@app.route("/drivers", methods=["GET", "POST"])
def drivers(year=2024):
    if request.method == "POST":
        year = request.form.get("year", 2024, type=int)
    driver_standings = e.season(year).get_driver_standing().driver_standings
    print(driver_standings)
    return render_template("drivers.html", driver_standings = driver_standings, year = year, selected_year = year)

# Driver details
@app.route("/drivers/<string:driver_id>")
def driver_profile(driver_id):

    # Get driver data
    driver_profile = e.driver(f"{driver_id}").get_driver()

    return render_template("driver-profile.html", driver=driver_profile)

# Constructor standings
@app.route("/constructors", methods=["GET", "POST"])
def constructors(year=2024): 
    if request.method == "POST":
        year = request.form.get("year", 2024, type=int)
    constructor_standings = e.season(year).get_constructor_standing().constructor_standings
    return render_template("constructors.html", constructor_standings = constructor_standings, year = year, selected_year = year)

# Constructor details
@app.route("/constructors/<string:constructor_id>")
def constructor_profile(constructor_id):
    return "constructors works!"

# Race results
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