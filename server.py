from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime
import os

app = Flask(__name__)

nustatymai = {
    1: {
        "id": 1,
        "name": "Elektrine 1",
        "vietove": "Valmantiskiai",
        "jautrumas": 50,
        "uzdelsimasSek": 5,
        "infoRinkimasMin": 3,
        "maxVejas": 15,
        "stabdo": True,
        "rankinis": False,
        "kampas": 0,
        "status": "online"
    },
    2: {
        "id": 2,
        "name": "Elektrine 2",
        "vietove": "Eugenijaus",
        "jautrumas": 70,
        "uzdelsimasSek": 2,
        "infoRinkimasMin": 1,
        "maxVejas": 20,
        "stabdo": True,
        "rankinis": False,
        "kampas": 0,
        "status": "online"
    },
    3: {
        "id": 3,
        "name": "Elektrine 3",
        "vietove": "Sadausko",
        "jautrumas": 30,
        "uzdelsimasSek": 10,
        "infoRinkimasMin": 5,
        "maxVejas": 18,
        "stabdo": False,
        "rankinis": True,
        "kampas": 270,
        "status": "standby"
    }
}

busena = {
    1: {"galia": 0, "temp": 0, "hum": 0, "apkrova": 0, "paskCartasOnline": None},
    2: {"galia": 0, "temp": 0, "hum": 0, "apkrova": 0, "paskCartasOnline": None},
    3: {"galia": 0, "temp": 0, "hum": 0, "apkrova": 0, "paskCartasOnline": None},
}

def log(tekstas):
    laika = datetime.now().strftime("%H:%M:%S")
    print(f"[{laika}] {tekstas}")

@app.route("/")
def index():
    if os.path.exists("index.html"):
        return send_from_directory(".", "index.html")
    return "<h2>Serveris veikia!</h2>"

@app.route("/api/settings", methods=["GET"])
def gauti_visus():
    return jsonify(list(nustatymai.values()))

@app.route("/api/settings/<int:nr>", methods=["GET"])
def gauti_viena(nr):
    if nr not in nustatymai:
        return jsonify({"klaida": "Elektrine nerasta"}), 404
    log(f"GET /api/settings/{nr}")
    return jsonify(nustatymai[nr])

@app.route("/api/settings/<int:nr>", methods=["POST"])
def atnaujinti(nr):
    if nr not in nustatymai:
        return jsonify({"klaida": "Elektrine nerasta"}), 404
    duomenys = request.get_json()
    if not duomenys:
        return jsonify({"klaida": "Nera duomenu"}), 400
    leistini = ["jautrumas","uzdelsimasSek","infoRinkimasMin","maxVejas","stabdo","rankinis","kampas","status"]
    for laukas in leistini:
        if laukas in duomenys:
            nustatymai[nr][laukas] = duomenys[laukas]
    log(f"POST /api/settings/{nr} -> {duomenys}")
    return jsonify({"ok": True, "nustatymai": nustatymai[nr]})

@app.route("/api/status/<int:nr>", methods=["POST"])
def gauti_busena(nr):
    if nr not in busena:
        return jsonify({"klaida": "Elektrine nerasta"}), 404
    duomenys = request.get_json()
    if duomenys:
        busena[nr].update(duomenys)
        busena[nr]["paskCartasOnline"] = datetime.now().strftime("%H:%M:%S")
        log(f"STATUS {nr} <- {duomenys}")
    return jsonify({"ok": True})

@app.route("/api/status", methods=["GET"])
def visu_busena():
    return jsonify(busena)

@app.route("/api/komanda/<int:nr>", methods=["POST"])
def komanda(nr):
    if nr not in nustatymai:
        return jsonify({"klaida": "Elektrine nerasta"}), 404
    duomenys = request.get_json()
    veiksmas = duomenys.get("veiksmas") if duomenys else None
    if veiksmas == "stop":
        nustatymai[nr]["rankinis"] = True
        nustatymai[nr]["kampas"] = 0
    elif veiksmas == "vakarus":
        nustatymai[nr]["rankinis"] = True
        nustatymai[nr]["kampas"] = 90
    elif veiksmas == "rytus":
        nustatymai[nr]["rankinis"] = True
        nustatymai[nr]["kampas"] = 270
    elif veiksmas == "auto":
        nustatymai[nr]["rankinis"] = False
    else:
        return jsonify({"klaida": f"Nezinomas veiksmas: {veiksmas}"}), 400
    log(f"KOMANDA {nr}: {veiksmas}")
    return jsonify({"ok": True})

if __name__ == "__main__":
    print("=" * 45)
    print("  Elektriniu valdymo serveris")
    print("  http://localhost:5000")
    print("=" * 45)
    app.run(host="0.0.0.0", port=5000, debug=False)