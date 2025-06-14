from flask import Flask, request, jsonify, render_template
from treys import Evaluator, Card, Deck
import itertools, random

app = Flask(__name__)
evaluator = Evaluator()
SIMULATIONS = 1000

SUIT_SYMBOLS = {'s': '♠', 'h': '♥', 'd': '♦', 'c': '♣'}
SUIT_MAP = {v: k for k, v in SUIT_SYMBOLS.items()}

def convert_to_treys(cards):
    converted = []
    for card in cards:
        rank = card[:-1].replace("10", "T")
        suit = SUIT_MAP[card[-1]]
        converted.append(Card.new(rank + suit))
    return converted

def convert_to_symbol(card_str):
    rank = card_str[0] if card_str[1] != '0' else '10'
    suit_letter = card_str[-1].lower()
    return rank + SUIT_SYMBOLS.get(suit_letter, '?')

def simulate_best_combo(all_players_hands):
    best_combos = []
    for idx, hand in enumerate(all_players_hands):
        best_score = -1
        best_combo = []
        for combo in itertools.combinations(hand, 2):
            wins = 0
            for _ in range(SIMULATIONS):
                opponents = [convert_to_treys(random.sample(h, 2)) if i != idx else convert_to_treys(combo)
                             for i, h in enumerate(all_players_hands)]
                deck = Deck()
                for h in opponents:
                    for c in h:
                        if c in deck.cards:
                            deck.cards.remove(c)
                board = deck.draw(5)
                scores = [evaluator.evaluate(b, board) for b in opponents]
                best = min(scores)
                if scores[idx] == best and scores.count(best) == 1:
                    wins += 1
            win_rate = wins / SIMULATIONS
            if win_rate > best_score:
                best_score = win_rate
                best_combo = list(combo)
        readable = [convert_to_symbol(Card.int_to_str(c).replace("T", "10")) for c in best_combo]
        best_combos.append({'best_cards': readable, 'win_rate': round(best_score * 100, 2)})
    return best_combos

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bestcombo', methods=['POST'])
def best_combo():
    data = request.get_json()
    players = data.get('players', [])
    if not players or not all(len(p) == 3 for p in players):
        return jsonify({'error': 'invalid input'}), 400
    result = simulate_best_combo(players)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)