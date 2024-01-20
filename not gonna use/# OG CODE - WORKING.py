# OG CODE - WORKING

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, CallbackContext
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import uuid
from pytz import timezone
import random
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
import datetime

# Setup and constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
UK_TIME_ZONE = 'Europe/London'
CZ_TIME_ZONE = 'Europe/Prague'


load_dotenv()
telegram_token = os.getenv('API_KEY')
SPREAD_SHEET_ID = os.getenv('SPREAD_SHEET_ID')
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Function to insert data into Google Sheets
def insert_into_sheet_food(meal_datetime, timestamp, user_input, meal_type, time_zone):
    try:
        unique_id = str(random.randint(1000000000, 9999999999))
        source = 'telegram'
        current_time = datetime.datetime.now(timezone(time_zone))
        imported_at_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        date = current_time.strftime("%Y-%m-%d")
        time = current_time.strftime("%H:%M:%S")
        key = f"meal_type_{meal_type}".lower()
        data_type = str(type(user_input).__name__)  # Get the data type of user_input
        values = [[unique_id, date, imported_at_time, time, time_zone, key, '', data_type, user_input, source]]
        body = {'values': values}
        result = service.spreadsheets().values().append(spreadsheetId=SPREAD_SHEET_ID, range='Sheet1!A:A', valueInputOption='USER_ENTERED', body=body).execute()
        print("Data appended successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to insert water intake into google sheets
def log_water_intake(volume, time_zone, source='telegram'):
    try:
        unique_id = str(random.randint(1000000000, 9999999999))
        current_time = datetime.datetime.now(timezone(time_zone))
        date = current_time.strftime("%Y-%m-%d")
        time = current_time.strftime("%H:%M:%S")
        imported_at_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        key = 'water_intake'
        data_type = str(type(volume).__name__)  # Get the data type of volume
        values = [[unique_id, date, imported_at_time, time, time_zone, key, '', data_type, volume, source]]
        body = {'values': values}
        result = service.spreadsheets().values().append(spreadsheetId=SPREAD_SHEET_ID, range='Sheet1!A:A', valueInputOption='USER_ENTERED', body=body).execute()
        print("Water intake logged successfully")
    except Exception as e:
        print(f"An error occurred: {e}")


# Start command function
async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Hello, I'm your personal tracking assistant bot! 👾 \n"
              "We will log your daily activities and track aspects of your life to quantify it eventually.\n"
              "Let's get started with your daily tracking. Use /commands shall you need help."),
        parse_mode='HTML'
    )

# Stop command function
async def stop(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    user_data['notifications_paused'] = True
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🤖Notifications are now paused. Use /start or /resume when you're ready to receive notifications again."
    )

# range
ASK_IF_EATEN_BEFORE, MEAL_TIME, TIME_ZONE, TYPE_OF_MEAL, MEAL_DETAILS = range(5)
    

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
    await update.message.reply_text('Please choose the type of meal:', reply_markup=ReplyKeyboardMarkup([['Breakfast 🍳', 'Lunch 🥗', 'Dinner 🍗', 'Snack 🍪', 'Other 🥖']], one_time_keyboard=True))
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
    meal_details = update.message.text
    if 'meal_datetime' in context.user_data:
        meal_datetime = context.user_data['meal_datetime']
    else: 
        meal_datetime = datetime.datetime.now().isoformat()
    timestamp = datetime.datetime.now().isoformat()
    meal_type = context.user_data.get('meal_type')
    insert_into_sheet_food(meal_datetime, timestamp, meal_details, meal_type, time_zone)

    await update.message.reply_text('Thank you for recording your meal! 👌🏻')
    return ConversationHandler.END

# Food eat now/before
async def food(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Now🍴', 'Before🍴']]
    await update.message.reply_text('Are you eating now or have you eaten before?🍽️', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ASK_IF_EATEN_BEFORE

# Import the datetime module
# eat before state
async def ask_if_eaten_before(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text
    if user_choice.lower() == 'before':
        # Get the current date and time
        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        await update.message.reply_text('Enter the date and time of your meal (YYYY-MM-DD HH:MM):', reply_markup=ReplyKeyboardMarkup([[current_datetime]], one_time_keyboard=True))
        return MEAL_TIME
    else:
        return await ask_time_zone(update, context)

# mealtime
async def meal_time(update: Update, context: CallbackContext) -> int:
    context.user_data['meal_datetime'] = update.message.text
    await update.message.reply_text('Please choose the type of meal:', reply_markup=ReplyKeyboardMarkup([['Breakfast 🍳', 'Lunch 🥗', 'Dinner 🍗', 'Snack 🍪', 'Other 🥖']], one_time_keyboard=True))
    return TYPE_OF_MEAL


# commands

async def commands(update: Update, context: CallbackContext) -> None:
    # Send available commands
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🚨The commands you can use are:\n"
             "/start - Start the bot\n"
             "/stop - Stop the bot\n"
             "/commands - Get help\n"
             "/food -  Automatically log your food intake\n"
             "/awake - Log your wake up time\n"
             "Other shall come soon🚨"
    )

# Water intake command function
ASK_WATER_INTAKE = range(1)

async def water(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Little (0.8L)', 'Some More (1L - 1.5L)', 'Enough (2L - 3L)']]
    await update.message.reply_text('How much water did you drink?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ASK_WATER_INTAKE

async def ask_water_intake(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text
    if user_choice == 'Little (0.8L)':
        intake_volume = 0.8
    elif user_choice == 'Some More (1L - 1.5L)':
        intake_volume = 1.25  # Average of 1L and 1.5L
    elif user_choice == 'Enough (2L - 3L)':
        intake_volume = 2.5  # Average of 2L and 3L
    else:
        await update.message.reply_text('Invalid selection. Please choose again.')
        return ASK_WATER_INTAKE
    # Call function to log water intake
    log_water_intake(intake_volume, context.user_data.get('time_zone', 'UTC'))
    await update.message.reply_text('Thank you for logging your water intake!')
    return ConversationHandler.END

log_water_intake(ASK_WATER_INTAKE, time_zone, source='telegram')


# Run polling

if __name__ == '__main__':
    # Build a new application
    application = ApplicationBuilder().token(telegram_token).build()

    # Create handlers
    ask_time_zone_handler = CommandHandler('ask_time_zone', ask_time_zone)
    start_handler = CommandHandler('start', start)
    stop_handler = CommandHandler('stop', stop)
    food_handler = ConversationHandler(
        entry_points=[CommandHandler('food', food)],
        states={
            ASK_IF_EATEN_BEFORE: [MessageHandler(filters.Text() & ~filters.Command(), ask_if_eaten_before)],
            MEAL_TIME: [MessageHandler(filters.Text() & ~filters.Command(), meal_time)],
            TIME_ZONE: [MessageHandler(filters.Text() & ~filters.Command(), time_zone)],
            TYPE_OF_MEAL: [MessageHandler(filters.Text() & ~filters.Command(), meal_type)],
            MEAL_DETAILS: [MessageHandler(filters.Text() & ~filters.Command(), meal_details)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    
    water_handler = ConversationHandler(
    entry_points=[CommandHandler('water', water)],
    states={
        ASK_WATER_INTAKE: [MessageHandler(filters.Text() & ~filters.Command(), ask_water_intake)]
    },
    fallbacks=[CommandHandler('stop', stop)]
)
    commands_handler = CommandHandler('commands', commands)
    # Add handlers to the application
    application.add_handler(start_handler)
    application.add_handler(stop_handler)
    application.add_handler(food_handler)
    application.add_handler(commands_handler)
    application.add_handler(ask_time_zone_handler)
    application.add_handler(water_handler)

    # Run polling
    application.run_polling()
