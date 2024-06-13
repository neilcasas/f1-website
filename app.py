from flask import Flask, render_template, request
import ergast_py
import asyncio
import aiohttp

app = Flask(__name__)

e = ergast_py.Ergast()

@app.route("/")
def index():
    print(e.get_races())
    return render_template("index.html")

@app.route("/drivers", methods=["GET", "POST"])
def drivers(year=2024):
    if request.method == "POST":
        year = request.form.get("year", 2024, type=int)
    driver_standings = e.season(year).get_driver_standing().driver_standings
    return render_template("drivers.html", driver_standings = driver_standings, year = year, selected_year = year)


@app.route("/constructors", methods=["GET", "POST"])
def constructors(year=2024): 
    if request.method == "POST":
        year = request.form.get("year", 2024, type=int)
    constructor_standings = e.season(year).get_constructor_standing().constructor_standings
    return render_template("constructors.html", constructor_standings = constructor_standings, year = year, selected_year = year)

@app.route("/races", methods=["GET", "POST"])
def races(year=2024):
    if request.method == "POST":
        year = request.form.get("year", 2024, type=int)
    
    race_results = asyncio.run(get_race_results(year))
    
    return render_template("races.html", race_results=race_results, year=year, selected_year=year)

async def fetch_race_result(session, year, circuit_id):
    url = f"https://ergast.com/api/f1/{year}/circuits/{circuit_id}/results.json?limit=5"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data['MRData']['RaceTable']['Races'][0] if data['MRData']['RaceTable']['Races'] else None
        return None

async def get_race_results(year):
    async with aiohttp.ClientSession() as session:
        tasks = []
        season_circuits = e.season(year).get_circuits()
        for circuit in season_circuits:
            tasks.append(fetch_race_result(session, year, circuit.circuit_id))
        
        race_results = await asyncio.gather(*tasks)
        return [result for result in race_results if result]