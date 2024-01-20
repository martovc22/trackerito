# Timezone 
async def set_time_zone(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text
    current_date = datetime.now().date()
    if user_choice == 'UK':
        context.user_data['time_zone'] = UK_TIME_ZONE
        context.user_data['time_zone_date'] = current_date
    elif user_choice == 'CZ':
        context.user_data['time_zone'] = CZ_TIME_ZONE
        context.user_data['time_zone_date'] = current_date
    else:
        await update.message.reply_text('Invalid selection. Please choose again.')
        return TIME_ZONE
    await update.message.reply_text('Time zone set successfully.')
    return ConversationHandler.END

def is_time_zone_set_for_today(context: CallbackContext) -> bool:
    current_date = datetime.now().date()
    return ('time_zone' in context.user_data and 
            'time_zone_date' in context.user_data and 
            context.user_data['time_zone_date'] == current_date)


# Timezone selection 
async def set_time_zone(update: Update, context: CallbackContext) -> int:
    user_choice = update.message.text
    current_date = datetime.now().date()
    if user_choice == 'UK':
        context.user_data['time_zone'] = UK_TIME_ZONE
        context.user_data['time_zone_date'] = current_date
    elif user_choice == 'CZ':
        context.user_data['time_zone'] = CZ_TIME_ZONE
        context.user_data['time_zone_date'] = current_date
    else:
        await update.message.reply_text('Invalid selection. Please choose again.')
        return TIME_ZONE

    await update.message.reply_text(f"Time zone set successfully to {context.user_data['time_zone']}.")
    return ConversationHandler.END

# wrapper function decorator!
def timezone_check(func):
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        if not is_time_zone_set_for_today(context):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please set your time zone first using /set_time_zone"
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper