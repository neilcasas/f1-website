from flask import Flask, render_template, request
import ergast_py

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

    race_results = []
    # Get results for every circuit for that season
    season_circuits = e.season(year).get_circuits()
    
    # Append to race results list
    for circuit in season_circuits:
        try:
            race_results.append(e.season(year).circuit(circuit.circuit_id).get_result)
        except:
            continue
    return render_template("races.html", race_results = race_results, year = year, selected_year = year)