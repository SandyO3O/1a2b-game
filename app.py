from flask import Flask, render_template, request, redirect, url_for
import random, string, qrcode, io, base64

app = Flask(__name__)
games = {}

# 隨機產生遊戲代碼
def generate_code(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# 產生題目
def generate_answer(length=4):
    return ''.join(random.choices('0123456789', k=length))

# 計算幾A幾B
def get_hint(answer, guess):
    A = sum(a == b for a, b in zip(answer, guess))
    B = sum(min(answer.count(d), guess.count(d)) for d in set(guess)) - A
    return f"{A}A{B}B"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create_game():
    length = int(request.form.get('length', 4))
    code = generate_code()
    answer = generate_answer(length)
    games[code] = {'answer': answer, 'guesses': [], 'length': length}
    return redirect(url_for('game', room_code=code))

@app.route('/game/<room_code>', methods=['GET', 'POST'])
def game(room_code):
    game = games.get(room_code)
    if not game:
        return "找不到這個遊戲代碼", 404

    # 產生 QR code 並轉成 base64
    game_url = request.url_root.strip('/') + url_for('game', room_code=room_code)
    img = qrcode.make(game_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_code_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

    if request.method == 'POST':
        name = request.form.get('name', '').strip() or '匿名'
        guess = request.form.get('guess', '').strip()

        if len(guess) == game['length'] and guess.isdigit():
            hint = get_hint(game['answer'], guess)
            game['guesses'].append({'name': name, 'guess': guess, 'hint': hint})

    return render_template('game.html',
                           room_code=room_code,
                           guesses=game['guesses'],
                           qr_code_url=qr_code_url,
                           length=game['length'])

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

