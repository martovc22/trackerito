async def wellbeing_categories(update: Update, context: CallbackContext, category: str) -> int:
    reply_keyboard = [['0 - 😢 Very low', '1 - 😕 Low'],
                      ['2 - 😐 Meh', '3 - 😊 Moderate'],
                      ['4 - 😄 High', '5 - 😁 Very high']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await update.message.reply_text(f"On a scale of 0-5, how would you rate your {category}?", reply_markup=reply_markup)
    context.user_data['current_category'] = category
    return WELLBEING_SCALE
    


    async def wellbeing_scale(update: Update, context: CallbackContext) -> int:
    if 'category_index' not in context.user_data:
        context.user_data['category_index'] = 0
    category_rating_text = update.message.text
    category_rating = category_rating_text[0] if category_rating_text else ''
    try:
        category_rating = int(category_rating)
        if 0 <= category_rating <= 5:
            context.user_data['category_index'] += 1
            log_wellbeing(context.user_data['current_category'], category_rating, f"On a scale of 0-5, how would you rate your {context.user_data['current_category']}?")
            await update.message.reply_text(f"Well-being rating logged!")
            if context.user_data['category_index'] < len(WELLBEING_CATEGORIES):
                return await wellbeing_categories(update, context, WELLBEING_CATEGORIES[context.user_data['category_index']])
            else:
                return ConversationHandler.END
        else:
            await update.message.reply_text('Invalid input. Please enter a number between 0 and 5.')
            return WELLBEING_SCALE
    except ValueError:
        await update.message.reply_text('Invalid input. Please enter a valid number.')
        return WELLBEING_SCALE
    







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






if category in ['Stress😫', 'Energy Levels⚡️', 'Happiness😊', 'Anxiety😰', 'Stress Cause🔍', 'Stress-Related Hunger🍔']:
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

    context.user_data['current_category'] = category
    return WELLBEING_SCALE