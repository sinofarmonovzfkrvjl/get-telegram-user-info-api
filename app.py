from quart import Quart, request, jsonify
from telethon import TelegramClient, errors
import asyncio
import time

# Telegram API ma'lumotlari
api_id = '808393'
api_hash = '052bb836544996dff795e6db0bee8614'
bot_token = '7146975082:AAEhfitmmvA-IPCbeR0W0hmRUZJK42evhag'

# Quart ilovasini yaratish
app = Quart(__name__)

# Telegram klienti uchun doimiy sessiya fayli
client = TelegramClient('session_name', api_id, api_hash)

# GET orqali username qabul qilib, ma'lumotni qaytarish funksiyasi
@app.route('/info', methods=['GET'])
async def get_info():
    username = request.args.get('user')
    if not username:
        return jsonify({'error': 'Username kiritilmadi'}), 400

    try:
        entity = await client.get_entity(username)
        info = {
            'ID': entity.id,
            'Name': f"{entity.first_name or ''} {entity.last_name or ''}".strip(),
            'Username': entity.username or 'Mavjud emas',
            'Phone': entity.phone or 'Mavjud emas',
            'Bot emasmi': not entity.bot,
        }
        return jsonify(info), 200

    except errors.FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        return jsonify({'error': f"FloodWait: Wait {e.seconds} seconds before retrying"}), 429
    except errors.RPCError as e:
        return jsonify({'error': f"Telegram xatosi: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Xatolik: {str(e)}"}), 500

# Telegram klientini ishga tushirish (FloodWaitError ga qarshi himoya)
async def start_client():
    global client
    while True:
        try:
            await client.start(bot_token=bot_token)
            print("Client started successfully.")
            break
        except errors.FloodWaitError as e:
            print(f"FloodWaitError: Waiting for {e.seconds} seconds before retrying.")
            await asyncio.sleep(e.seconds)

@app.before_serving
async def startup():
    await start_client()

@app.after_serving
async def shutdown():
    await client.disconnect()

# Asosiy serverni ishga tushirish
async def main():
    await app.run_task()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print(f"Runtime error occurred: {e}")
    except (KeyboardInterrupt, SystemExit):
        print("Dastur to'xtatildi.")
