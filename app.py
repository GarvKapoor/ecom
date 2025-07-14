from flask import Flask, render_template
import requests
import os
from dotenv import load_dotenv

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