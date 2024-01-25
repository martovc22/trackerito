from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, CallbackContext
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton
from telegram.ext import CallbackContext
from googlesheetsimport import log_water_intake, log_alcohol_intake, log_coffee_intake, insert_into_sheet_food, log_mood, log_symptoms, log_wellbeing
from googlesheetsimport import log_vitamins_supplements, log_sleep_data, log_social_battery_energy, log_heart_palpitations_data, cold_symptoms_data
from googlesheetsimport import log_productivity_data, log_day_overall, log_hygiene_data
from datetime import datetime
from googlesheetsimport import tz_str as time_zone
from telegram.ext import JobQueue





# Stop command function
async def stop(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    user_data['notifications_paused'] = True
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🤖Notifications are now paused. Use /start or /resume when you're ready to receive notifications again."
    )

# Start command function
async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Hello, I'm your personal tracking assistant bot! 👾 \n"
              "We will log your daily activities and track aspects of your life to quantify it eventually.\n"
              "Let's get started with your daily tracking. Use /commands shall you need any help."),
        parse_mode='HTML'
    )

# Command function - NEED TO ADD THEM ALL
async def commands(update: Update, context: CallbackContext) -> None:
    # Send available commands
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🚨The commands you can use are:\n"
             "/start - Start the bot\n"
             "/stop - Stop the bot\n"
             "/commands - Get help\n"
             "/food -  Log your food intake\n"
             "/awake - Log your wake up time\n"
             "/coffee - Log your coffee intake\n"
             "/alcohol - Log your alcohol intake\n"
             "/water - Log your water intake\n"
             "/mood - Log your mood\n"
             "/symptom - Log your symptoms\n"
            "/wellbeing - Log your well-being\n"
            "/vitamins - Log your vitamins and supplements\n"
            "/sleep - Log your sleep\n"
            "/battery - Log your social battery\n"
            "/palpitations - Log your heart palpitations\n"
            "/cold - Log your cold symptoms\n"
            "/productivity - Log your productivity\n"
            "/day_rate - rate your day overall\n"
            "/hygiene - Log your hygiene\n"
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
    log_water_intake(intake_volume, time_zone)
    await update.message.reply_text('Thank you for logging your water intake!')
    return ConversationHandler.END

# Food intake command functions
ASK_IF_EATEN_BEFORE, MEAL_TIME, ASK_MEAL_DETAILS, TYPE_OF_MEAL, MEAL_DETAILS, ASK_MEAL_DATE_TIME, MEAL_DATE_TIME = range(7)
# Food eat now/before
async def food(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Now 🍽️', 'Before🍴']]
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
        return MEAL_DATE_TIME
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
    await update.message.reply_text('What food did you have?:')
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

# Coffee

coffee_intake, cups, ASK_COFFEE_INTAKE = range(3)
async def coffee(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Yes', 'No']]
    user_choice = update.message.text
    await update.message.reply_text('Did you drink coffee today?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ASK_COFFEE_INTAKE

async def ask_coffee_intake(update: Update, context: CallbackContext) -> int:
    cups_input = update.message.text
    cups = None  # Initialize 'cups'
    if cups_input in ['Yes', 'No']:
        if cups_input == 'Yes':
            await update.message.reply_text('How many cups of coffee did you drink?')
            return cups
        else:
            # If the user answered 'No', end the conversation
            await update.message.reply_text('No coffee logged.')
            return ConversationHandler.END
    else:
        try:
            cups = int(cups_input)
            if 1 <= cups <= 10:
                log_coffee_intake(cups, context.user_data.get('time_zone', 'UTC'))
                await update.message.reply_text(f'Thank you for logging your {cups} cup(s) of coffee!')
                return ConversationHandler.END
            else:
                await update.message.reply_text('Invalid input. Please enter a number between 1 and 10.')
                return cups 
        except ValueError:
            await update.message.reply_text('Invalid input. Please enter a valid number.')
            return cups  
# Alcohol intake 
ASK_ALCOHOL_TYPE, ALCOHOL_DETAILS = range(2)

# Function to start alcohol logging
async def alcohol(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Wine 🍷', 'Beer 🍺', 'Spirits🍸', 'Gin 🍹', 'Champagne 🥂', 'Other 🎉'], ['No']]
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

# Mood Tracking
MOOD_TRACKING, ASK_MOOD_TIME, MOOD_SCALE = range(3)

async def mood(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Morning☀️', 'Afternoon🌄', 'Evening🌛', 'Now🌆']]
    await update.message.reply_text('Shall we track your mood?',
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ASK_MOOD_TIME

async def ask_mood_time(update: Update, context: CallbackContext) -> int:
    time_of_day = update.message.text
    if time_of_day in ['Morning☀️', 'Afternoon🌄', 'Evening🌛', 'Now🌆']:
        context.user_data['mood_time'] = time_of_day
        reply_keyboard = [
            ['0 - Absolutely awful 💀', '1 - Not great 😔', '2 - So/so 🫠', '3 - Better, but not great 😾'],
            [ '4 - Oh Yeah 🙂', '5 - Excellent, sun is shining, so am I 🌟']
            ]
        await update.message.reply_text('How would you rate your mood?',
                                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return MOOD_SCALE
    else:
        await update.message.reply_text('Invalid input. Please choose from Morning, Afternoon, Evening, or Right Now.')
        return ASK_MOOD_TIME

async def mood_scale(update: Update, context: CallbackContext) -> int:
    mood_rating_text = update.message.text
    mood_rating = mood_rating_text[0] if mood_rating_text else ''
    mood_time = context.user_data['mood_time']
    try:
        mood_rating = int(mood_rating)
        if 0 <= mood_rating <= 5:
            log_mood(mood_time, mood_rating, time_zone)
            await update.message.reply_text(f'Mood logged!')
            return ConversationHandler.END
        else:
            await update.message.reply_text('Invalid input. Please enter a number between 0 and 5.')
            return MOOD_SCALE
    except ValueError:
        await update.message.reply_text('Invalid input. Please enter a valid number.')
        return MOOD_SCALE

# Symptom tracking

SYMPTOM_TRACKING, FATIGUE, HEADACHES, STOMACHACHE, BREATHING_DIFFICULTIES, OTHER_SYMPTOMS, SYMPTOM_SCALE, BRAIN_FOG = range(8)

SYMPTOMS = ['Fatigue😵', 'Headaches🤕', 'Stomach Ache🤢', 'Breathing Difficulties😪', 'Brain Fog🌫️' 'Other😶‍🌫️']

async def symptoms(update: Update, context: CallbackContext, symptom: str) -> int:
    if symptom == 'others':
        await update.message.reply_text("Please specify the symptom you're experiencing.")
        return OTHER_SYMPTOMS
    else:
        await update.message.reply_text(f"Do you have {symptom}? (Rate from 0-5)")
        context.user_data['current_symptom'] = symptom
        return SYMPTOM_SCALE
    
async def other_symptoms(update: Update, context: CallbackContext) -> int:
    context.user_data['current_symptom'] = update.message.text
    await update.message.reply_text(f"Do you have {context.user_data['current_symptom']}? (Rate from 0-5)")
    return SYMPTOM_SCALE

async def symptom_scale(update: Update, context: CallbackContext) -> int:
    symptom_rating_text = update.message.text
    symptom_rating = symptom_rating_text[0] if symptom_rating_text else ''
    try:
        symptom_rating = int(symptom_rating)
        if 0 <= symptom_rating <= 5:
            context.user_data['symptom_index'] += 1
            if not (context.user_data['current_symptom'].lower() == 'others' and symptom_rating == 0):
                log_symptoms(context.user_data['current_symptom'], symptom_rating, f"Do you have {context.user_data['current_symptom']}?", time_zone)
                await update.message.reply_text(f"Symptom rating logged!")
            if context.user_data['symptom_index'] < len(SYMPTOMS):
                return await symptoms(update, context, SYMPTOMS[context.user_data['symptom_index']])
            else:
                return ConversationHandler.END
        else:
            await update.message.reply_text('Invalid input. Please enter a number between 0 and 5.')
            return SYMPTOM_SCALE
    except ValueError:
        await update.message.reply_text('Invalid input. Please enter a valid number.')
        return SYMPTOM_SCALE

async def track_all_symptoms(update: Update, context: CallbackContext) -> int:
    context.user_data['symptom_index'] = 0
    reply_keyboard = [['0 - 😇 No symptoms', '1 - 😊 Feeling it a little bit'],
                      ['2 - 😕 Mild discomfort', '3 - 😟 Moderate discomfort'],
                      ['4 - 😖 Strong discomfort', '5 - 😫 Really uncomfortable here']]
    await update.message.reply_text('Please rate your symptoms:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return await symptoms(update, context, SYMPTOMS[context.user_data['symptom_index']])
# Well-being tracking
WELLBEING_TRACKING, STRESS, ENERGY_LEVELS, HAPPINESS, ANXIETY, STRESS_CAUSE, STRESS_RELATED_HUNGER, WELLBEING_SCALE = range(8)

WELLBEING_CATEGORIES = ['Stress😫', 'Energy Levels⚡️', 'Happiness😊', 'Anxiety😰', 'Stress Cause🔍', 'Stress-Related Hunger🍔']

async def wellbeing(update: Update, context: CallbackContext) -> int:
    context.user_data['category_index'] = 0
    return await wellbeing_categories(update, context, WELLBEING_CATEGORIES[0])

async def wellbeing_categories(update: Update, context: CallbackContext, category: str) -> int:
    # Set the current category
    context.user_data['current_category'] = category

    if category in ['Stress😫', 'Energy Levels⚡️', 'Happiness😊', 'Anxiety😰']:
        reply_keyboard = [['0 - 😢 Very low', '1 - 😕 Low'],
                          ['2 - 😐 Meh', '3 - 😊 Moderate'],
                          ['4 - 😄 High', '5 - 😁 Very high']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f"On a scale of 0-5, how would you rate your {category}?", reply_markup=reply_markup)
    elif category == 'Stress Cause🔍':
        await update.message.reply_text(f"What is causing your stress today?")
    elif category == 'Stress-Related Hunger🍔':
        reply_keyboard = [['Yes', 'No']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f"Are you feeling hungry due to stress?", reply_markup=reply_markup)
    
    return WELLBEING_SCALE

async def wellbeing_scale(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    current_category = user_data['current_category']
    
    if current_category == 'Stress Cause🔍':
        stress_cause_text = update.message.text
        log_wellbeing(current_category, stress_cause_text, "What is causing your stress today?")
        await update.message.reply_text(f"{current_category} logged successfully.")
    elif current_category == 'Stress-Related Hunger🍔':
        stress_hunger_response = update.message.text
        log_wellbeing(current_category, stress_hunger_response, "Are you hungry from stress?")
        await update.message.reply_text(f"{current_category} logged successfully.")
    else:
        category_rating_text = update.message.text
        category_rating = category_rating_text[0] if category_rating_text else ''
        try:
            category_rating = int(category_rating)
            if 0 <= category_rating <= 5:
                log_wellbeing(current_category, category_rating, f"On a scale of 0-5, how would you rate your {current_category}?")
                await update.message.reply_text(f"Well-being rating logged!")
            else:
                await update.message.reply_text('Invalid input. Please enter a number between 0 and 5.')
                return WELLBEING_SCALE
        except ValueError:
            await update.message.reply_text('Invalid input. Please enter a valid number.')
            return WELLBEING_SCALE

    user_data['category_index'] += 1  # Increment after handling the response

    if user_data['category_index'] >= len(WELLBEING_CATEGORIES):
        return ConversationHandler.END
    else:
        return await wellbeing_categories(update, context, WELLBEING_CATEGORIES[user_data['category_index']])


# Vitamins & Supplements tracking
VITAMINS, VITAMINS_CATEGORIES = range(2)
VITAMINS_SUPPLEMENTS_CATEGORIES = ['Magnesium', 'Zinc', 'Vitamin D', 'Vitamin B', 'Vitamin A', 'Vitamin C', 'Others']
SUPPLEMENTS = ['Piracetam', 'Collagen']


# Start the vitamins and supplements tracking conversation
async def vitamins(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Did you have any vitamins or supplements today? (Yes/No)')
    return VITAMINS_CATEGORIES

async def vitamins_categories(update: Update, context: CallbackContext) -> int:
    print("vitamins_categories function called")
    user_text = update.message.text
    if user_text == 'Yes':
        context.user_data['vitamin_index'] = 0
        await update.message.reply_text(f"Did you have {VITAMINS_SUPPLEMENTS_CATEGORIES[0]} today?", reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True))
        return VITAMINS
    elif user_text == 'No':
        await update.message.reply_text('No vitamins or supplements logged.')
        return ConversationHandler.END  # End the conversation here
    else:
        print(f"Unexpected user input: {user_text}")  # Debugging statement
        return ConversationHandler.END
    
async def log_vitamin(update: Update, context: CallbackContext) -> int:
    vitamin_index = context.user_data.get('vitamin_index', 0)
    user_text = update.message.text
    if user_text == 'Yes':
        # Log that the user had 1 of the current vitamin or supplement
        context.user_data[VITAMINS_SUPPLEMENTS_CATEGORIES[vitamin_index]] = 1
        log_vitamins_supplements(VITAMINS_SUPPLEMENTS_CATEGORIES[vitamin_index], 1)  # Log the data to the Google Sheet
        vitamin_index += 1
    elif user_text == 'No':
        log_vitamins_supplements(VITAMINS_SUPPLEMENTS_CATEGORIES[vitamin_index], 0)  # Log the data to the Google Sheet
        vitamin_index += 1
    else:
        await update.message.reply_text('Invalid response. Please respond with either "Yes" or "No".')
        return ConversationHandler.END

    context.user_data['vitamin_index'] = vitamin_index  # Store the updated index back into context.user_data

    if vitamin_index < len(VITAMINS_SUPPLEMENTS_CATEGORIES):
        # Ask about the next vitamin or supplement
        await update.message.reply_text(f"Did you have {VITAMINS_SUPPLEMENTS_CATEGORIES[vitamin_index]} today?", reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True))
        return VITAMINS
    else:
        # If there are no more vitamins or supplements to ask about, end the conversation
        await update.message.reply_text('Vitamins and supplements logged.')
        return ConversationHandler.END
    

# Sleep tracking
SLEEP, SLEEP_DURATION, SLEEP_QUALITY, HEART_RATE, FEELING_RESTED = range(5)

async def sleep(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('How long did you sleep (in hours)?')
    return SLEEP_DURATION

async def sleep_duration(update: Update, context: CallbackContext) -> int:
    duration = update.message.text
    context.user_data['sleep_duration'] = duration
    await update.message.reply_text('Rate the quality of your sleep (1-5):', reply_markup=ReplyKeyboardMarkup([['1 - 😩 Very Unrested', '2 - 😕 Unrested', '3 - 😐 Neutral', '4 - 😊 Rested', '5 - 😁 Very Rested']], one_time_keyboard=True, resize_keyboard=True))
    return SLEEP_QUALITY

async def sleep_quality(update: Update, context: CallbackContext) -> int:
    quality = update.message.text.split(' ')[0]
    context.user_data['sleep_quality'] = quality
    await update.message.reply_text('What was your average heart rate during sleep?')
    return HEART_RATE

async def heart_rate(update: Update, context: CallbackContext) -> int:
    heart_rate = update.message.text
    context.user_data['heart_rate'] = heart_rate
    await update.message.reply_text('How rested do you feel (1-5)?', reply_markup=ReplyKeyboardMarkup([['1 - 😩 Very Unrested', '2 - 😕 Unrested', '3 - 😐 Neutral', '4 - 😊 Rested', '5 - 😁 Very Rested']], one_time_keyboard=True, resize_keyboard=True))
    return FEELING_RESTED

async def feeling_rested(update: Update, context: CallbackContext) -> int:
    feeling_rested = update.message.text.split(' ')[0]
    # feeling_rested = context.user_data['feeling_rested']
    sleep_duration = context.user_data['sleep_duration']
    sleep_quality = context.user_data['sleep_quality']
    heart_rate = context.user_data['heart_rate']
    log_sleep_data(sleep_duration, sleep_quality, heart_rate, feeling_rested)
    await update.message.reply_text('Sleep data logged.')
    return ConversationHandler.END

async def log_sleep(update: Update, context: CallbackContext) -> int:
    user_text = update.message.text
    if user_text in ['Yes', 'No']:
        context.user_data['log_sleep_data'] = user_text
        await update.message.reply_text('How rested do you feel (1-5)?', reply_markup=ReplyKeyboardMarkup([['1 - 😩 Very Unrested', '2 - 😕 Unrested', '3 - 😐 Neutral', '4 - 😊 Rested', '5 - 😁 Very Rested']], one_time_keyboard=True, resize_keyboard=True))
        return FEELING_RESTED
    else:
        await update.message.reply_text('Invalid response. Please respond with either "Yes" or "No".')
        return ConversationHandler.END

# Social battery
SOCIAL_BATTERY, LOG_BATTERY = range(2)

async def ask_social_battery(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        'How is your social battery? (1 - Low, 2 - Medium, 3 - High)', 
        reply_markup=ReplyKeyboardMarkup([['1 - Low', '2 - Medium', '3 - High']], one_time_keyboard=True, resize_keyboard=True)
    )
    return LOG_BATTERY

async def log_social_battery(update: Update, context: CallbackContext) -> int:
    social_battery = int(update.message.text.split(' ')[0])  # Extract the number from the response
    log_social_battery_energy(social_battery)
    await update.message.reply_text('Social battery logged.')
    return ConversationHandler.END

# Heart palpitations
HEART_PALPITATIONS, LOG_PALPITATIONS = range(2)

async def ask_heart_palpitations(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        'Did you experience any heart palpitations?', 
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True)
    )
    return LOG_PALPITATIONS

async def log_heart_palpitations(update: Update, context: CallbackContext) -> int:
    heart_palpitations = update.message.text
    log_heart_palpitations_data(heart_palpitations)
    await update.message.reply_text('Heart palpitations logged.')
    return ConversationHandler.END

# Cold symptoms
LOG_COLD_SYMPTOMS, LOG_COLD_SYMPTOMS_DETAILS = range(2)

async def ask_cold_symptoms(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        'Do you have any cold symptoms? (Yes/No)', 
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True)
    )
    return LOG_COLD_SYMPTOMS

async def log_cold_symptoms(update: Update, context: CallbackContext) -> int:
    cold_symptoms = update.message.text
    if cold_symptoms == 'No':
        await update.message.reply_text('No cold symptoms logged.')
        return ConversationHandler.END
    elif cold_symptoms == 'Yes':
        context.user_data['cold_symptoms'] = []  # Initialize the list to store symptoms
        return await ask_for_symptoms(update, context)

async def ask_for_symptoms(update: Update, context: CallbackContext) -> int:
    # List of cold symptoms to ask
    symptoms_list = ['Runny nose', 'Stuffed nose', 'Sore throat', 'Cough', 'Fever', 'Body ache']
    # Ask for the first symptom
    await update.message.reply_text(
        f"Do you have a {symptoms_list[0]}? (Yes/No)",
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True)
    )
    context.user_data['current_symptom_index'] = 0
    return LOG_COLD_SYMPTOMS_DETAILS

async def log_cold_symptoms_details(update: Update, context: CallbackContext) -> int:
    symptoms_list = ['Runny nose', 'Stuffed nose', 'Sore throat', 'Cough', 'Fever', 'Body ache']
    index = context.user_data['current_symptom_index']
    response = update.message.text

    if response == 'Yes':
        symptom = symptoms_list[index]
        context.user_data['cold_symptoms'].append(symptom)
        cold_symptoms_data(symptom)

    # more symptoms? check
    index += 1
    if index < len(symptoms_list):
        await update.message.reply_text(
            f"Do you have a {symptoms_list[index]}? (Yes/No)",
            reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True)
        )
        context.user_data['current_symptom_index'] = index
        return LOG_COLD_SYMPTOMS_DETAILS
    else:
        await update.message.reply_text('All symptoms logged.')
        return ConversationHandler.END

# Feeling productive tracking
PRODUCTIVITY_RATING = range(9)
async def ask_productivity(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1 - 😴 Not productive', '2 - 🙁 Slightly productive'],
                      ['3 - 😐 Moderately productive', '4 - 🙂 Quite productive'],
                      ['5 - 🌟 Highly productive']]
    await update.message.reply_text(
        'How productive are you feeling today? (Rate from 1-5)',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return PRODUCTIVITY_RATING
async def log_productivity(update: Update, context: CallbackContext) -> int:
    productivity_rating = update.message.text.split(' ')[0]  # Extracts the number from the response
    try:
        productivity_rating = int(productivity_rating)
        if 1 <= productivity_rating <= 5:
            log_productivity_data(productivity_rating)
            await update.message.reply_text(f"Productivity rating of {productivity_rating} logged!")
            return ConversationHandler.END
        else:
            await update.message.reply_text('Invalid input. Please enter a number between 1 and 5.')
            return PRODUCTIVITY_RATING
    except ValueError:
        await update.message.reply_text('Invalid input. Please enter a valid number.')
        return PRODUCTIVITY_RATING



# Rating the day overall (in the evening)
DAY_RATING = range(10)
async def ask_day_rating(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1 - 😞 Very Bad', '2 - 🙁 Bad'],
                      ['3 - 😐 Okay', '4 - 🙂 Good'],
                      ['5 - 🌟 Excellent']]
    await update.message.reply_text(
        'How would you rate your day overall? (Rate from 1-5)',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return DAY_RATING

async def log_day_rating(update: Update, context: CallbackContext) -> int:
    day_rating = update.message.text.split(' ')[0]  # Extracts the number from the response
    try:
        day_rating = int(day_rating)
        if 1 <= day_rating <= 5:
            log_day_overall(day_rating)
            await update.message.reply_text(f"Day rating of {day_rating} logged!")
            return ConversationHandler.END
        else:
            await update.message.reply_text('Invalid input. Please enter a number between 1 and 5.')
            return DAY_RATING
    except ValueError:
        await update.message.reply_text('Invalid input. Please enter a valid number.')
        return DAY_RATING

# Hygiene/routine tracking
HYGIENE_ROUTINE, SKIN_CARE, BRUSHING_TEETH, SHOWER, SHAVE = range(5)
async def ask_hygiene_routine(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Let's go through your hygiene routine. Did you take care of your skin today? (Yes/No)",
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True)
    )
    return SKIN_CARE
async def ask_skin_care(update: Update, context: CallbackContext) -> int:
    context.user_data['hygiene'] = {'skin_care': update.message.text}
    await update.message.reply_text(
        "Burshed your teeth?",
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True)
    )
    return BRUSHING_TEETH

async def ask_brushing_teeth(update: Update, context: CallbackContext) -> int:
    context.user_data['hygiene']['brushing_teeth'] = update.message.text
    await update.message.reply_text(
        "Did you take a shower?",
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True)
    )
    return SHOWER

async def ask_shower(update: Update, context: CallbackContext) -> int:
    context.user_data['hygiene']['shower'] = update.message.text
    await update.message.reply_text(
        "Did you shave?",
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True)
    )
    return SHAVE

async def ask_shave(update: Update, context: CallbackContext) -> int:
    context.user_data['hygiene']['shave'] = update.message.text
    log_hygiene_data(context.user_data['hygiene'])
    await update.message.reply_text("Hygiene routine logged. Thank you!")
    return ConversationHandler.END



# Handlers
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

mood_handler = ConversationHandler(
    entry_points=[CommandHandler('mood', mood)],
    states={
        MOOD_SCALE: [MessageHandler(filters.Text() & ~filters.Command(), mood_scale)],
        ASK_MOOD_TIME: [MessageHandler(filters.Text() & ~filters.Command(), ask_mood_time)],
    },
    fallbacks=[CommandHandler('stop', stop)]
)

symptom_handler = ConversationHandler(
    entry_points=[CommandHandler('symptom', track_all_symptoms)],
    states={
        FATIGUE: [MessageHandler(filters.Text() & ~filters.Command(), lambda u, c: symptoms(u, c, 'fatigue'))],
        HEADACHES: [MessageHandler(filters.Text() & ~filters.Command(), lambda u, c: symptoms(u, c, 'headaches'))],
        STOMACHACHE: [MessageHandler(filters.Text() & ~filters.Command(), lambda u, c: symptoms(u, c, 'stomachache'))],
        BREATHING_DIFFICULTIES: [MessageHandler(filters.Text() & ~filters.Command(), lambda u, c: symptoms(u, c, 'breathing difficulties'))],
        BRAIN_FOG: [MessageHandler(filters.Text() & ~filters.Command(), lambda u, c: symptoms(u, c, 'brain fog'))], 
        OTHER_SYMPTOMS: [MessageHandler(filters.Text() & ~filters.Command(), other_symptoms)],
        SYMPTOM_SCALE: [MessageHandler(filters.Text() & ~filters.Command(), symptom_scale)],
    },
    fallbacks=[CommandHandler('stop', stop)]
)


wellbeing_handler = ConversationHandler(
    entry_points=[CommandHandler('wellbeing', wellbeing)],
    states={
        STRESS: [MessageHandler(filters.Text() & ~filters.Command(), lambda u, c: wellbeing_categories(u, c, 'Stress😫'))],
        ENERGY_LEVELS: [MessageHandler(filters.Text() & ~filters.Command(), lambda u, c: wellbeing_categories(u, c, 'Energy Levels⚡️'))],
        HAPPINESS: [MessageHandler(filters.Text() & ~filters.Command(), lambda u, c: wellbeing_categories(u, c, 'Happiness😊'))],
        ANXIETY: [MessageHandler(filters.Text() & ~filters.Command(), lambda u, c: wellbeing_categories(u, c, 'Anxiety😰'))],
       #STRESS_AVERAGE: [MessageHandler(filters.Text() & ~filters.Command(), lambda u, c: wellbeing_categories(u, c, 'Stress Average📊'))],
        STRESS_CAUSE: [MessageHandler(filters.Text() & ~filters.Command(), lambda u, c: wellbeing_categories(u, c, 'Stress Cause🔍'))],
        STRESS_RELATED_HUNGER: [MessageHandler(filters.Text() & ~filters.Command(), lambda u, c: wellbeing_categories(u, c, 'Stress-Related Hunger🍔'))],
        WELLBEING_SCALE: [MessageHandler(filters.Text() & ~filters.Command(), wellbeing_scale)],
    },
    fallbacks=[CommandHandler('stop', stop)]
)


vitamins_supplements_handler = ConversationHandler(
    entry_points=[CommandHandler('vitamins', vitamins)],
    states={
        VITAMINS_CATEGORIES: [MessageHandler(filters.Text() & ~filters.Command(), vitamins_categories)],
        VITAMINS: [MessageHandler(filters.Text() & ~filters.Command(), log_vitamin)],
    },
    fallbacks=[CommandHandler('stop', stop)],
)

sleep_handler = ConversationHandler(
    entry_points=[CommandHandler('sleep', sleep)],
    states={
        SLEEP_DURATION: [MessageHandler(filters.Text() & ~filters.Command(), sleep_duration)],
        SLEEP_QUALITY: [MessageHandler(filters.Text() & ~filters.Command(), sleep_quality)],
        HEART_RATE: [MessageHandler(filters.Text() & ~filters.Command(), heart_rate)],
        FEELING_RESTED: [MessageHandler(filters.Text() & ~filters.Command(), feeling_rested)],
    },
    fallbacks=[CommandHandler('stop', stop)]
)

social_battery_handler = ConversationHandler(
    entry_points=[CommandHandler('battery', ask_social_battery)],
    states={
        SOCIAL_BATTERY: [MessageHandler(filters.Text() & ~filters.Command(), ask_social_battery)],
        LOG_BATTERY: [MessageHandler(filters.Text() & ~filters.Command(), log_social_battery)]
    },
    fallbacks=[CommandHandler('stop', stop)]
)



heart_palpitation_handler = ConversationHandler(
    entry_points=[CommandHandler('palpitations', ask_heart_palpitations)],
    states={
        LOG_PALPITATIONS: [MessageHandler(filters.Text() & ~filters.Command(), log_heart_palpitations)],
    },
    fallbacks=[CommandHandler('stop', stop)]
)



cold_handler = ConversationHandler(
    entry_points=[CommandHandler('cold', ask_cold_symptoms)],
    states={
        LOG_COLD_SYMPTOMS: [MessageHandler(filters.Text() & ~filters.Command(), log_cold_symptoms)],
        LOG_COLD_SYMPTOMS_DETAILS: [MessageHandler(filters.Text() & ~filters.Command(), log_cold_symptoms_details)],
    },
    fallbacks=[CommandHandler('stop', stop)]
)

productivity_handler = ConversationHandler(
    entry_points=[CommandHandler('productivity', ask_productivity)],
    states={
        PRODUCTIVITY_RATING: [MessageHandler(filters.Text() & ~filters.Command(), log_productivity)]
    },
    fallbacks=[CommandHandler('stop', stop)]
)

day_rating_handler = ConversationHandler(
    entry_points=[CommandHandler('day', ask_day_rating)],
    states={
        DAY_RATING: [MessageHandler(filters.Text() & ~filters.Command(), log_day_rating)]
    },
    fallbacks=[CommandHandler('stop', stop)]
)

hygiene_handler = ConversationHandler(
    entry_points=[CommandHandler('hygiene', ask_hygiene_routine)],
    states={
        SKIN_CARE: [MessageHandler(filters.Text() & ~filters.Command(), ask_skin_care)],
        BRUSHING_TEETH: [MessageHandler(filters.Text() & ~filters.Command(), ask_brushing_teeth)],
        SHOWER: [MessageHandler(filters.Text() & ~filters.Command(), ask_shower)],
        SHAVE: [MessageHandler(filters.Text() & ~filters.Command(), ask_shave)],
    },
    fallbacks=[CommandHandler('stop', stop)]
)
