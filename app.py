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
    
    Examples:
    - "Reyon_Fabric_Kaftans_1095_S_500_M_700_L_800.jpg"
    - "Cotton_Shirt_899_S_899_M_999_L_1099.png"
    - "Simple_Dress_1500_OneSize_1500.jpg"
    - "Denim_Jacket_2000_M_2000_L_2200_XL_2400.png"
    """
    try:
        # Remove file extension
        name_without_ext = filename.rsplit('.', 1)[0]
        
        # Split by underscores
        parts = name_without_ext.split('_')
        
        if len(parts) < 2:
            # Fallback for malformed filenames
            return {
                'name': filename.rsplit('.', 1)[0],
                'price': '0',
                'sizes': []
            }
        
        # Strategy: Find the first numeric part which should be the base price
        # Then parse alternating size labels and prices after that
        base_price_index = -1
        
        # Look for the first numeric part (this should be the base price)
        for i, part in enumerate(parts):
            if part.isdigit():
                base_price_index = i
                break
        
        if base_price_index == -1:
            # No numeric parts found, treat as name only
            return {
                'name': ' '.join(parts),
                'price': '0',
                'sizes': []
            }
        
        # Extract product name (everything before base price)
        name = ' '.join(parts[:base_price_index])
        base_price = parts[base_price_index]
        
        # Extract sizes (everything after base price)
        size_parts = parts[base_price_index + 1:]
        sizes = []
        
        # Parse sizes in alternating format: size_label, size_price, size_label, size_price...
        i = 0
        while i < len(size_parts):
            if i + 1 < len(size_parts):
                size_label = size_parts[i]
                size_price = size_parts[i + 1]
                
                # Check if the next part is a price (numeric)
                if size_price.isdigit():
                    sizes.append({
                        'label': size_label,
                        'price': size_price
                    })
                    i += 2
                else:
                    # If not a price, treat current part as size with base price
                    sizes.append({
                        'label': size_label,
                        'price': base_price
                    })
                    i += 1
            else:
                # Odd number of parts, treat last part as size with base price
                sizes.append({
                    'label': size_parts[i],
                    'price': base_price
                })
                i += 1
        
        # If no sizes found, create a default "One Size" entry
        if not sizes:
            sizes.append({
                'label': 'One Size',
                'price': base_price
            })
        
        return {
            'name': name if name else 'Unknown Product',
            'price': base_price,
            'sizes': sizes
        }
        
    except Exception as e:
        # Fallback for any parsing errors
        print(f"Error parsing filename '{filename}': {e}")
        return {
            'name': filename.rsplit('.', 1)[0],
            'price': '0',
            'sizes': [{'label': 'One Size', 'price': '0'}]
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
