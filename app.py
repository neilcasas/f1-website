# save this as app.py
from flask import Flask, render_template, redirect
import ergast_py

app = Flask(__name__)

e = ergast_py.Ergast()

@app.route("/")
def hello():
    return render_template("layout.html")