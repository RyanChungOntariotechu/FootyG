import requests
from flask import Flask, render_template

app = Flask(__name__)

headers = {"X-Auth-Token": "{API_KEY}"}
BASE_URL = "https://api.football-data.org/v4/"

def league_display():
    url = f"{BASE_URL}competitions/"
    response = requests.get(url, headers=headers)
    data = response.json()
    competitions = data["competitions"]

    leagues = [item for item in competitions if item["type"] == "LEAGUE"]
    cups = [item for item in competitions if item["type"] != "LEAGUE"]

    return leagues, cups

@app.route("/")
def home():
    leagues, cups = league_display()
    return render_template("index.html", leagues=leagues, cups=cups)

if __name__ == "__main__":
    app.run(debug=True)
