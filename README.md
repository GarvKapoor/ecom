# Manpasand Clothing

Manpasand Clothing is a modern e-commerce web application built with Flask and other modern technologies. It provides a seamless shopping experience for users, with a focus on a clean and responsive user interface.

## Features

- **Product Gallery:** Browse a beautiful gallery of clothing items.
- **Dynamic Product Details:** View product information, including sizes and prices, parsed dynamically from filenames.
- **Shopping Cart:** Add items to a shopping cart, update quantities, and remove items.
- **Responsive Design:** The application is fully responsive and works on all devices, from mobile phones to desktops.
- **Sticky Navigation:** The navigation bar remains visible on scroll, providing easy access to the cart and other options.

## Technologies Used

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Image Hosting:** GitHub
- **Deployment:** Render

## Setup and Installation

To run this project locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/manpasand-clothing.git
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a `.env` file** in the root directory and add the following environment variables:
   ```
   GITHUB_TOKEN=your-github-token
   SECRET_KEY=your-secret-key
   ```

6. **Run the application:**
   ```bash
   python app.py
   ```

The application will be available at `http://127.0.0.1:5000`.



## Contributing

Contributions are welcome! If you have any suggestions or find any bugs, please open an issue or create a pull request.
