import telebot
import openai
import requests
import os

# API Keys ඇතුළත් කරන්න
TELEGRAM_TOKEN = '8360915162:AAE4wFFgyJtwyDWJYJh8OmyzHrgdGJR1eNo'
OPENAI_API_KEY = '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'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # පරිශීලකයා එවූ caption එක පරීක්ෂා කිරීම
    caption = message.caption
    if caption and caption.startswith('/edit'):
        prompt = caption.replace('/edit', '').strip()
        
        if not prompt:
            bot.reply_to(message, "කරුණාකර රූපය වෙනස් විය යුතු ආකාරය සඳහන් කරන්න. (උදා: /edit add a car)")
            return

        sent_msg = bot.reply_to(message, "මදක් රැඳී සිටින්න, රූපය සකස් කරමින් පවතී...")

        try:
            # 1. පින්තූරය Download කරගැනීම
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            with open("image.png", "wb") as f:
                f.write(downloaded_file)

            # 2. OpenAI Edit API භාවිතා කිරීම
            # සටහන: OpenAI මගින් Image editing සඳහා රූපය PNG සහ 4MB ට අඩු විය යුතුය.
            response = openai.Image.create_edit(
                image=open("image.png", "rb"),
                prompt=prompt,
                n=1,
                size="1024x1024"
            )

            image_url = response['data'][0]['url']
            
            # 3. සකස් කළ පින්තූරය යැවීම
            bot.send_photo(message.chat.id, image_url, caption="මෙන්න ඔබ ඉල්ලූ වෙනස්කම!")
            bot.delete_message(message.chat.id, sent_msg.message_id)

        except Exception as e:
            bot.reply_to(message, f"දෝෂයක් සිදු විය: {str(e)}")
            if os.path.exists("image.png"):
                os.remove("image.png")
    else:
        bot.reply_to(message, "පින්තූරය සමඟ /edit සහ වෙනස් විය යුතු ආකාරය ලියා එවන්න.")

print("බොට් වැඩ කිරීමට සූදානම්...")
bot.infinity_polling()

