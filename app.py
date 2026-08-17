from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudscraper
import re

app = Flask(__name__)
# GitHub Pages'ten gelen tüm isteklerin engellenmemesi için CORS izni
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

        # Chess.com Oyun ID'sini Regex ile Çekme
        match = re.search(r'live/(\d+)', game_url)
        if not match:
            return jsonify({'success': False, 'error': 'Invalid Chess.com link format!'}), 400

        game_id = match.group(1)

        # Chess.com API / Scrape İsteği
        # (Kendi özel algoritman/Stockfish analiz hesasplaman buraya bağlanır)
        # Örnek test hesabı/veri çekme simülasyonu:
        estimated_elo = 1500  # Buraya kendi Elo hesaplama fonksiyonunu bağlayabilirsin

        # 'elo' anahtarı eklendi, böylece ön yüz doğrudan rakamı okuyacak
        return jsonify({
            'success': True,
            'game_id': game_id,
            'elo': estimated_elo
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
