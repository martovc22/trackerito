# Timezone fuction - the simpler way of 2 locations for now UK/CZ 
UK_TIME_ZONE = 'Europe/London'
CZ_TIME_ZONE = 'Europe/Prague'

SET_TIMEZONE = range(1)

async def set_timezone(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [[UK_TIME_ZONE], [CZ_TIME_ZONE]]
    current_timezone = context.user_data.get('timezone')
    if current_timezone:
        await update.message.reply_text(
            f'Your current timezone is {current_timezone}. You can change it below:',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    else:
        await update.message.reply_text(
            'Please select your timezone:',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    
    return SET_TIMEZONE

async def confirm_timezone(update: Update, context: CallbackContext) -> int:
    chosen_timezone = update.message.text
    context.user_data['timezone'] = chosen_timezone
    current_date = datetime.now().strftime('%Y-%m-%d')
    context.user_data['last_update_date'] = current_date
    await update.message.reply_text(f'Your timezone is set to {chosen_timezone}.')
    return ConversationHandler.END


#timezone_handler = ConversationHandler(
    entry_points=[CommandHandler('timezone', set_timezone)],
    states={
        SET_TIMEZONE: [MessageHandler(filters.Text() & ~filters.Command(), confirm_timezone)]
    },
    fallbacks=[CommandHandler('stop', stop)]
)