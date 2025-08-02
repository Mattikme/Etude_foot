# tools/generate_allowed_leagues.py

import requests
import yaml
from pathlib import Path

API_KEY = "e1e76b8e3emsh2445ffb97db0128p158afdjsnb3175ce8d916"  # 🔒 Place cette clé dans un fichier sécurisé ou .env
API_URL = "https://v3.football.api-sports.io/leagues"

TARGET_KEYWORDS = [
    "champions", "europa", "conference", "super cup", "ligue 1", "ligue 2",
    "bundesliga", "dfb pokal", "premier league", "championship", "efl cup",
    "community shield", "laliga", "copa del rey", "serie a", "serie b", "coppa italia",
    "cdm", "world cup", "can", "libertadores", "sudamericana", "leagues cup",
    "argentina", "brazil", "belgium", "croatia", "denmark", "scotland", "portugal",
    "netherlands", "turkey", "ukraine", "sweden", "switzerland", "greece",
    "poland", "czech", "romania", "slovakia", "slovenia", "bulgaria", "austria",
    "mexico", "usa", "mls", "japan", "korea", "china", "colombia", "chile", "paraguay",
    "ecuador", "saudi", "qatar", "norway", "finland", "ireland", "iceland", "wales",
    "northern ireland", "georgia", "estonia", "latvia", "lithuania", "luxembourg",
    "bosnia", "serbia", "hungary"
]

headers = {
    "x-apisports-key": API_KEY
}
response = requests.get(API_URL, headers=headers)
data = response.json()

filtered_leagues = []

for item in data.get("response", []):
    name = item["league"]["name"].lower()
    country = item["country"]["name"].lower()

    if any(keyword in name or keyword in country for keyword in TARGET_KEYWORDS):
        filtered_leagues.append({
            "id": item["league"]["id"],
            "name": item["league"]["name"],
            "country": item["country"]["name"],
            "season": item["seasons"][-1]["year"] if item.get("seasons") else None
        })

Path("config").mkdir(exist_ok=True)
with open("config/allowed_leagues_extracted.yaml", "w", encoding="utf-8") as f:
    yaml.dump(filtered_leagues, f, allow_unicode=True)

print(f"✅ {len(filtered_leagues)} ligues filtrées et enregistrées dans config/allowed_leagues_extracted.yaml")
