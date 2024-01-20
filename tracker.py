import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, CallbackContext
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import uuid
from pytz import timezone
import random
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from datetime import datetime
from functools import wraps
from threading import Thread
from server import app

 

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# .env setup
load_dotenv()
telegram_token = os.getenv('API_KEY')
SPREAD_SHEET_ID = os.getenv('SPREAD_SHEET_ID')
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Constants
SOURCE = 'telegram'
SPREADSHEET_RANGE = 'Sheet1!A:A'
VALUE_INPUT_OPTION = 'USER_ENTERED'


# Time_zone decorator
UK_TIME_ZONE = 'Europe/London'
CZ_TIME_ZONE = 'Europe/Prague'

time_zone = {'current': CZ_TIME_ZONE}  # Default timezone
tz = time_zone['current']
def check_timezone(func):
    @wraps(func)
    async def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        if 'awaiting_timezone' in context.user_data:
            return await func(update, context, *args, **kwargs)

        reply_keyboard = [[UK_TIME_ZONE, CZ_TIME_ZONE]]
        await update.message.reply_text(
            "Please choose your timezone:", 
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        context.user_data['awaiting_timezone'] = True
        context.user_data['original_func'] = func
        return

    return wrapped

async def set_timezone_choice(update: Update, context: CallbackContext) -> None:
    if 'awaiting_timezone' in context.user_data:
        timezone_choice = update.message.text
        time_zone['current'] = timezone_choice
        del context.user_data['awaiting_timezone']
        original_func = context.user_data.pop('original_func')
        await original_func(update, context)



# Function to log data into google sheets
def log_data_to_sheet(key, data, source=SOURCE):
    try:
        unique_id = str(random.randint(1000000000, 9999999999))
        current_time = datetime.now()
        date = current_time.strftime("%Y-%m-%d %H:%M")
        time = current_time.strftime("%H:%M:%S")
        imported_at_time = current_time.strftime("%Y-%m-%d %H:%M")
        food_actual_time = ''
        data_type = str(type(data).__name__)  # Get the data type of data
        values = [[unique_id, date, imported_at_time, time, tz, key, '', data_type, data, source,]]
        body = {'values': values}
        result = service.spreadsheets().values().append(spreadsheetId=SPREAD_SHEET_ID, range=SPREADSHEET_RANGE, valueInputOption=VALUE_INPUT_OPTION, body=body).execute()
        print(f"{key} logged successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to insert food intake into google sheets
def insert_into_sheet_food(meal_datetime, timestamp, meal_details, meal_type):
    key = f"meal_type_{meal_type}".lower()
    food_actual_time = meal_datetime.split()[0]
    log_data_to_sheet(key, meal_details)

# Function to insert water intake into google sheets
def log_water_intake(volume, time_zone):
    key = 'water_intake'
    # data = volume
    log_data_to_sheet(key, str(volume), tz)

# Function to insert coffee intake into google sheets
def log_coffee_intake(cups, time_zone):
    key = 'coffee_intake'
    log_data_to_sheet(key, cups,)

# Function to insert alcoohl intake into google sheets
def log_alcohol_intake(alcohol_type, alcohol_quantity, time_zone):
    # Construct a key that includes both the type and the quantity of alcohol
    key = alcohol_type
    data = alcohol_quantity
    log_data_to_sheet(key, data, tz)



# Stop command function
async def stop(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    user_data['notifications_paused'] = True
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🤖Notifications are now paused. Use /start or /resume when you're ready to receive notifications again."
    )

# range
ASK_IF_EATEN_BEFORE, MEAL_TIME, ASK_MEAL_DETAILS, TYPE_OF_MEAL, MEAL_DETAILS = range(5)
ASK_MEAL_DATE_TIME = range(6)
MEAL_DATE_TIME = range(7)
# Meal 


#@timezone_check


# Food eat now/before
async def food(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Now🍴', 'Before🍴']]
    await update.message.reply_text('Are you eating now or have you eaten before?🍽️', 
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ASK_IF_EATEN_BEFORE

# eat before state
async def ask_if_eaten_before(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text
    if user_choice == 'Before🍴':
        current_datetime = datetime.now().strftime('%d-%m-%Y %H:%M')
        await update.message.reply_text(
            'Please enter the date and time of your meal (DD-MM-YYYY HH:MM):',
            reply_markup=ReplyKeyboardRemove())
        return MEAL_DATE_TIME  # Ensure this matches the state defined in ConversationHandler
    else:
        return await meal_type(update, context)


# Function to handle meal time for 'before' option
async def meal_time_before(update: Update, context: CallbackContext) -> int:
    meal_time_input = update.message.text
    context.user_data['meal_datetime'] = meal_date_time
    return await meal_type(update, context)


# Function to handle current meal time
async def meal_time_now(update: Update, context: CallbackContext) -> int:
    context.user_data['meal_datetime'] = datetime.now().isoformat()
    return await meal_type(update, context)

async def meal_date_time(update: Update, context: CallbackContext) -> int:
    meal_datetime_input = update.message.text
    # Store the date and time in context.user_data
    context.user_data['meal_datetime'] = meal_datetime_input
    # Proceed to ask for the type of meal
    return await meal_type(update, context)

# mealtime
async def meal_time(update: Update, context: CallbackContext) -> int:
    meal_time_input = update.message.text
    meal_date = context.user_data.get('meal_date', datetime.now().strftime('%Y-%m-%d'))
    # Combine the date with the user-provided time
    meal_datetime = f"{meal_date} {meal_time_input}"
    context.user_data['meal_datetime'] = meal_datetime
    return MEAL_DETAILS  # Ensure this matches the state defined in ConversationHandler
# Meal type selection
async def meal_type(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Breakfast 🍳', 'Lunch 🥗', 'Dinner 🍗', 'Snack 🍪', 'Other 🥖']]
    await update.message.reply_text('Please choose the type of meal:', 
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return  MEAL_DETAILS

# Meal details
async def meal_details(update: Update, context: CallbackContext) -> int:
    meal_type = update.message.text
    context.user_data['meal_type'] = meal_type
    await update.message.reply_text('Please enter the details of your meal:')
    return ASK_MEAL_DETAILS

# Ask meal details
async def ask_meal_details(update: Update, context: CallbackContext) -> int:
    meal_details = update.message.text
    if 'meal_datetime' in context.user_data:
        meal_datetime = context.user_data['meal_datetime']
    else: 
        meal_datetime = datetime.now().isoformat()
    timestamp = datetime.now().isoformat()
    meal_type = context.user_data.get('meal_type')
    timestamp = datetime.now().isoformat()
    insert_into_sheet_food(meal_datetime, timestamp, meal_details, meal_type)
    await update.message.reply_text('Thank you for recording your meal! 👌🏻')
    return ConversationHandler.END

# commands
#@timezone_check
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


# Start command function
async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Hello, I'm your personal tracking assistant bot! 👾 \n"
              "We will log your daily activities and track aspects of your life to quantify it eventually.\n"
              "Let's get started with your daily tracking. Use /commands shall you need help."),
        parse_mode='HTML'
    )

    
# Water intake command function
ASK_WATER_INTAKE = range(1)
#@timezone_check
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

# Coffee

coffee_intake, cups, ASK_COFFEE_INTAKE = range(3)
#@timezone_check
async def coffee(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Yes', 'No']]
    user_choice = update.message.text
    await update.message.reply_text('Did you drink coffee today?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ASK_COFFEE_INTAKE

async def ask_coffee_intake(update: Update, context: CallbackContext) -> int:
    cups_input = update.message.text

    # Check if the input is 'Yes' or 'No'
    if cups_input in ['Yes', 'No']:
        if cups_input == 'Yes':
            # Prompt for the number of cups if the user answered 'Yes'
            await update.message.reply_text('How many cups of coffee did you drink?')
            return cups
        else:
            # If the user answered 'No', end the conversation
            await update.message.reply_text('No coffee logged.')
            return ConversationHandler.END
    else:
        # If the user is entering the number of cups
        try:
            cups = int(cups_input)
            if 1 <= cups <= 10:
                log_coffee_intake(cups, context.user_data.get('time_zone', 'UTC'))
                await update.message.reply_text(f'Thank you for logging {cups} cups of coffee!')
                return ConversationHandler.END
            else:
                await update.message.reply_text('Invalid input. Please enter a number between 1 and 10.')
                return cups  # Ask for the number of cups again
        except ValueError:
            await update.message.reply_text('Invalid input. Please enter a valid number.')
            return cups  # Ask for the number of cups again

# Alcohol intake 
# Add a new range for the alcohol conversation states
ASK_ALCOHOL_TYPE, ALCOHOL_DETAILS = range(2)

# Function to start alcohol logging
async def alcohol(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Wine 🍷', 'Beer 🍺', 'Spirits🍸'], ['No']]
    await update.message.reply_text(
        'Did you consume any alcohol?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ASK_ALCOHOL_TYPE

# Function to ask alcohol type
async def ask_alcohol_type(update: Update, context: CallbackContext) -> int:
    alcohol_type = update.message.text
    if alcohol_type == 'No':
        await update.message.reply_text('No alcohol logged.')
        return ConversationHandler.END
    else:
        context.user_data['alcohol_type'] = alcohol_type
        await update.message.reply_text(f'How much {alcohol_type} did you have?')
        return ALCOHOL_DETAILS

# Function to log alcohol details
async def alcohol_details(update: Update, context: CallbackContext) -> int:
    alcohol_quantity = update.message.text
    alcohol_type = context.user_data['alcohol_type']
    log_alcohol_intake(alcohol_type, alcohol_quantity, time_zone)
    await update.message.reply_text(f'Thank you for recording your {alcohol_type} intake: {alcohol_quantity}')
    return ConversationHandler.END
        


# Run polling

if __name__ == '__main__':
    # Build a new application
    application = ApplicationBuilder().token(telegram_token).build()
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    # Create handlers
timezone_handler = MessageHandler(filters.Text() & filters.Regex(f"^{UK_TIME_ZONE}$|^{CZ_TIME_ZONE}$"), set_timezone_choice)
start_handler = CommandHandler('start', start)
stop_handler = CommandHandler('stop', stop)
food_handler = ConversationHandler(
        entry_points=[CommandHandler('food', food)],
        states={
            ASK_IF_EATEN_BEFORE: [MessageHandler(filters.Text() & ~filters.Command(), ask_if_eaten_before)],
            MEAL_TIME: [MessageHandler(filters.Text() & ~filters.Command(), meal_time)],
            TYPE_OF_MEAL: [MessageHandler(filters.Text() & ~filters.Command(), meal_type)],
            MEAL_DETAILS: [MessageHandler(filters.Text() & ~filters.Command(), meal_details)],
            ASK_MEAL_DETAILS: [MessageHandler(filters.Text() & ~filters.Command(), ask_meal_details)],
            ASK_MEAL_DATE_TIME: [MessageHandler(filters.Text() & ~filters.Command(), meal_date_time)],
            MEAL_DATE_TIME: [MessageHandler(filters.Text() & ~filters.Command(), meal_date_time)],
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
coffee_handler = ConversationHandler(
    entry_points=[CommandHandler('coffee', coffee)],
    states={
        ASK_COFFEE_INTAKE: [MessageHandler(filters.Text() & ~filters.Command(), ask_coffee_intake)]
    },
    fallbacks=[CommandHandler('stop', stop)]
)
alcohol_handler = ConversationHandler(
    entry_points=[CommandHandler('alcohol', alcohol)],
    states={
        ASK_ALCOHOL_TYPE: [MessageHandler(filters.Text() & ~filters.Command(), ask_alcohol_type)],
        ALCOHOL_DETAILS: [MessageHandler(filters.Text() & ~filters.Command(), alcohol_details)],
    },
    fallbacks=[CommandHandler('stop', stop)]
)
#timezone_handler = CommandHandler('timezone', set_time_zone)

    # Add handlers to the application
application.add_handler(start_handler)
application.add_handler(stop_handler)
application.add_handler(food_handler)
application.add_handler(commands_handler)
application.add_handler(water_handler)
application.add_handler(coffee_handler)
application.add_handler(timezone_handler)
application.add_handler(alcohol_handler)

    # Run polling
application.run_polling()

