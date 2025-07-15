from flask import Flask, render_template
import requests
import os
from dotenv import load_dotenv
import re, base64
import base64
load_dotenv()

app = Flask(__name__)

@app.route('/gallery')
def gallery():
    owner = 'GarvKapoor'
    repo = 'ecom-pics'
    token = os.getenv('GITHUB_TOKEN')

    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/'
    headers = {'Authorization': f'token {token}'}

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        images = []
        for file in data:
            if file['name'].lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raw_url = file['download_url']
                images.append(raw_url)
    else:
        images = []

    return render_template('gallery.html', images=images)

@app.route('/')
def home():
    return gallery()

if __name__ == '__main__':
    app.run(debug=True)
    
@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    sizes = data.get('sizes')
    image_base64 = data.get('image_base64')

    if not all([name, price, sizes, image_base64]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Format filename
    filename = f"{name}_{price}_{sizes.replace(',', '_')}"
    # Try to detect image extension from base64 header
    
    match = re.match(r'^data:image/(\w+);base64,', image_base64)
    if match:
        ext = match.group(1)
        image_data = base64.b64decode(image_base64.split(',')[1])
    else:
        ext = 'png'  # default
        image_data = base64.b64decode(image_base64)
    filename = f"{filename}.{ext}"

    owner = 'GarvKapoor'
    repo = 'ecom-pics'
    token = os.getenv('GITHUB_TOKEN')
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{filename}'
    headers = {'Authorization': f'token {token}'}

    
    content_b64 = base64.b64encode(image_data).decode('utf-8')
    payload = {
        'message': f'Add {filename}',
        'content': content_b64
    }
    response = requests.put(api_url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        return jsonify({'success': True, 'filename': filename}), 201
    else:
        return jsonify({'error': response.json()}), response.status_code    
