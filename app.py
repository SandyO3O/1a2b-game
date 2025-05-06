from flask import Flask, render_template, request, redirect, url_for, session, send_file
import random, string, io, qrcode
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

games = {}

def generate_answer(length):
    return ''.join(random.choices(string.digits, k=length))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create_game():
    length = int(request.form.get('length', 6))
    game_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    games[game_id] = {
        'answer': generate_answer(length),
        'guesses': [],
        'length': length
    }
    return redirect(url_for('show_qr', game_id=game_id))

@app.route('/qr/<game_id>')
def show_qr(game_id):
    game_url = request.url_root.strip('/') + url_for('play_game', game_id=game_id)
    return render_template('qr.html', game_url=game_url, game_id=game_id)

@app.route('/qrcode/<game_id>')
def generate_qrcode(game_id):
    game_url = request.url_root.strip('/') + url_for('play_game', game_id=game_id)
    img = qrcode.make(game_url)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/game/<game_id>', methods=['GET', 'POST'])
def play_game(game_id):
    game = games.get(game_id)
    if not game:
        return "Game not found.", 404

    result = None
    if request.method == 'POST':
        guess = request.form['guess']
        answer = game['answer']
        a = sum(g == a for g, a in zip(guess, answer))
        b = sum(min(guess.count(d), answer.count(d)) for d in set(guess)) - a
        result = f"{a}A{b}B"
        game['guesses'].append((guess, result))

    return render_template('game.html', game_id=game_id, guesses=game['guesses'], result=result, length=game['length'])

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
