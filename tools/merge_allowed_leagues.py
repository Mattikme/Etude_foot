import yaml

with open("config/allowed_leagues.yaml", "r") as f:
    base = yaml.safe_load(f)

with open("config/allowed_leagues_extracted.yaml", "r") as f:
    extracted = yaml.safe_load(f)

merged = {}

# fusionne les 2 dicts pays => [ligues]
for country in set(base.keys()) | set(extracted.keys()):
    merged[country] = sorted(set(base.get(country, []) + extracted.get(country, [])))

with open("config/allowed_leagues_merged.yaml", "w") as f:
    yaml.dump(merged, f, allow_unicode=True)

print("✅ Fichier fusionné : config/allowed_leagues_merged.yaml")
