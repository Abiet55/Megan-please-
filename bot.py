from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
import playwright.sync_api as sync

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a MEGA.nz file link and I will download it.")

def download_mega_file(mega_url):
    with sync.sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(mega_url)
        page.wait_for_selector('.download')
        download_link = page.query_selector('a.download').get_attribute('href')
        file_name = download_link.split('/')[-1]
        page.close()
        browser.close()
        return download_link, file_name

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    if "mega.nz" in message:
        await update.message.reply_text("Processing your MEGA link...")
        try:
            download_link, file_name = download_mega_file(message)
            # Download the file
            response = requests.get(download_link)
            with open(file_name, 'wb') as f:
                f.write(response.content)
            # Send the file
            await update.message.reply_document(open(file_name, 'rb'))
            os.remove(file_name)  # Clean up the downloaded file
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")
    else:
        await update.message.reply_text("Please send a valid MEGA.nz link.")

if __name__ == '__main__':
    import asyncio
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    asyncio.run(app.run_polling())