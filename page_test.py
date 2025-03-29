import json
with open("fraud_keywords.json", "r", encoding="utf-8") as f:
    keywords = json.load(f)
keywords = [keywords[i][0] for i in range(len(keywords))]
print(keywords)
