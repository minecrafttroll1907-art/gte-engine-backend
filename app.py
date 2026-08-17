from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudscraper
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

scraper = cloudscraper.create_scraper()

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'online', 'message': 'GTE Engine Backend is running!'})

@app.route('/api/get-elo', methods=['POST'])
def get_elo():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON payload provided'}), 400

        game_url = data.get('game_url', '').strip()
        if not game_url:
            return jsonify({'success': False, 'error': 'Please provide a valid Chess.com link!'}), 400

        # Chess.com canlı oyun ID'sini yakalama
        match = re.search(r'live/(\d+)', game_url)
        if not match:
            return jsonify({'success': False, 'error': 'Invalid Chess.com link format!'}), 400

        game_id = match.group(1)

        # Chess.com callback servisinden oyun detaylarını çekme
        api_url = f"https://www.chess.com/callback/live/game/{game_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        
        response = scraper.get(api_url, headers=headers)
        if response.status_code != 200:
            return jsonify({'success': False, 'error': 'Could not fetch game data from Chess.com'}), 400

        game_data = response.json()
        
        # Oyuncu bilgilerini çekip ortalama veya tahminî Elo'yu hesaplama mantığı
        game_info = game_data.get('game', {})
        white_rating = game_info.get('white', {}).get('rating', 1500)
        black_rating = game_info.get('black', {}).get('rating', 1500)
        
        # Burada VS Code'da kurduğumuz hesaplama algoritmasını uyguluyoruz
        estimated_elo = int((white_rating + black_rating) / 2)

        return jsonify({
            'success': True,
            'game_id': game_id,
            'elo': estimated_elo
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
