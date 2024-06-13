import logging
from app.inference import response
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters


# настроим модуль ведения журнала логов
logging.basicConfig(
    filename="bot.log",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filemode='w'
)


logger = logging.getLogger("bot")


async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Добрый день! Какая информация о пользовании банковской картой вас интересует?")


async def clear(update, context):
    context.bot.callback_data_cache.clear_callback_data()
    context.bot.callback_data_cache.clear_callback_queries()
    await update.effective_message.reply_text("Все чисто!")


#async def query(update, context):
#    res = response(update.message.text)
#    await context.bot.send_message(chat_id=update.effective_chat.id, text=res)


if __name__ == '__main__':
    TOKEN = '.........................'
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    clear_handler = CommandHandler('clear', clear)
#    query_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), query)

    application.add_handler(start_handler)
    application.add_handler(clear_handler)
#    application.add_handler(query_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
