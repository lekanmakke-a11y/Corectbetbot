import os
import logging
import sys
import time
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError, BadRequest, NetworkError, TimedOut

# Load environment variables
load_dotenv()

# Configure logging with file and console output
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Get environment variables with fallbacks
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

# Convert CHANNEL_ID to integer with error handling
try:
    CHANNEL_ID_INT = int(CHANNEL_ID)
except ValueError:
    logger.error(f"Invalid CHANNEL_ID format: {CHANNEL_ID}. Must be a number.")
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

ERROR_MESSAGE = """❌ **A apărut o eroare.**

Te rugăm să încerci din nou mai târziu."""

# Helper functions for keyboards
def get_verify_keyboard():
    """Create keyboard with verify button"""
    keyboard = [[InlineKeyboardButton("🔐 VERIFICĂ ȘI INTRĂ ÎN CORECTBET", url=CHANNEL_LINK)]]
    return InlineKeyboardMarkup(keyboard)

def get_check_keyboard():
    """Create keyboard with join and check buttons"""
    keyboard = [
        [InlineKeyboardButton("🔐 INTRĂ ÎN CORECTBET", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ AM INTRAT ÎN CANAL", callback_data='check_membership')]
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
    try:
        if not update or not update.effective_user:
            logger.warning("Received start command with no user")
            return
            
        user = update.effective_user
        logger.info(f"User {user.id} (@{user.username}) started the bot")
        
        await update.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=get_verify_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        try:
            await update.message.reply_text(
                "❌ A apărut o eroare. Te rugăm să încerci din nou.",
                parse_mode='Markdown'
            )
        except:
            pass

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user has joined the channel"""
    try:
        if not update or not update.callback_query:
            logger.warning("Received callback with no query")
            return
            
        query = update.callback_query
        user_id = query.from_user.id
        
        # Always answer callback query first to prevent timeout
        try:
            await query.answer()
        except Exception as e:
            logger.warning(f"Could not answer callback: {e}")
        
        logger.info(f"Checking membership for user {user_id}")
        
        # Get chat member status with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                member = await context.bot.get_chat_member(chat_id=CHANNEL_ID_INT, user_id=user_id)
                status = member.status
                logger.info(f"User {user_id} membership status: {status}")
                
                if status in ['member', 'administrator', 'creator']:
                    # User is a member
                    try:
                        await query.edit_message_text(
                            ACCESS_CONFIRMED,
                            reply_markup=get_access_confirmed_keyboard(),
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Error editing message: {e}")
                        await query.message.reply_text(
                            ACCESS_CONFIRMED,
                            reply_markup=get_access_confirmed_keyboard(),
                            parse_mode='Markdown'
                        )
                    logger.info(f"User {user_id} successfully verified")
                    return
                else:
                    # User is not a member
                    try:
                        await query.edit_message_text(
                            NOT_JOINED_MESSAGE,
                            reply_markup=get_check_keyboard(),
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Error editing message: {e}")
                        await query.message.reply_text(
                            NOT_JOINED_MESSAGE,
                            reply_markup=get_check_keyboard(),
                            parse_mode='Markdown'
                        )
                    logger.info(f"User {user_id} not a member")
                    return
                    
            except BadRequest as e:
                logger.error(f"BadRequest for user {user_id} (attempt {attempt+1}): {str(e)}")
                
                if "chat not found" in str(e).lower():
                    error_msg = "❌ **Canalul nu a fost găsit.**\n\nVerifică dacă botul este administrator în canal."
                elif "bot is not a member" in str(e).lower():
                    error_msg = "❌ **Botul nu este administrator în canal.**\n\nTe rugăm să contactezi suportul."
                elif "user not found" in str(e).lower():
                    error_msg = "❌ **Nu te-am putut găsi.**\n\nTe rugăm să încerci din nou."
                elif "too many requests" in str(e).lower():
                    error_msg = "⏳ **Prea multe cereri.**\n\nTe rugăm să aștepți câteva secunde."
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
                        continue
                else:
                    error_msg = f"❌ **Eroare:** {str(e)[:100]}"
                
                try:
                    await query.edit_message_text(
                        error_msg,
                        reply_markup=get_check_keyboard(),
                        parse_mode='Markdown'
                    )
                except:
                    await query.message.reply_text(
                        error_msg,
                        reply_markup=get_check_keyboard(),
                        parse_mode='Markdown'
                    )
                return
                
            except (NetworkError, TimedOut) as e:
                logger.error(f"Network error for user {user_id} (attempt {attempt+1}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                else:
                    error_msg = "⚠️ **Eroare de conexiune.**\n\nTe rugăm să încerci din nou."
                    try:
                        await query.edit_message_text(
                            error_msg,
                            reply_markup=get_check_keyboard(),
                            parse_mode='Markdown'
                        )
                    except:
                        await query.message.reply_text(
                            error_msg,
                            reply_markup=get_check_keyboard(),
                            parse_mode='Markdown'
                        )
                    return
                    
            except TelegramError as e:
                logger.error(f"TelegramError for user {user_id}: {str(e)}")
                try:
                    await query.edit_message_text(
                        ERROR_MESSAGE,
                        reply_markup=get_check_keyboard(),
                        parse_mode='Markdown'
                    )
                except:
                    await query.message.reply_text(
                        ERROR_MESSAGE,
                        reply_markup=get_check_keyboard(),
                        parse_mode='Markdown'
                    )
                return
                
    except Exception as e:
        logger.error(f"Unexpected error in check_membership: {str(e)}")
        try:
            if update and update.callback_query:
                await update.callback_query.message.reply_text(
                    ERROR_MESSAGE,
                    parse_mode='Markdown'
                )
        except:
            pass

async def handle_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the start callback to reset the flow"""
    try:
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            WELCOME_MESSAGE,
            reply_markup=get_verify_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in start callback: {str(e)}")
        try:
            await update.callback_query.message.reply_text(
                "❌ A apărut o eroare. Te rugăm să încerci din nou.",
                parse_mode='Markdown'
            )
        except:
            pass

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error: {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ A apărut o eroare. Te rugăm să încerci din nou.",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}")

async def post_init(application):
    """Called after the application is initialized"""
    logger.info("Bot started successfully!")
    logger.info(f"Bot Username: @{application.bot.username}")
    logger.info(f"Channel ID: {CHANNEL_ID_INT}")
    logger.info(f"Channel Link: {CHANNEL_LINK}")
    
    # Test connection to channel
    try:
        chat = await application.bot.get_chat(chat_id=CHANNEL_ID_INT)
        logger.info(f"Connected to channel: {chat.title}")
        logger.info("Bot is ready to accept messages!")
    except Exception as e:
        logger.error(f"Could not connect to channel: {str(e)}")
        logger.warning("Bot will still work but channel verification may fail")

def main():
    """Start the bot"""
    try:
        # Create the Application with proper settings
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(check_membership, pattern='^check_membership$'))
        application.add_handler(CallbackQueryHandler(handle_start_callback, pattern='^start$'))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Add post initialization
        application.post_init = post_init
        
        # Start the bot
        if WEBHOOK_URL:
            # Webhook mode (for Railway)
            logger.info(f"Starting bot in webhook mode on port {PORT}")
            logger.info(f"Webhook URL: {WEBHOOK_URL}/{BOT_TOKEN}")
            
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
                drop_pending_updates=True,
                poll_interval=1.0
            )
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.info("Bot will restart in 5 seconds...")
        time.sleep(5)
        sys.exit(1)

if __name__ == '__main__':
    # Add asyncio import for sleep
    import asyncio
    main()
