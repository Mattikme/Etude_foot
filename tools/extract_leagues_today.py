import requests
import datetime
import yaml

API_KEY = "e1e76b8e3emsh2445ffb97db0128p158afdjsnb3175ce8d916"
headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
url = f"https://v3.football.api-sports.io/fixtures?date={today}"
response = requests.get(url, headers=headers)

leagues_by_country = {}
if response.status_code == 200:
    data = response.json().get("response", [])
    for fixture in data:
        league = fixture["league"]
        country = league["country"]
        name = league["name"]
        leagues_by_country.setdefault(country, set()).add(name)

cleaned = {k: sorted(list(v)) for k, v in leagues_by_country.items()}
with open("config/allowed_leagues_extracted.yaml", "w") as f:
    yaml.dump(cleaned, f, allow_unicode=True)

print("✅ Fichier saved: config/allowed_leagues_extracted.yaml")
