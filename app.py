# KryptoEwolucja Flask API – Rozszerzenie backendu o projekty Web3 z wyborem

from flask import Flask, jsonify, session, request
import random, json, os
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'krypto_secret'
CORS(app)

plansza = [
    "Start", "Szansa", "Projekt", "DAO", "Quiz", "Wsparcie", "Pułapka", "Premia", "MetaDAO",
    "Szansa", "DAO", "Quiz", "Projekt", "Wsparcie", "Pułapka", "Premia", "Szansa", "Quiz",
    "MetaDAO", "Projekt", "DAO", "Wsparcie", "Pułapka", "Premia", "Quiz", "Szansa", "Projekt",
    "MetaDAO", "Premia", "Start"
]

karty_projektowe = [
    {"nazwa": "Projekt NFT Marketplace", "tur_pozostalo": 3, "zwrot": 200},
    {"nazwa": "Platforma DeFi", "tur_pozostalo": 4, "zwrot": 250},
    {"nazwa": "Gra Web3", "tur_pozostalo": 2, "zwrot": 150},
    {"nazwa": "Portfel Mobilny", "tur_pozostalo": 3, "zwrot": 180},
    {"nazwa": "MetaDAO Community", "tur_pozostalo": 5, "zwrot": 300}
]

def nowy_gracz(imie, bot=False):
    return {"imie": imie, "poz": 0, "portfel": 1000, "projekty": [], "bot": bot}

@app.route("/start")
def start():
    session['gracze'] = [nowy_gracz("Ty"), nowy_gracz("Bot1", True)]
    session['tura'] = 0
    session['plansza'] = plansza
    session['ostatnia_karta'] = {}
    session['propozycje_projektow'] = []
    return jsonify({"message": "Gra rozpoczęta"})

@app.route("/projekty_dostepne")
def projekty_dostepne():
    propozycje = random.sample(karty_projektowe, 2)
    session['propozycje_projektow'] = propozycje
    return jsonify({"projekty": propozycje})

@app.route("/wybierz_projekt", methods=["POST"])
def wybierz_projekt():
    index = request.json.get("index")
    gracze = session.get("gracze", [])
    tura = session.get("tura", 0)
    gracz = gracze[(tura - 1) % len(gracze)]  # aktualny gracz to ten z ostatniego ruchu
    propozycje = session.get("propozycje_projektow", [])
    if 0 <= index < len(propozycje):
        gracz['projekty'].append(propozycje[index])
        efekt = f"Wybrano projekt {propozycje[index]['nazwa']}."
        session['ostatnia_karta'] = propozycje[index]
        session['gracze'] = gracze
        session['propozycje_projektow'] = []
        return jsonify({"message": efekt})
    return jsonify({"message": "Nieprawidłowy wybór."})

@app.route("/move", methods=["POST"])
def move():
    gracze = session.get("gracze", [])
    tura = session.get("tura", 0)
    gracz = gracze[tura % len(gracze)]
    rzut = random.randint(1, 6)
    gracz['poz'] = (gracz['poz'] + rzut) % len(plansza)
    pole = plansza[gracz['poz']]
    efekt = ""
    karta = {}

    for p in gracz['projekty']:
        p['tur_pozostalo'] -= 1
    zwroty = [p for p in gracz['projekty'] if p['tur_pozostalo'] <= 0]
    for z in zwroty:
        gracz['portfel'] += z['zwrot']
        efekt += f" Projekt {z['nazwa']} zakończony: +{z['zwrot']} zł."
        gracz['projekty'].remove(z)

    if pole == "Projekt":
        efekt += " Wybierz jeden z dostępnych projektów."

    session['gracze'] = gracze
    session['tura'] = tura + 1
    session['ostatnia_karta'] = karta
    return jsonify({"gracz": gracz, "rzut": rzut, "pole": pole, "efekt": efekt})

@app.route("/get_state")
def get_state():
    return jsonify({
        "gracze": session.get("gracze", []),
        "plansza": session.get("plansza", plansza),
        "ostatnia_karta": session.get("ostatnia_karta", {}),
        "propozycje_projektow": session.get("propozycje_projektow", [])
    })

@app.route("/save_game", methods=["POST"])
def save_game():
    stan = {
        "gracze": session.get("gracze", []),
        "plansza": session.get("plansza", plansza),
        "tura": session.get("tura", 0),
        "ostatnia_karta": session.get("ostatnia_karta", {}),
        "propozycje_projektow": session.get("propozycje_projektow", [])
    }
    with open("save_game.json", "w") as f:
        json.dump(stan, f)
    return jsonify({"message": "Gra zapisana."})

@app.route("/load_game")
def load_game():
    try:
        with open("save_game.json") as f:
            stan = json.load(f)
        session['gracze'] = stan['gracze']
        session['plansza'] = stan['plansza']
        session['tura'] = stan['tura']
        session['ostatnia_karta'] = stan['ostatnia_karta']
        session['propozycje_projektow'] = stan.get('propozycje_projektow', [])
        return jsonify({"message": "Gra wczytana."})
    except Exception as e:
        return jsonify({"message": f"Błąd: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
