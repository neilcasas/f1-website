# save this as app.py
from flask import Flask, render_template, request
import ergast_py

app = Flask(__name__)

e = ergast_py.Ergast()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/drivers", methods=["GET", "POST"])
def drivers(year=2024):
    if request.method == "POST":
        year = request.form.get("year", 2024, type=int)
    driver_standings = e.season(year).get_driver_standing().driver_standings
    print(driver_standings)
    return render_template("drivers.html", driver_standings = driver_standings, year = year, selected_year = year)


@app.route("/constructors", methods=["GET", "POST"])
def constructors(year=2024): 
    if request.method == "POST":
        year = request.form.get("year", 2024, type=int)
    constructor_standings = e.season(year).get_constructor_standing().constructor_standings
    return render_template("constructors.html", constructor_standings = constructor_standings, year = year, selected_year = year)

@app.route("/races")
def races():
    return render_template("races.html")