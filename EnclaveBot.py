
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, Application, CallbackQueryHandler
import logging
import re

token = ""

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO, filename="log.txt"
)
logger = logging.getLogger(__name__)

async def hello(update, context) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}!")

async def enclave(update, context) -> None:
    await update.message.reply_text("На месте.")

async def alarm(context) -> None:
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"{job.data} секунд прошло!")

def remove_job_if_exists(name: str, context) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_timer(update, context) -> None:
    chat_id = update.effective_message.chat_id
    due = float(update.message.text[7:])
    if due < 0:
        await update.effective_message.reply_text("Жаль, что мы не можем вернуться в прошлое!")
        return
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)
    text = "Таймер установлен!"
    if job_removed:
        text += " (Старый удалён)"
    await update.effective_message.reply_text(text)

async def unset(update, context) -> None:
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Таймер остановлен!" if job_removed else "Таймер не найден."
    await update.message.reply_text(text)

async def echo(update, context) -> None:
    text = update.message.text[8:]
    await update.message.reply_text(text)

async def start(update, context) -> None:
    keyboard = [
        [InlineKeyboardButton("Команда 1", callback_data='command1')],
        [InlineKeyboardButton("Команда 2", callback_data='command2')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Доступные команды: \n.привет \n.анклав \n.повтори <сообщение> \n+/-таймер <секунды>')
    await update.message.reply_text('Выберите команду:', reply_markup=reply_markup)

async def button_click(update, context) -> None:
    query = update.callback_query
    command = query.data
    if command == 'command1':
        await context.bot.send_message(chat_id=query.message.chat_id, text='Вы выбрали команду 1')
    elif command == 'command2':
        await context.bot.send_message(chat_id=query.message.chat_id, text='Вы выбрали команду 2')

if __name__ == '__main__':
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Regex(re.compile(r'^[\/\.]привет$', re.IGNORECASE)), hello))
    application.add_handler(MessageHandler(filters.Regex(re.compile(r'^[\/\.]?анклав$', re.IGNORECASE)), enclave))
    application.add_handler(MessageHandler(filters.Regex(re.compile(r'^[\/\.]повтори\s', re.IGNORECASE)), echo))
    application.add_handler(MessageHandler(filters.Regex(re.compile(r'^[\/\+]таймер\s', re.IGNORECASE)), set_timer))
    application.add_handler(MessageHandler(filters.Regex(re.compile(r'^[\/\-]таймер$', re.IGNORECASE)), unset))
    application.add_handler(CallbackQueryHandler(button_click))
    application.run_polling(1.0)