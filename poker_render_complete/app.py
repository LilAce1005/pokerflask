
from flask import Flask, request, jsonify, render_template
from itertools import combinations
from treys import Card, Evaluator

app = Flask(__name__)

def parse_card(card_str):
    rank_str, suit_str = card_str[:-1], card_str[-1]
    suit_map = {'♣': 'c', '♠': 's', '♦': 'd', '♥': 'h'}
    rank_map = {'A': 'A', 'K': 'K', 'Q': 'Q', 'J': 'J',
                '10': 'T', '9': '9', '8': '8', '7': '7',
                '6': '6', '5': '5', '4': '4', '3': '3', '2': '2'}
    rank = rank_map[rank_str]
    suit = suit_map[suit_str]
    return Card.new(rank + suit)

def get_best_combo_winrate(hands):
    evaluator = Evaluator()
    results = []
    for i, hand in enumerate(hands):
        max_score = None
        best_combo = None
        this_cards = [parse_card(c) for c in hand]
        combos = list(combinations(this_cards, 2))
        scores = []
        for combo in combos:
            score = 0
            for j, other_hand in enumerate(hands):
                if i == j:
                    continue
                other_cards = [parse_card(c) for c in other_hand]
                other_combos = list(combinations(other_cards, 2))
                for ocombo in other_combos:
                    result = evaluator.evaluate(list(combo), list(ocombo))
                    if result < 0:
                        score += 1
            scores.append((combo, score))
        scores.sort(key=lambda x: -x[1])
        best = scores[0]
        best_cards = [Card.int_to_str(c) for c in best[0]]
        win_rate = round(best[1] / ((len(hands) - 1) * 3), 2)
        best_cards_display = []
        for card in hand:
            for b in best_cards:
                if card.replace("10", "T") in b:
                    best_cards_display.append(card)
                    break
        results.append({"best_cards": best_cards_display, "win_rate": win_rate})
    return results

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/bestcombo", methods=["POST"])
def bestcombo():
    data = request.get_json()
    players = data["players"]
    result = get_best_combo_winrate(players)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
