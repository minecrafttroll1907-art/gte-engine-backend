from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudscraper
import re

app = Flask(__name__)
CORS(app)

scraper = cloudscraper.create_scraper()

@app.route('/api/get-elo', methods=['POST'])
def get_elo():
    data = request.get_json()
    game_url = data.get('game_url', '')

    match = re.search(r'live/(\d+)', game_url)
    if not match:
        return jsonify({'success': False, 'error': 'Geçersiz Chess.com linki!'})
    
    game_id = match.group(1)

    try:
        api_url = f"https://www.chess.com/callback/live/game/{game_id}"
        res = scraper.get(api_url)

        if res.status_code != 200:
            return jsonify({'success': False, 'error': 'Chess.com verisi alınamadı.'})

        game_data = res.json()
        players = game_data.get('players', {})

        # 'top' ve 'bottom' objelerinden ELO'ları çekiyoruz
        top_rating = players.get('top', {}).get('rating')
        bottom_rating = players.get('bottom', {}).get('rating')

        if top_rating and bottom_rating:
            average_elo = round((top_rating + bottom_rating) / 2)
            return jsonify({'success': True, 'average_elo': average_elo})
        else:
            return jsonify({'success': False, 'error': 'Oyuncu ratingleri bulunamadı.'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)