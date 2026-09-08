# CorectBet Telegram Bot

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/YOUR_TEMPLATE_LINK)

A professional Telegram bot for CorectBet community membership verification with automatic deployment on Railway.

## Features

- ✅ Welcome message with CorectBet branding
- ✅ Channel membership verification using `getChatMember`
- ✅ Clean and professional UI/UX
- ✅ Romanian language support
- ✅ Secure environment variable configuration
- ✅ Auto-deploy on Railway
- ✅ Health checks and error handling
- ✅ Webhook support for production

## Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/YOUR_TEMPLATE_LINK)

### Step 1: Fork this repository

Click the "Fork" button at the top right of this repository.

### Step 2: Deploy on Railway

1. Click the "Deploy on Railway" button above
2. Connect your GitHub account
3. Select the forked repository
4. Add the following environment variables:
   - `BOT_TOKEN`: Your bot token from @BotFather
   - `CHANNEL_ID`: Your channel ID (negative number)
   - `CHANNEL_LINK`: Your channel invite link
5. Click "Deploy"

### Step 3: Configure Webhook

After deployment, Railway will provide a URL (e.g., `https://your-app.railway.app`). 
Add this URL as `WEBHOOK_URL` in your environment variables.

## Manual Setup

### Prerequisites

- Python 3.8+
- Telegram Bot Token from @BotFather
- Telegram Channel with bot as administrator

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/corectbet-bot.git
cd corectbet-bot
