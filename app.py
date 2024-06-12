# save this as app.py
from flask import Flask, render_template, redirect
import ergast_py

app = Flask(__name__)

e = ergast_py.Ergast()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/drivers")
def drivers():
    return render_template("drivers.html")

@app.route("/constructors")
def constructors():
    return render_template("constructors.html")

@app.route("/races")
def races():
    return render_template("races.html")