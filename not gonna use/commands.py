from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler
import datetime
import logging
import random
import os
from dotenv import load_dotenv
from pytz import timezone

load_dotenv()
SPREAD_SHEET_ID = os.getenv('SPREAD_SHEET_ID')


# Setup and constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
UK_TIME_ZONE = 'Europe/London'
CZ_TIME_ZONE = 'Europe/Prague'
TIME_ZONE, TYPE_OF_MEAL, MEAL_DETAILS = range(3)
# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Function to insert data into Google Sheets
def insert_into_sheet_food(timestamp, user_input, meal_type, time_zone):
    try:
        unique_id = str(random.randint(1000000000, 9999999999))
        current_time = datetime.datetime.now(timezone(time_zone))
        date = current_time.strftime("%Y-%m-%d")
        time = current_time.strftime("%H:%M:%S")
        key = f"meal_type_{meal_type}".lower()
        data_type = str(type(user_input).__name__)  # Get the data type of user_input
        values = [[unique_id, date, '', time, time_zone, key, '', data_type, user_input]]
        body = {'values': values}
        result = service.spreadsheets().values().append(spreadsheetId=SPREAD_SHEET_ID, range='Sheet1!A:J', valueInputOption='USER_ENTERED', body=body).execute()
        print("Data appended successfully")
    except Exception as e:
        print(f"An error occurred: {e}")


# Start command function
async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Hello, I'm your personal tracking assistant bot!\n"
              "We will log your daily activities and track aspects of your life to quantify it eventually.\n"
              "Let's get started with your daily tracking. Use /awake to begin logging today's activities."),
        parse_mode='HTML'
    )

# Stop command function
async def stop(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    user_data['notifications_paused'] = True
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Notifications are now paused. Use /start or /resume when you're ready to receive notifications again."
    )


# Timezone 
async def ask_time_zone(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['UK', 'CZ']]
    await update.message.reply_text('Please choose your time zone:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return TIME_ZONE

# Timezone selection + meal type
async def time_zone(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text
    if user_choice == 'UK':
        context.user_data['time_zone'] = UK_TIME_ZONE
    elif user_choice == 'CZ':
        context.user_data['time_zone'] = CZ_TIME_ZONE
    else:
        await update.message.reply_text('Invalid selection. Please choose again.')
        return TIME_ZONE
    await update.message.reply_text('Please choose the type of meal:', reply_markup=ReplyKeyboardMarkup([['Breakfast', 'Lunch', 'Dinner', 'Snack', 'Other']], one_time_keyboard=True))
    return TYPE_OF_MEAL   

async def meal_type(update: Update, context: CallbackContext) -> int:
    context.user_data['meal_type'] = update.message.text
    await update.message.reply_text(
        'Please write what you ate for ' + update.message.text.lower(),
        reply_markup=ReplyKeyboardRemove()
    )
    return MEAL_DETAILS

# Meal details
async def meal_details(update: Update, context: CallbackContext) -> int:
    """Handle the response for meal details and end the conversation."""
    # Extract meal details and timestamp
    meal_details = update.message.text
    timestamp = datetime.datetime.now().isoformat()
    time_zone = context.user_data.get('time_zone', 'UTC')

    # Assuming you have meal type stored earlier
    meal_type = context.user_data.get('meal_type')
    insert_into_sheet_food(timestamp, meal_details, meal_type, time_zone)

    # Send confirmation to user
    await update.message.reply_text('Thank you for recording your meal!')
    return ConversationHandler.END

# Food command function
async def food(update: Update, context: CallbackContext) -> None:
    return await ask_time_zone(update, context)
