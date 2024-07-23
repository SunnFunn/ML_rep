import logging
from app.inference import response
from telegram import Bot, BotCommand, Chat, MenuButtonCommands, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# настроим модуль ведения журнала логов
logging.basicConfig(
    filename="bot.log",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filemode='w'
)


logger = logging.getLogger("bot")


INTRO, BUTTON, RESPONSE, END = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c1 = BotCommand(command='start', description='Начать диалог')
    c2 = BotCommand(command='cancel', description='Завершить диалог')
    await bot.set_my_commands(commands=[c1, c2])
    await bot.set_chat_menu_button()
    await update.message.reply_text(text="Здравствуйте, как я могу к вам обращаться? Введите, пожалуйста, ваше имя в строке чата.")

    return INTRO


async def introduction (update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    user_name = update.message.text
    context.user_data['user_name'] = user_name
    logger.info("User of %s: %s", user.first_name, user_name)

    keyboard = [[InlineKeyboardButton("Посмотрите, чем я могу вам помочь", callback_data="1")],
                [InlineKeyboardButton("Задайте вопрос", callback_data="2")],
                [InlineKeyboardButton("Завершить диалог", callback_data="3")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text=f"{user_name}, хотя вы сразу можете задать мне вопрос, рекомендую вам на первом шаге взглянуть на перечень информации, в которой я могу помочь разобраться.",
                                    reply_markup=reply_markup
                                    )
    return BUTTON


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = context.user_data['user_name']
    query = update.callback_query

    if query.data == '1':
        await query.answer()

        await query.message.reply_text(text=f"{user_name}, подождите, идет загрузка информационного ролика...")
        video = open('./app/context_source/Introduction.mp4', 'rb')

        await query.bot.send_video(chat_id=update.effective_chat.id,
                                   video=video,
                                   caption='Рекомендую посмотреть, так будет больше пользы от нашего диалога.')
        return BUTTON

    elif query.data == '2':
        await query.answer()
        await query.message.reply_text(text=f"{user_name}, напишите что вас интересует...")
        return RESPONSE

    elif query.data == '3':
        await query.answer()
        logger.info("User %s canceled the conversation.", user_name)
        await query.message.reply_text(
        "До встречи! Надеюсь общение со мной было полезным для вас."
        )
        return ConversationHandler.END


#async def repeat(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    await update.message.reply_text(text=f"{user_name}, чем еще я могу вам помочь?")

#    return INTRO


async def query(update, context):
    user_name = context.user_data['user_name']
    res = response(update.message.text)
    keyboard = [[InlineKeyboardButton("Задайте новый вопрос", callback_data="2")],
                [InlineKeyboardButton("Завершить диалог", callback_data="3")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text=f"{user_name}, подождите, ищу нужную информацию...")
    await update.message.reply_text(text=res,
                                    reply_markup=reply_markup)

    return BUTTON


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "До встречи! Надеюсь общение со мной было полезным для вас. Если остались вопросы, можете возобновить диалог в menu."
    )

    return ConversationHandler.END


if __name__ == '__main__':
    TOKEN = '........................................'
    application = ApplicationBuilder().token(TOKEN).build()
    bot = Bot(TOKEN)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            INTRO: [MessageHandler(filters.TEXT & (~filters.COMMAND), introduction)],
            BUTTON: [CallbackQueryHandler(button)],
            RESPONSE: [MessageHandler(filters.TEXT & (~filters.COMMAND), query)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
