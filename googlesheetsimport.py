from dotenv import load_dotenv 
import random
from pytz import timezone
import pytz
import uuid
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
import json
from datetime import datetime, time

# Time of the day
def get_time_of_day():
    current_time = datetime.now().time()
    if time(7, 0) <= current_time <= time(13, 0):
        return 'morning'
    elif time(13, 1) <= current_time <= time(17, 0):
        return 'afternoon'
    else:
        return 'evening'


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

load_dotenv()
SPREAD_SHEET_ID = os.getenv('SPREAD_SHEET_ID')
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)


# Constants 
    

SOURCE = 'telegram'
SPREADSHEET_RANGE = 'Sheet1!A:A'
VALUE_INPUT_OPTION = 'USER_ENTERED'

#tz = pytz.timezone('Europe/Prague') # gotta edit this later for the actual timezone
tz_str = 'Europe/Prague'
tz = tz_str

# General function to log data into the google sheet
def log_data_to_sheet(key, data, question,source=SOURCE,food_actual_time=None):
    try:
        unique_id = str(random.randint(1000000000, 9999999999))
        current_time = datetime.now()
        date = current_time.strftime("%Y-%m-%d %H:%M")
        time = current_time.strftime("%H:%M:%S")
        imported_at_time = imported_at_time = food_actual_time if food_actual_time is not None else current_time.strftime("%Y-%m-%d %H:%M") # might not work 
        data_type = str(type(data).__name__)  # Get the data type of data
        values = [[unique_id, date, imported_at_time, time, tz, key, question, data_type, data, source,]]
        body = {'values': values}
        result = service.spreadsheets().values().append(spreadsheetId=SPREAD_SHEET_ID, range=SPREADSHEET_RANGE, valueInputOption=VALUE_INPUT_OPTION, body=body).execute()
        print(f"{key} logged successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

      # Function to insert food intake into google sheets
def insert_into_sheet_food(meal_datetime, timestamp, meal_details, meal_type):
    key = f"meal_type_{meal_type}".lower()
    food_actual_time = meal_datetime.split()[0]
    question = "What kind of food did you have?"
    log_data_to_sheet(key, meal_details, food_actual_time=food_actual_time)

# Function to insert water intake into google sheets
def log_water_intake(volume, time_zone):
    key = 'water_intake'
    question = "How much water did you have today?"
    log_data_to_sheet(key, volume)

# Function to insert coffee intake into google sheets
def log_coffee_intake(cups, time_zone):
    key = 'coffee_intake'
    question = "How many cups of coffee did you have today?"
    log_data_to_sheet(key, cups, question)

# Function to insert alcohol intake into google sheets
def log_alcohol_intake(alcohol_type, alcohol_quantity, time_zone):
    # Construct a key that includes both the type and the quantity of alcohol
    key = alcohol_type
    data = alcohol_quantity
    log_data_to_sheet(key, data, tz)

# Function to insert mood rating into google sheets
def log_mood(mood_time, mood_rating, time_zone):
    # Key representing the time of day for mood logging
    mood_key = f"mood_{mood_time}".lower()
    data = mood_rating
    question = "How are you feeling today?"
    log_data_to_sheet(mood_key, data, question)


def log_symptoms(symptoms, symptom_rating, question, time_zone):
    question = "How intensive is it?"
    key = f"symptoms_of_{symptoms}".lower()
    log_data_to_sheet(symptoms, symptom_rating, question)


def log_wellbeing(category, wellbeing_rating, message):
    time_of_day = get_time_of_day()
    key = f"{category}_{time_of_day}".lower()
    question = "How's them feelings?"
    log_data_to_sheet(key, wellbeing_rating, question)


def log_vitamins_supplements(item, took):
    time_of_day = get_time_of_day()
    key = f"vitamin_supplement_{item}_{time_of_day}".lower()
    question = f"Did you take {item} today?"
    log_data_to_sheet(key, int(took), question)

def log_sleep_data(sleep_duration, sleep_quality, heart_rate, feeling_rested):
    sleep_params = {
        'sleep_duration': sleep_duration,
        'sleep_quality': sleep_quality,
        'heart_rate': heart_rate,
        'feeling_rested': feeling_rested
    }
    question = 'How was your sleep?'
    for param, value in sleep_params.items():
        key = f"sleep_{param}".lower()
        log_data_to_sheet(key, value, question)

def log_social_battery_energy(social_battery):
    key = f"social_battery".lower()
    question = "How's your social battery?"
    log_data_to_sheet(key, social_battery, question)

def log_heart_palpitations_data(heart_palpitations):
    key = f"heart_palpitations".lower()
    question = "Have you experienced any heart palpitations?"
    log_data_to_sheet(key, heart_palpitations, question)


def cold_symptoms_data(cold_symptoms):
    key = f"cold_symptoms".lower()
    question = "Have you experienced any cold symptoms?"
    log_data_to_sheet(key, cold_symptoms, question)

def log_productivity_data(productivity_rating):
    key = f"productivity".lower()
    question = "Are you feeling productive? (1-5)"
    log_data_to_sheet(key, productivity_rating, question)

def log_day_overall(day_overall_rating):
    key = f"day_overall".lower()
    question = "How was your day overall? (1-5)"
    log_data_to_sheet(key, day_overall_rating, question)

def log_hygiene_data(hygiene_data):
    time_of_day = get_time_of_day()
    for activity, response in hygiene_data.items():
        key = f"hygiene_{activity}_{time_of_day}".lower()
        question = f"Did you {activity.replace('_', ' ')} today?"
        log_data_to_sheet(key, response, question)
    print("Hygiene data logged successfully.")
