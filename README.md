# Shopping Cart Bot

This project is a Telegram bot designed for managing a shopping cart experience. Users can browse products, add them to their cart, and complete purchases through a simple and interactive interface.

## Features

- User registration and authentication
- Product catalog with detailed descriptions and media
- Cart management including adding, removing, and viewing items
- Payment processing with prepayment confirmation
- Admin functionalities for managing products and categories

## Project Structure

```
shopping-cart-bot
├── src
│   ├── bot.py                # Main entry point for the bot
│   ├── config.py             # Configuration settings
│   ├── handlers               # Contains all command handlers
│   │   ├── admin.py          # Admin command handlers
│   │   ├── auth.py           # User authentication handlers
│   │   ├── cart.py           # Cart management handlers
│   │   ├── catalog.py        # Product catalog handlers
│   │   └── payment.py        # Payment processing handlers
│   ├── keyboards              # Custom keyboard layouts
│   │   ├── admin_kb.py       # Admin keyboard layout
│   │   ├── catalog_kb.py     # Product navigation keyboard
│   │   └── cart_kb.py        # Cart action keyboard
│   ├── models                 # Data models
│   │   ├── product.py         # Product model
│   │   ├── user.py            # User model
│   │   └── order.py           # Order model
│   ├── states                 # State management
│   │   ├── states.py          # State definitions
│   └── utils                  # Utility functions
│       ├── db.py              # Database interaction functions
├── media                      # Media files
│   ├── products               # Product images/videos
│   └── qr_codes              # QR code images for payments
├── data                       # Data files
│   └── products.json          # Product data in JSON format
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```
   cd shopping-cart-bot
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your bot token and admin chat ID in `src/config.py`.

## Usage

1. Run the bot:
   ```
   python src/bot.py
   ```

2. Interact with the bot on Telegram to explore its features.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.