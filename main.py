import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from typing import Final

API_KEY = open('API_KEY').read()
SEARCH_ENGINE_ID = open('SEARCH_ENGINE_ID').read()

TOKEN: Final = open('TOKEN').read()
BOT_USERNAME: Final = '@CustomSearchAPI_bot'

url = 'https://www.googleapis.com/customsearch/v1'

params = {}

QUERY, COUNTRY, DATE, FILE, NUMBER, IMAGE, QUICK = range(7)





async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Hello {update.effective_user.first_name}, Let`s create a custom search!')


async def make_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text('Type your query')
    params['key'] = API_KEY
    params['cx'] = SEARCH_ENGINE_ID
    return QUERY


async def query(update: Update, context: ContextTypes.DEFAULT_TYPE):

    search_query = update.message.text
    print(f'Got query {search_query}')

    params['q'] = search_query
    print(params)

    await update.message.reply_text('Do you want to make a search in a specified country?\n'
                                    'If yes, type it in a countryUA format. If not, send /no')

    return COUNTRY

async def country(update: Update, context: ContextTypes.DEFAULT_TYPE):

    search_country = update.message.text
    print(f'Got country restriction {search_country}')

    params['cr'] = search_country
    print(params)

    await update.message.reply_text('Do you want to make a search in a specified anount of time?\n'
                                    'If yes, type it in a d[number] format (number of days) Use w instead of d for weeks,'
                                    'm for months and y for years. If not, send /no')

    return DATE

async def skip_country(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print(f'Got not country restriction')

    params['cr'] = ''
    print(params)

    await update.message.reply_text('Do you want to make a search in a specified anount of time?\n'
                                    'If yes, type it in a d[number] format (number of days) Use w instead of d for weeks,'
                                    'm for months and y for years. If not, send /no')

    return DATE

async def date(update: Update, context: ContextTypes.DEFAULT_TYPE):

    search_date = update.message.text
    print(f'Got date restriction {search_date}')

    params['dateRestrict'] = search_date
    print(params)

    await update.message.reply_text('Do you want to search for a specified file type?\n'
                                    'If yes, type it in a pdf/jpg/etc format. If not, send /no')

    return FILE

async def skip_date(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print('Got no date restriction')

    params['dateRestrict'] = ''
    print(params)

    await update.message.reply_text('Do you want to search for a specified file type?\n'
                                    'If yes, type it in a pdf pdf/jpg/etc format. If not, send /no')

    return FILE

async def file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    search_file = update.message.text
    print(f'Got file type {search_file}')

    params['fileType'] = search_file
    print(params)

    await update.message.reply_text('How many results (between 1 and 10) do you want to see?')

    return NUMBER

async def skip_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print('Got no file type')

    params['fileType'] = ''
    print(params)

    await update.message.reply_text('How many results (between 1 and 10) do you want to see?')

    return NUMBER

async def number(update: Update, context: ContextTypes.DEFAULT_TYPE):

    search_number = update.message.text
    print(f'Got number {search_number}')

    params['num'] = search_number
    print(params)

    await update.message.reply_text('Do you want a result to be an image? Send /yes or /no')

    return IMAGE

async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print('Got image')

    params['searchType'] = 'image'
    print(params)

    result = requests.get(url, params=params).json()['items']
    for item in result:
        await update.message.reply_text(item['link'])
    params.clear()

    return ConversationHandler.END

async def no_image(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print('Got no image')
    print(params)

    result = requests.get(url, params=params).json()['items']
    for item in result:
        await update.message.reply_text(item['link'])
    params.clear()

    return ConversationHandler.END





async def quick_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Type your query')
    params['key'] = API_KEY
    params['cx'] = SEARCH_ENGINE_ID

    return QUICK


async def image_search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text('Type your query')
    params['key'] = API_KEY
    params['cx'] = SEARCH_ENGINE_ID
    params['searchType'] = 'image'
    print(params)

    return QUICK

async def quick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_query = update.message.text
    print(f'Got query {search_query}')

    print(params)
    params['q'] = search_query
    print(params)

    result = requests.get(url, params=params).json()['items']
    await update.message.reply_text(result[0]['link'])
    params.clear()

    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Such a shame!')
    return ConversationHandler.END


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')





if __name__ == '__main__':
    print('Starting bot...')
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("hello", hello))

    conv_handler = ConversationHandler (
        entry_points=[CommandHandler("make_custom_search", make_search), CommandHandler("quick_search", quick_search), CommandHandler("quick_image_search", image_search)],
        states={
            QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, query)],
            COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, country), CommandHandler("no", skip_country)],
            DATE: [MessageHandler(filters.Regex("(d|w|m|y)\[(\d+)\]"), date), CommandHandler("no", skip_date)],
            FILE: [MessageHandler(filters.Regex("(\w+)"), file), CommandHandler("no", skip_file)],
            NUMBER: [MessageHandler(filters.Regex("^[1-9]|10$"), number)],
            IMAGE: [CommandHandler("yes", image), CommandHandler("no", no_image)],
            QUICK: [MessageHandler(filters.TEXT & ~filters.COMMAND, quick)],
        },
        fallbacks = [MessageHandler(filters.Regex("^Done$"), handle_message)],
    )

    app.add_handler(conv_handler)

    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)