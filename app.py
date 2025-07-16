from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv
import re
import base64

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# ===========================
# Helper function to parse product info from filename
# ===========================
def parse_product_info(filename):
    """
    Parse product information from filename format: {name}_{price}_{sizes}.{ext}
    Example: "Reyon_Fabric_Kaftans_1095_S_500_M_700_L_800.jpg"
    """
    try:
        # Remove file extension
        name_without_ext = filename.rsplit('.', 1)[0]
        
        # Split by underscores
        parts = name_without_ext.split('_')
        
        if len(parts) < 3:
            # Fallback for malformed filenames
            return {
                'name': 'Unknown Product',
                'price': '0',
                'sizes': []
            }
        
        # Find the price (first numeric part after product name)
        price_index = -1
        for i, part in enumerate(parts):
            if part.isdigit():
                price_index = i
                break
        
        if price_index == -1:
            # No price found, use defaults
            name = ' '.join(parts)
            price = '0'
            sizes = []
        else:
            # Extract name (everything before price)
            name = ' '.join(parts[:price_index])
            price = parts[price_index]
            
            # Extract sizes (everything after price)
            size_parts = parts[price_index + 1:]
            sizes = []
            
            # Parse sizes in format: S, 500, M, 700, L, 800
            for i in range(0, len(size_parts), 2):
                if i + 1 < len(size_parts):
                    size_label = size_parts[i]
                    size_price = size_parts[i + 1]
                    if size_price.isdigit():
                        sizes.append({
                            'label': size_label,
                            'price': size_price
                        })
        
        return {
            'name': name,
            'price': price,
            'sizes': sizes
        }
    except Exception as e:
        # Fallback for any parsing errors
        return {
            'name': filename.rsplit('.', 1)[0],
            'price': '0',
            'sizes': []
        }

# ===========================
# Home route redirects to gallery
# ===========================
@app.route('/')
def home():
    return gallery()

# ===========================
# Gallery route to list images from GitHub repo
# ===========================
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
                # Parse product information from filename
                filename = file['name']
                product_info = parse_product_info(filename)
                product_info['image_url'] = file['download_url']
                images.append(product_info)
    else:
        images = []

    return render_template('gallery.html', images=images)

# ===========================
# Upload route to upload image to GitHub repo
# ===========================
@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    sizes = data.get('sizes')
    image_base64 = data.get('image_base64')

    # ✅ Check required fields
    if not all([name, price, sizes, image_base64]):
        return jsonify({'error': 'Missing required fields'}), 400

    # ✅ Validate sizes format: expect comma-separated list like "S:500,M:700"
    try:
        for item in sizes.split(','):
            size_label, size_price = item.split(':')
            float(size_price)  # ensure it's a number
    except Exception:
        return jsonify({'error': 'Invalid sizes format. Expected: S:500,M:700'}), 400

    # ✅ Sanitize sizes for filename (remove special characters)
    safe_sizes = re.sub(r'[^a-zA-Z0-9_]', '_', sizes)
    filename_base = f"{name}_{price}_{safe_sizes}"

    # ✅ Detect extension from base64 header
    match = re.match(r'^data:image/(\w+);base64,', image_base64)
    if match:
        ext = match.group(1)
        image_data = base64.b64decode(image_base64.split(',')[1])
    else:
        ext = 'png'  # Default to PNG if header is missing
        image_data = base64.b64decode(image_base64)

    # ✅ Debug: Log image size
    print(f"Uploading image of size: {len(image_data) / 1024:.2f} KB")

    filename = f"{filename_base}.{ext}"

    # ✅ GitHub Upload
    owner = 'GarvKapoor'
    repo = 'ecom-pics'
    token = os.getenv('GITHUB_TOKEN')

    if not token:
        return jsonify({'error': 'GitHub token not set'}), 500

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
        error_info = response.json().get('message', 'Unknown GitHub error')
        return jsonify({'error': f'GitHub upload failed: {error_info}'}), response.status_code

# ===========================
# Run locally (development only)
# In production, use gunicorn via Procfile:
# web: gunicorn app:app
# ===========================
if __name__ == '__main__':
    app.run(debug=True)
