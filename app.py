from quart import Quart, request, jsonify
from telethon import TelegramClient, errors
import asyncio

# Telegram API uchun kerakli ma'lumotlar
api_id = '808393'
api_hash = '052bb836544996dff795e6db0bee8614'
bot_token = '7146975082:AAEhfitmmvA-IPCbeR0W0hmRUZJK42evhag'  # Bot tokenini bu yerga qo'shing

# Quart ilovasini ishga tushiramiz
app = Quart(__name__)

# Telegram klientini yaratish
client = None

# GET orqali username qabul qilib, ma'lumotni qaytarish funksiyasi
@app.route('/info', methods=['GET'])
async def get_info():
    username = request.args.get('user')  # URL dan username ni olish

    if not username:
        return jsonify({'error': 'Username kiritilmadi'}), 400

    try:
        # Foydalanuvchi haqida ma'lumot olish
        entity = await client.get_entity(username)
        info = {
            'ID': entity.id,
            'Name': f"{entity.first_name or ''} {entity.last_name or ''}".strip(),
            'Username': entity.username or 'Mavjud emas',
            'Phone': entity.phone or 'Mavjud emas',
            'Bot emasmi': not entity.bot,
        }
        return jsonify(info), 200

    except errors.RPCError as e:
        return jsonify({'error': f"Telegram xatosi: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Xatolik: {str(e)}"}), 500

# Telegram klientini ishga tushirish va Quart serverini boshlash
async def main():
    global client
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start(bot_token=bot_token)  # Telegram clientni ishga tushiramiz
    await app.run_task()  # Quart serverini ishga tushiramiz (async)

# Cleanup function to close the Telegram client properly
@app.before_serving
async def startup():
    global client
    await client.start(bot_token=bot_token)

@app.after_serving
async def shutdown():
    global client
    await client.disconnect()

if __name__ == '__main__':
    try:
        asyncio.run(main())  # Asosiy event loop orqali kodni ishga tushirish
    except RuntimeError as e:
        print(f"Runtime error occurred: {e}")
    except (KeyboardInterrupt, SystemExit):
        print("Dastur to'xtatildi.")
