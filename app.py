import requests
import os
from dotenv import load_dotenv
from flask import Flask, render_template
load_dotenv()

API_KEY= os.getenv("API_KEY")

headers = {
    "X-Auth-Token": API_KEY
}


api_key = os.getenv("API_KEY")

BASE_URL = "https://api.football-data.org/v4/"
app = Flask(__name__)

def get_comps():
    url = f"{BASE_URL}competitions"
    response=requests.get(url,headers=headers)

    if response.status_code == 200:
        print("Data Retrieved")
        comp_data=response.json()
        comp_info=comp_data["competitions"]
        return [
            {
            "name":comp["name"],
            "code":comp["code"],
            "type":comp["type"]
            }
            for comp in comp_info
            if comp["type"] == "LEAGUE" and comp["code"] is not None
        ]
    else: 
        print(f"Failed to retrieve data {response.status_code}")
        return None

def get_matches(id):
    url = f"{BASE_URL}competitions/{id}/matches"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        match_data = response.json()
        match_info = match_data["matches"]
        match_info.sort(key=lambda x: x["utcDate"], reverse=True)  # latest first
        return [
            {
                "Comp": match["competition"]["name"],
                "Home-Team": match["homeTeam"]["shortName"],
                "Away-Team": match["awayTeam"]["shortName"],
                "Score": f'{match["score"]["fullTime"]["home"]} - {match["score"]["fullTime"]["away"]}',
                "Status": match["status"],
                "Date": match["utcDate"][:10],
                "Goals": [
                    {
                        "minute": goal["minute"],
                        "scorer": goal["scorer"]["name"],
                        "team": goal["team"]["name"]
                    }
                    for goal in match.get("goals", [])
                ]
            }
            for match in match_info
        ]
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None

def get_standings(id):
    url = f"{BASE_URL}competitions/{id}/standings"
    response=requests.get(url,headers=headers)

    if response.status_code ==200:
        print("Data Retrieved")
        standings_data=response.json()
        standings_info=standings_data["standings"]
        league_table=standings_info[0]["table"]
        return [
            {
                "team_id": league["team"]["id"],
                "position": league["position"],
                "team": league["team"]["shortName"],
                "PG": league["playedGames"],
                "Won": league["won"],
                "Draw": league["draw"],
                "Lost": league["lost"],
                "Points": league["points"],
                "GF": league["goalsFor"],
                "GA": league["goalsAgainst"],
                "GD": league["goalDifference"]

            }
            for league in league_table
        ]
    else: 
        print(f"Failed to retrieve data: {response.status_code}")
        return None
    
def get_teams(id):
    url =  f"{BASE_URL}competitions/{id}/teams"
    response=requests.get(url,headers=headers)

    if response.status_code == 200: 
        print("Data Retrieved")
        teams_data=response.json()
        teams_info=teams_data["teams"]

        return [
            {
                "name": team["name"],
                "website": team["website"]
            }
            for team in teams_info
            ]
    else:
        print(f"Failed to retrieve data {response.status_code}")

def get_team_info(id):
    url = f"{BASE_URL}teams/{id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        team_data = response.json()
        return {
            "crest": team_data["crest"],
            "id": team_data["id"],
            "name": team_data["name"],
            "coach": team_data["coach"]["firstName"],
            "founded": team_data["founded"],
            "venue": team_data["venue"],
            "address": team_data["address"],
            "website": team_data["website"]
        }
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None

#Flask
@app.route("/")
def index():
    comps = get_comps()
    return render_template("index.html", comps=comps)

@app.route("/standings/<id>")
def standings(id):
    table = get_standings(id)
    return render_template("standings.html", table=table, id=id)

@app.route("/matches/<id>")
def matches(id):
    match_list = get_matches(id)
    if match_list is None:
        return "Matches not available", 404
    return render_template("matches.html", matches=match_list, id=id)

@app.route("/team/<id>")
def team(id):
    team_info = get_team_info(id)
    if team_info is None:
        return "Team not found", 404
    return render_template("team.html", team=team_info)

if __name__ == "__main__":
    app.run(debug=True)


