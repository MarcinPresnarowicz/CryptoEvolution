from flask import Flask, request, jsonify, session
from flask_cors import CORS
import random

app = Flask(__name__)
app.secret_key = "tajny_klucz"  # Do trzymania sesji
CORS(app)

# === Dane gry ===
kategorie_kart = {
    "DAO": [
        ("Publiczny airdrop", "+50 zl dla kazdego gracza"),
        ("Zakaz handlu DOGE", "Nie mozna kupowac DOGE do konca gry"),
        ("Podatek Web3", "Kazdy projekt Web3 traci 20 zl")
    ],
    "Quiz": [
        ("Co to jest Proof of Stake?", "Mechanizm zatwierdzania blokow przez staking tokenow"),
        ("Czym jest DAO?", "Zdecentralizowana organizacja zarzadzana smart kontraktami"),
        ("Czym jest NFT?", "Token niewymienialny, unikalny zasob cyfrowy")
    ],
    "Szansa": [
        ("ATH Bitcoina", "+50 zl dla posiadaczy BTC"),
        ("Hack giełdy", "Strata 50 zl (chyba ze masz zabezpieczenia)"),
        ("Airdrop tokenow", "+30 zl bonusowych tokenow")
    ],
    "Wsparcie": [
        ("Mentor Web3 pomaga ci za darmo", "+1 reputacja"),
        ("Nagroda społeczności DAO", "+1 GOV token")
    ]
}

pola_planszy = [
    "Start", "Szansa", "DAO", "Quiz", "Wsparcie", "Projekt",
    "Szansa", "DAO", "Quiz", "Projekt", "Szansa", "DAO",
    "Wsparcie", "Quiz", "Projekt", "Szansa", "DAO", "Projekt",
    "Szansa", "Quiz", "DAO", "Wsparcie", "Projekt", "Szansa",
    "Quiz", "DAO", "Projekt", "Wsparcie", "Szansa", "Quiz",
    "DAO", "Projekt", "Szansa", "Quiz", "Wsparcie", "DAO",
    "Projekt", "Quiz", "Szansa", "MetaDAO"
]

# === API ===
@app.route("/start_game", methods=["POST"])
def start_game():
    data = request.json
    session["gracze"] = [
        {"imie": g["imie"], "gotowka": 1000, "gov_tokeny": 0, "reputacja": 0, "projekty": [], "poz": 0}
        for g in data["gracze"]
    ]
    session["tura"] = 1
    session["poziom"] = data.get("poziom", "szkola")
    return jsonify({"message": "Gra rozpoczęta"})

@app.route("/get_state")
def get_state():
    return jsonify({
        "gracze": session.get("gracze", []),
        "tura": session.get("tura", 1),
        "plansza": pola_planszy
    })

@app.route("/move", methods=["POST"])
def move():
    gracze = session.get("gracze", [])
    tura = session.get("tura", 1)
    poziom = session.get("poziom", "szkola")
    aktualny = gracze[(tura - 1) % len(gracze)]

    rzut = random.randint(1, 6)
    aktualny["poz"] = (aktualny["poz"] + rzut) % len(pola_planszy)
    pole = pola_planszy[aktualny["poz"]]
    efekt = ""

    if pole in kategorie_kart:
        karta = random.choice(kategorie_kart[pole])
        efekt = karta[1]
        if "+50 zl" in efekt:
            aktualny["gotowka"] += 50
        elif "Strata 50 zl" in efekt:
            aktualny["gotowka"] -= 50
        elif "+1 reputacja" in efekt:
            aktualny["reputacja"] += 1
        elif "+1 GOV token" in efekt:
            aktualny["gov_tokeny"] += 1

    session["gracze"][(tura - 1) % len(gracze)] = aktualny
    session["tura"] = tura + 1

    return jsonify({
        "gracz": aktualny,
        "pole": pole,
        "rzut": rzut,
        "efekt": efekt
    })

if __name__ == "__main__":
    app.run(debug=True)

