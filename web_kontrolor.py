from flask import Flask
import json
import os

app = Flask(__name__)

SETTINGS_FILE = "settings.json"

@app.route("/")
def zobraz_vystupy():
    if not os.path.exists(SETTINGS_FILE):
        return "<h2>⚠️ Soubor settings.json nebyl nalezen.</h2>"
    
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    rows = data.get("rows", [])
    if not rows:
        return "<h2>⚠️ Žádná data k zobrazení.</h2>"
    
    html = "<h2>📈 Výstupy TP/SL Kontrolátoru</h2><table border='1'><tr>"
    headers = rows[0].keys()
    
    for h in headers:
        html += f"<th>{h}</th>"
    html += "</tr>"
    
    for row in rows:
        html += "<tr>"
        for h in headers:
            html += f"<td>{row.get(h, '')}</td>"
        html += "</tr>"
    
    html += "</table>"
    return html

if __name__ == "__main__":
    app.run()
