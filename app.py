from flask import Flask, request, jsonify, render_template, session
import requests
import os
from dotenv import load_dotenv
import re
import base64
from datetime import datetime
import uuid

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Add this to .env file

# ===========================
# Helper function to parse product info from filename
# ===========================
def parse_product_info(filename):
    """
    Parse product information from filename format: {name}_{size1}_{price1}_{size2}_{price2}...{ext}

    Examples:
    - "Beach_S_200_M_300_L_500.jpeg"
    - "Cotton_Shirt_S_899_M_999_L_1099.png"
    - "Simple_Dress_OneSize_1500.jpg"
    - "Denim_Jacket_M_2000_L_2200_XL_2400.png"
    """
    try:
        # Remove file extension
        name_without_ext = filename.rsplit('.', 1)[0]

        # Split by underscores
        parts = name_without_ext.split('_')

        if len(parts) < 3:
            # Fallback for malformed filenames (need at least name, size, price)
            return {
                'name': filename.rsplit('.', 1)[0],
                'price': '0',
                'sizes': [{'label': 'One Size', 'price': '0'}]
            }

        # Strategy: Find the first numeric part - this indicates where sizes start
        # Everything before first numeric part is the product name
        first_price_index = -1

        # Look for the first numeric part (this should be the first price)
        for i, part in enumerate(parts):
            if part.isdigit():
                first_price_index = i
                break

        if first_price_index == -1 or first_price_index == 0:
            # No numeric parts found or starts with number, treat as name only
            return {
                'name': ' '.join(parts),
                'price': '0',
                'sizes': [{'label': 'One Size', 'price': '0'}]
            }

        # Extract product name (everything before first price)
        # The part before first price should be the size label
        name_parts = parts[:first_price_index - 1]  # -1 because the part before price is size label
        name = ' '.join(name_parts) if name_parts else 'Unknown Product'

        # Extract sizes starting from the first size label
        size_parts = parts[first_price_index - 1:]  # Include the size label before first price
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
                    # If not a price, something is wrong, skip this part
                    i += 1
            else:
                # Odd number of parts, skip the last part
                i += 1

        # If no sizes found, create a default "One Size" entry with 0 price
        if not sizes:
            sizes.append({
                'label': 'One Size',
                'price': '0'
            })

        # Set the base price to the first size's price or 0
        base_price = sizes[0]['price'] if sizes else '0'

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
# Cart Management Routes
# ===========================

def init_cart():
    """Initialize cart in session if it doesn't exist"""
    if 'cart' not in session:
        session['cart'] = []
    return session['cart']

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    data = request.get_json()

    required_fields = ['name', 'size', 'price', 'image_url']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    cart = init_cart()

    # Create cart item
    cart_item = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'size': data['size'],
        'price': float(data['price']),
        'image_url': data['image_url'],
        'quantity': int(data.get('quantity', 1)),
        'selected': True,  # Default to selected
        'added_at': datetime.now().isoformat()
    }

    # Check if item already exists (same name and size)
    existing_item = None
    for item in cart:
        if item['name'] == cart_item['name'] and item['size'] == cart_item['size']:
            existing_item = item
            break

    if existing_item:
        # Update quantity of existing item
        existing_item['quantity'] += cart_item['quantity']
    else:
        # Add new item to cart
        cart.append(cart_item)

    session['cart'] = cart
    session.permanent = True

    return jsonify({
        'success': True,
        'cart_count': len(cart),
        'total_items': sum(item['quantity'] for item in cart)
    })

@app.route('/cart/get', methods=['GET'])
def get_cart():
    """Get cart contents"""
    cart = init_cart()

    total_amount = sum(item['price'] * item['quantity'] for item in cart if item['selected'])
    total_items = sum(item['quantity'] for item in cart)
    selected_items = sum(item['quantity'] for item in cart if item['selected'])

    return jsonify({
        'cart': cart,
        'total_amount': total_amount,
        'total_items': total_items,
        'selected_items': selected_items,
        'cart_count': len(cart)
    })

@app.route('/cart/update', methods=['POST'])
def update_cart():
    """Update cart item quantity or selection"""
    data = request.get_json()
    cart = init_cart()

    item_id = data.get('id')
    if not item_id:
        return jsonify({'error': 'Item ID required'}), 400

    # Find item in cart
    item = None
    for cart_item in cart:
        if cart_item['id'] == item_id:
            item = cart_item
            break

    if not item:
        return jsonify({'error': 'Item not found in cart'}), 404

    # Update item properties
    if 'quantity' in data:
        new_quantity = int(data['quantity'])
        if new_quantity <= 0:
            cart.remove(item)
        else:
            item['quantity'] = new_quantity

    if 'selected' in data:
        item['selected'] = bool(data['selected'])

    session['cart'] = cart

    return jsonify({'success': True})

@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    """Remove item from cart"""
    data = request.get_json()
    cart = init_cart()

    item_id = data.get('id')
    if not item_id:
        return jsonify({'error': 'Item ID required'}), 400

    # Remove item from cart
    cart = [item for item in cart if item['id'] != item_id]
    session['cart'] = cart

    return jsonify({'success': True, 'cart_count': len(cart)})

@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    """Clear all items from cart"""
    session['cart'] = []
    return jsonify({'success': True})

@app.route('/cart/checkout', methods=['POST'])
def checkout():
    """Process checkout (placeholder for payment gateway integration)"""
    cart = init_cart()
    selected_items = [item for item in cart if item['selected']]

    if not selected_items:
        return jsonify({'error': 'No items selected for checkout'}), 400

    # Calculate totals
    total_amount = sum(item['price'] * item['quantity'] for item in selected_items)

    # Create order data (this would typically be saved to a database)
    order_data = {
        'order_id': str(uuid.uuid4()),
        'items': selected_items,
        'total_amount': total_amount,
        'order_date': datetime.now().isoformat(),
        'status': 'pending_payment'
    }

    # TODO: Integrate with payment gateway (Razorpay, Stripe, etc.)

    return jsonify({
        'success': True,
        'order_id': order_data['order_id'],
        'total_amount': total_amount,
        'redirect_url': '/payment',  # Replace with actual payment gateway URL
        'message': 'Redirecting to payment gateway...'
    })

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
        size_data = []
        for item in sizes.split(','):
            size_label, size_price = item.split(':')
            float(size_price)  # ensure it's a number
            size_data.append((size_label, size_price))
    except Exception:
        return jsonify({'error': 'Invalid sizes format. Expected: S:500,M:700'}), 400

    # ✅ Create filename in new format: {name}_{size1}_{price1}_{size2}_{price2}...
    filename_parts = [name]
    for size_label, size_price in size_data:
        filename_parts.append(size_label)
        filename_parts.append(size_price)

    filename_base = '_'.join(filename_parts)

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
