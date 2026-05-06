# Telegram Mini App (TMA) Integration Guide

Your KG Hostel project is now fully integrated with Telegram Mini App support! Here's how to set it up and deploy.

## Architecture Overview

```
Telegram Bot (bot.py)
    ↓
Telegram Mini App (React Frontend)
    ↓
Backend API (FastAPI)
    ↓
Database (PostgreSQL)
```

## Setup Steps

### 1. Install Dependencies

#### Backend:
```bash
cd c:\Users\stroi\IdeaProjects\telegram.bot
pip install -r requirements.txt
```

#### Frontend:
```bash
cd frontend
npm install
npm install @twa-dev/sdk
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
# .env
API_TOKEN=your_actual_bot_token_here
ADMIN_CHAT_ID=your_admin_id
DATABASE_URL=postgresql://postgres:bektur97@localhost/postgres
FRONTEND_URL=https://your-domain.com/app
```

### 3. Deploy Frontend (Required for TMA)

Telegram Mini Apps **MUST** be served over HTTPS. Options:

#### Option A: Deploy to Vercel (Recommended)
```bash
cd frontend
npm install -g vercel
vercel
# Follow prompts, note your URL (e.g., https://kg-hostel.vercel.app)
```

#### Option B: Deploy to Netlify
```bash
cd frontend
npm run build
# Drag `dist` folder to Netlify
```

#### Option C: Self-hosted with HTTPS
- Use nginx with Let's Encrypt SSL
- Or use a service like Cloudflare

**Important:** Update `TMA_URL` in `handlers/tma.py` with your deployed URL:
```python
TMA_URL = "https://your-deployed-url.com"  # e.g., https://kg-hostel.vercel.app
```

### 4. Set Bot Menu Button

Run this Python script to set the bot's menu button to open your TMA:

```python
import requests

BOT_TOKEN = "your_bot_token"
TMA_URL = "https://your-deployed-url.com"

response = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setChatMenuButton",
    json={
        "menu_button": {
            "type": "web_app",
            "text": "🏨 Open App",
            "web_app": {
                "url": TMA_URL
            }
        }
    }
)

print(response.json())
```

Or use BotFather commands:
1. Message @BotFather
2. Select your bot
3. Choose "Menu button"
4. Choose "Edit menu button"
5. Paste your TMA URL

### 5. Run the Services

#### Terminal 1 - Backend API:
```bash
cd c:\Users\stroi\IdeaProjects\telegram.bot
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Telegram Bot:
```bash
cd c:\Users\stroi\IdeaProjects\telegram.bot
python bot.py
```

#### Terminal 3 - Frontend (Development):
```bash
cd frontend
npm run dev
```

## File Structure

```
handlers/tma.py                    # TMA command handlers
utils.py                          # TMA authentication utilities
frontend/src/context/TmaContext.jsx     # React TMA context
frontend/src/api/tmaApi.js              # API utilities with TMA auth
frontend/src/components/TmaUserInfo.jsx # Example TMA component
backend/main.py                   # TMA API endpoints (GET /api/tma/user, etc.)
```

## How TMA Authentication Works

1. **User opens bot** → Bot shows "🏨 Open KG Hostel App" button
2. **User clicks button** → Opens your TMA in Telegram
3. **TMA loads** → JavaScript SDK initializes with `initData`
4. **Frontend stores** → Saves `initData` in localStorage
5. **API requests** → Frontend sends `X-Telegram-Init-Data` header
6. **Backend verifies** → Checks signature using bot token (HMAC-SHA256)
7. **User authenticated** → Backend returns user data

## TMA Endpoints

### Public Endpoints
- `GET /api/hostels` - Get all visible hostels

### Authenticated Endpoints (require X-Telegram-Init-Data header)
- `GET /api/tma/user` - Get authenticated user info
- `GET /api/hostels/my` - Get user's hostels
- `POST /api/support` - Send support message
- `GET /api/support/history` - Get support message history

## Testing Locally

For local testing without real Telegram:

```javascript
// Open browser console and run:
localStorage.setItem('tmaInitData', 'mock_data_here')
localStorage.setItem('telegramUserId', '123456789')
```

Then the app will work in browser even without Telegram context.

## Troubleshooting

### TMA doesn't open
- Check bot token is correct
- Verify HTTPS URL (not HTTP)
- Use @BotFather to set menu button correctly

### Authentication fails
- Ensure `API_TOKEN` in config.py matches your bot token
- Verify `X-Telegram-Init-Data` header is being sent
- Check HMAC signature calculation in backend

### CORS issues
- Backend already has CORS enabled for all origins (line 35 in main.py)
- In production, replace `allow_origins=["*"]` with your frontend URL

### Database errors
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in .env file
- Run migrations: `python -m alembic upgrade head`

## Production Checklist

- [ ] Deploy frontend to HTTPS URL
- [ ] Set bot menu button to TMA URL
- [ ] Update `TMA_URL` in handlers/tma.py
- [ ] Set proper `DATABASE_URL` to production database
- [ ] Change `allow_origins` in backend to specific frontend URL
- [ ] Store secrets in environment variables (not hardcoded)
- [ ] Enable bot webhook instead of polling (for production)
- [ ] Set up monitoring and error logging
- [ ] Test TMA authentication end-to-end

## Next Steps

1. **Try it!** Open your bot and click the menu button
2. **Customize** - Add more features to TmaUserInfo component
3. **User roles** - Implement host vs user vs admin roles
4. **Payments** - Integrate payment processing for bookings
5. **Real-time** - Add WebSocket for live updates

## Resources

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Mini Apps](https://core.telegram.org/bots/webapps)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
