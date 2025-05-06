from flask import Flask, render_template, request, redirect, url_for
import random
import qrcode
import os

app = Flask(__name__)

games = {}

def generate_answer(length):
    return ''.join(random.choices('0123456789', k=length))

def generate_game_id():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))

def check_guess(answer, guess):
    A = sum(a == b for a, b in zip(answer, guess))
    B = sum(min(answer.count(d), guess.count(d)) for d in set(guess)) - A
    return f"{A}A{B}B"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new_game', methods=['POST'])
def new_game():
    length = int(request.form.get('length', 6))
    game_id = generate_game_id()
    answer = generate_answer(length)

    games[game_id] = {
        "answer": answer,
        "length": length,
        "guesses": []
    }

    # 產生 QR code
    join_url = request.url_root + 'game/' + game_id
    qr = qrcode.make(join_url)
    filename = f'{game_id}.png'
    filepath = os.path.join('static', filename)
    qr.save(filepath)

    return redirect(url_for('game', game_id=game_id))

@app.route('/game/<game_id>', methods=['GET', 'POST'])
def game(game_id):
    game = games.get(game_id)
    if not game:
        return "❌ 無效的遊戲代碼", 404

    answer = game["answer"]
    length = game["length"]
    guesses = game["guesses"]
    message = ''
    guess = ''
    name = ''

    if request.method == 'POST':
        guess = request.form['guess']
        name = request.form.get('name', '匿名').strip() or '匿名'

        if len(guess) != length or not guess.isdigit():
            message = f"請輸入 {length} 位數字"
        else:
            result = check_guess(answer, guess)
            message = result
            guesses.append({
                "name": name,
                "guess": guess,
                "result": result
            })
            if result == f"{length}A0B":
                message += " 🎉 恭喜答對！"

    return render_template('game.html', game_id=game_id, guess=guess, message=message,
                           guesses=guesses, length=length)

if __name__ == '__main__':
    app.run(debug=True)
