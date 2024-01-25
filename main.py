from asyncore import dispatcher
import os
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler
from commands import (start, stop, commands, water, ask_water_intake,
                      food, ask_if_eaten_before, meal_time, meal_type, 
                      meal_details, ask_meal_details, coffee, ask_coffee_intake,
                      alcohol, ask_alcohol_type, alcohol_details)
from commands import (start_handler, stop_handler, commands_handler, water_handler, 
                      food_handler, coffee_handler, alcohol_handler, mood_handler, symptom_handler,
                      wellbeing_handler, vitamins_supplements_handler, sleep_handler, social_battery_handler, heart_palpitation_handler, cold_handler,
                      productivity_handler, day_rating_handler, hygiene_handler)
from server import app

# from server import app
from threading import Thread
import json
#from telegram.ext import JobQueue

# `env`
telegram_token = os.getenv('API_KEY')

if __name__ == '__main__':
    application = ApplicationBuilder().token(telegram_token).build()
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()


    # Add handlers to the application
#application.add_handler(timezone_handler)
application.add_handler(start_handler)
application.add_handler(stop_handler)
application.add_handler(food_handler)
application.add_handler(commands_handler)
application.add_handler(water_handler)
application.add_handler(coffee_handler)
application.add_handler(alcohol_handler)
application.add_handler(mood_handler)
application.add_handler(symptom_handler)
application.add_handler(wellbeing_handler)
application.add_handler(vitamins_supplements_handler)
application.add_handler(sleep_handler)
application.add_handler(social_battery_handler)
application.add_handler(heart_palpitation_handler)
application.add_handler(cold_handler)
application.add_handler(productivity_handler)
application.add_handler(day_rating_handler)
application.add_handler(hygiene_handler)
#application.add_handler(morning_handler)
    # Run polling
application.run_polling()