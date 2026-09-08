import os
import logging
import sys
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CHANNEL_LINK = os.getenv('CHANNEL_LINK', 'https://t.me/+QvCFEopP3r9hY2Q0')
PORT = int(os.getenv('PORT', 8080))
WEBHOOK_URL = os.getenv('WEBHOOK_URL', None)

# Validate required environment variables
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not found in environment variables")
    sys.exit(1)

if not CHANNEL_ID:
    logger.error("CHANNEL_ID not found in environment variables")
    sys.exit(1)

# Constants
WELCOME_MESSAGE = """👋 **Bine ai venit în CorectBet!**

De peste **7 ani construim și dezvoltăm această comunitate**, iar unul dintre lucrurile la care am ținut întotdeauna este **calitatea membrilor**, nu doar numărul lor.

🛡️ Din acest motiv, accesul se realizează prin intermediul botului oficial CorectBet.

Nu acceptăm **boți, conturi fake sau membri generați artificial**. Ne dorim o comunitate formată din **persoane reale și active**, interesate de conținutul pe care îl oferim.

Această verificare ne ajută să păstrăm grupul curat și standardele pe care le-am construit în toți acești ani.

✅ **Ești o persoană reală? Continuă mai jos pentru acces.**"""

ACCESS_CONFIRMED = """🎉 **Acces confirmat!**

Bine ai venit în comunitatea CorectBet. Ai fost verificat cu succes."""

NOT_JOINED_MESSAGE = """❌ **Nu ești încă membru al canalului.**

Te rugăm să intri în canal folosind butonul de mai jos, apoi revino și apasă „AM INTRAT ÎN CANAL”."""

ERROR_MESSAGE = """❌ **Eroare la verificare.**

Te rugăm să încerci din nou mai târziu."""

# Button texts
VERIFY_BUTTON_TEXT = "🔐 VERIFICĂ ȘI INTRĂ ÎN CORECTBET"
JOINED_BUTTON_TEXT = "✅ AM INTRAT ÎN CANAL"
JOIN_CHANNEL_BUTTON_TEXT = "🔐 INTRĂ ÎN CORECTBET"

# Helper functions for keyboards
def get_verify_keyboard():
    """Create keyboard with verify button"""
    keyboard = [[InlineKeyboardButton(VERIFY_BUTTON_TEXT, url=CHANNEL_LINK)]]
    return InlineKeyboardMarkup(keyboard)

def get_check_keyboard():
    """Create keyboard with join and check buttons"""
    keyboard = [
        [InlineKeyboardButton(JOIN_CHANNEL_BUTTON_TEXT, url=CHANNEL_LINK)],
        [InlineKeyboardButton(JOINED_BUTTON_TEXT, callback_data='check_membership')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_access_confirmed_keyboard():
    """Create keyboard after successful verification"""
    keyboard = [
        [InlineKeyboardButton("📢 Vizitează Canalul", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🔄 Verifică din nou", callback_data='check_membership')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    user = update.effective_user
    logger.info(f"User {user.id} (@{user.username}) started the bot")
    
    try:
        await update.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=get_verify_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        await update.message.reply_text(
            "❌ A apărut o eroare. Te rugăm să încerci din nou.",
            parse_mode='Markdown'
        )

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user has joined the channel"""
    query = update.callback_query
    user_id = query.from_user.id
    
    try:
        await query.answer()
        logger.info(f"Checking membership for user {user_id}")
        
        # Get chat member status
        chat_id = int(CHANNEL_ID)
        member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        status = member.status
        
        logger.info(f"User {user_id} membership status: {status}")
        
        if status in ['member', 'administrator', 'creator']:
            # User is a member
            await query.edit_message_text(
                ACCESS_CONFIRMED,
                reply_markup=get_access_confirmed_keyboard(),
                parse_mode='Markdown'
            )
            logger.info(f"User {user_id} successfully verified")
        else:
            # User is not a member
            await query.edit_message_text(
                NOT_JOINED_MESSAGE,
                reply_markup=get_check_keyboard(),
                parse_mode='Markdown'
            )
            logger.info(f"User {user_id} not a member")
            
    except Exception as e:
        logger.error(f"Error checking membership for user {user_id}: {str(e)}")
        
        # Handle specific error cases
        error_msg = ERROR_MESSAGE
        if "bot is not a member" in str(e).lower():
            error_msg = """❌ **Eroare de configurare.**

Botul nu este administrator în canal. Te rugăm să contactezi suportul."""
        
        try:
            await query.edit_message_text(
                error_msg,
                reply_markup=get_check_keyboard(),
                parse_mode='Markdown'
            )
        except Exception as edit_error:
            logger.error(f"Error editing message: {edit_error}")
            await query.message.reply_text(
                error_msg,
                reply_markup=get_check_keyboard(),
                parse_mode='Markdown'
            )

async def handle_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the start callback to reset the flow"""
    query = update.callback_query
    await query.answer()
    
    try:
        await query.edit_message_text(
            WELCOME_MESSAGE,
            reply_markup=get_verify_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in start callback: {str(e)}")
        await query.message.reply_text(
            "❌ A apărut o eroare. Te rugăm să încerci din nou.",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ A apărut o eroare. Te rugăm să încerci din nou.",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}")

def main():
    """Start the bot"""
    try:
        # Create the Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(check_membership, pattern='^check_membership$'))
        application.add_handler(CallbackQueryHandler(handle_start_callback, pattern='^start$'))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Start the bot
        if WEBHOOK_URL:
            # Webhook mode (for Railway)
            logger.info(f"Starting bot in webhook mode on port {PORT}")
            application.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=BOT_TOKEN,
                webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
            )
        else:
            # Polling mode (for local development)
            logger.info("Starting bot in polling mode")
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
