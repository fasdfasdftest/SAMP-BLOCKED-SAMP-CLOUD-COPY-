import telebot
import psutil
import os
import random
from telebot import types
import psutil
import subprocess
import threading
import time
from telebot.apihelper import ApiTelegramException
import schedule
from datetime import datetime, timedelta
import sys
import string
from PIL import Image, ImageDraw, ImageFont
from samp_client.client import SampClient

bot_token = "7444964455:AAFUr6km1Y8SP-VIsaKmgdfjdNEarvfghd2ZVc"
bot = telebot.TeleBot(bot_token)

admin_ids = [123123123]
black_list = ["127.0.0.1", "0.0.0.0"]
data_file = 'user_data.txt'
promo_codes = {}
user_last_click = {}
cooldown_seconds = 15
test = 0
test2 = 0 

agreement_text = """
Пользовательское соглашение

Прежде чем начать использовать бота, пожалуйста, внимательно прочитайте данное соглашение.

1. Общие положения

Данное Пользовательское соглашение (далее – Соглашение) устанавливает правила взаимодействия между владельцем Telegram-бота (далее – Бот) и пользователем Интернета (далее – Пользователь), который использует Бот.

2. Предмет Соглашения

Бот предоставляет Пользователю доступ к функционалу, связанному с [возможностью блокировки доступа определенному игроку на сервер].

3. Отказ от ответственности

3.1. Администрация Бота не отвечает за сбои в функционировании Бота, вызванные техническими проблемами, а также за временную недоступность Бота по причинам, находящимся вне зоны ответственности Администрации.
3.2. Администрация Бота не несет ответственности за любые прямые или косвенные потери, возникшие вследствие использования Бота или невозможности его использования.

4. Принятие условий Соглашения

Использование Бота означает, что Пользователь ознакомился с условиями настоящего Соглашения и полностью с ними согласен.

5. Изменения в Соглашении

Администрация Бота имеет право вносить изменения в настоящее Соглашение без предварительного уведомления Пользователей.
"""

def is_ip_allowed(ip):
    return ip not in black_list

def generate_captcha():
    length = random.randint(3, 5)
    captcha_text = ''.join(random.choices(string.ascii_lowercase, k=length))
    
    img_width = int(100 * 1.3)
    img_height = int(50 * 1.3)
    img = Image.new('RGB', (img_width, img_height), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", int(36 * 1.3))
    
    for i, char in enumerate(captcha_text):
        d.text((10 + i * 20, 5), char, fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), font=font)
    
    for _ in range(2):
        d.line([(random.randint(0, img_width // 2), random.randint(0, img_height // 2)), 
                (random.randint(img_width // 2, img_width), random.randint(0, img_height // 2))], 
               fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), width=2)
    
    d.line([(0, img_height // 2), (img_width, img_height // 2)], 
           fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), width=2)
    
    img.save('captcha.png')
    return captcha_text

def count_proxies():
    with open('Proxy.txt', 'r') as file:
        return len(file.readlines())

def send_proxies(user_id):
    with open('Proxy.txt', 'r') as file:
        proxies = file.read()
        bot.send_message(user_id, proxies)

def send_lua_scripts(user_id):
    for script_file in os.listdir('scripts'):
        if script_file.endswith('.lua'):
            with open(os.path.join('scripts', script_file), 'r') as file:
                script_content = file.read()
                chunks = [script_content[i:i+4000] for i in range(0, len(script_content), 4000)]
                for i, chunk in enumerate(chunks):
                    bot.send_message(user_id, f"Content of {script_file} (Part {i+1}/{len(chunks)}):\n\n{chunk}")

def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)
def stop_user_bots(user_id):
    user_bots = get_bots_by_user(user_id)
    for bot in user_bots:
        terminate_bot(bot)

def send_regular_notification():
    keyboard = types.InlineKeyboardMarkup()
    bot_button = types.InlineKeyboardButton(text="🤖 Перейти к боту", url="https://t.me/sampblocked_bot")
    keyboard.add(bot_button)

    for user_id in user_info:
        try:
            chat = bot.get_chat(user_id)
            if chat.type in ['group', 'supergroup']:
                bot.send_message(user_id, "ℹ Регулярное уведомление: Если у вас возникли проблемы или баги, рекомендую зайти в бота напрямую а не использовать его в группе/супер группе.", reply_markup=keyboard)
        except ApiTelegramException:
            continue

schedule.every(45).minutes.do(send_regular_notification)


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_scheduler).start()


def stop_all_bots(user_id):
    try:
        user_info[user_id]['active_bots'] = 0
        save_user_data(user_info)
        time.sleep(2)
        bot.send_message(user_id, "⛔ Информация: Все боты были завершены одним из администраторов по технической причине.")

        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == "RakSAMPLite.exe":
                proc.terminate()
                print(f"Terminated process {proc.info['name']} with PID {proc.info['pid']}")

    except ApiTelegramException as e:
        if e.error_code == 403:
            print(f"Cannot send message to user {user_id}: bot was blocked by the user.")
            pass
        else:
            print(f"An unexpected error occurred: {e}")

def broadcast_message(user_id, text):
    try:
        bot.send_message(user_id, text)
    except ApiTelegramException as e:
        if e.error_code == 403:
            print(f"User {user_id} has blocked the bot.")
            pass
        else:
            print(f"Failed to send message to {user_id}: {e}")


def save_user_data(user_info):
    with open(data_file, 'w') as file:
        for user_id, data in user_info.items():
            file.write(f"{user_id},{data['balance']},{data['tag']},{data['registration_date']},{data['status']},{data.get('ip', '')},{data.get('port', '')},{data.get('nickname', '')},{data['max_bots']},{data['last_bonus']},{data['active_bots']}\n")

def load_user_data():
    if not os.path.exists(data_file):
        return {}
    
    user_info = {}
    with open(data_file, 'r') as file:
        for line in file:
            line = line.strip()
            parts = line.split(',')
            if len(parts) == 11:
                user_id, balance, tag, registration_date, status, ip, port, nickname, max_bots, last_bonus, active_bots = parts
                user_info[int(user_id)] = {
                    'balance': int(balance),
                    'tag': tag,
                    'registration_date': registration_date,
                    'status': status,
                    'ip': ip,
                    'port': port,
                    'nickname': nickname,
                    'max_bots': int(max_bots),
                    'last_bonus': last_bonus,
                    'active_bots': int(active_bots)
                }
            else:
                print(f"Ошибка в строке: {line}. Недостаточно данных.")
    return user_info

user_info = load_user_data()
print(user_info)

user_info = load_user_data()

user_counter = len(user_info)



def send_startup_message(user_id):
    with open("welcome.png", "rb") as image: #welcome.png
        time.sleep(2)
        bot.send_photo(user_id, image, caption="🤖 Бот успешно запущен и готов к работе! В случае проблем перезапустите бота коммандой /start либо обратитесь к администрации.")

def get_system_stats():
    cpu_usage = psutil.cpu_percent(interval=1)
    
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent
    
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_recv = net_io.bytes_recv
    
    stats = (
        f"💻 Системная статистика:\n"
        f"🔋 Загруженность процессора: {cpu_usage}%\n"
        f"🧠 Использование озу: {memory_usage}%\n"
        f"💾 Использование диска: {disk_usage}%\n"
        f"🌐 Сетевой трафик:\n"
        f"   📤 Отправлено: {bytes_sent} байт\n"
        f"   📥 Получено: {bytes_recv} байт\n"
    )
    return stats

@bot.message_handler(commands=['start'])
def start(message):
    if test == 1:
        if message.chat.id not in admin_ids:
            bot.send_message(message.chat.id, "⛔ Бот временно недоступен из-за технических работ. Приносим извинения за неудобства.")
            return

    chat_type = message.chat.type
    
    if chat_type == 'private':
        captcha_text = generate_captcha()
        with open('captcha.png', 'rb') as captcha_image:
            bot.send_photo(message.chat.id, captcha_image, caption="Пожалуйста, введите капчу с изображения.")
        bot.register_next_step_handler(message, lambda msg: check_captcha(msg, captcha_text))
    else:
        show_menu(message)

def check_captcha(message, captcha_text):
    if message.text.lower() == captcha_text:
        bot.send_message(message.chat.id, "Капча верна! Теперь вы можете продолжить.")
        show_menu(message)
    else:
        bot.send_message(message.chat.id, "Неверная капча. Попробуйте снова.")
        start(message)

def show_menu(message):
    global user_counter
    user_id = message.chat.id
    chat_type = message.chat.type

    if user_id not in user_info:
        if chat_type == 'group' or chat_type == 'supergroup':
            initial_balance = 0
        else:
            initial_balance = 120

        user_info[user_id] = {
            'balance': initial_balance,
            'tag': f'user_{user_id}',
            'registration_date': datetime.now().strftime("%Y-%m-%d"),
            'status': 'Пользователь',
            'ip': '',
            'port': '',
            'nickname': '',
            'max_bots': 1,
            'last_bonus': '',
            'active_bots': 0
        }
        save_user_data(user_info)
        user_counter += 1
        notify_admin_about_new_user(user_id)

    send_startup_message(user_id)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text="ℹ️ Информация", callback_data="info"),
        types.InlineKeyboardButton(text="📊 Просмотреть нагрузку на систему", callback_data="stats"),
    )
    keyboard.add(
        types.InlineKeyboardButton(text="📈 Пользовательское соглашение", callback_data="testing"),
        types.InlineKeyboardButton(text="📈 Количество прокси", callback_data="count_proxies"),
    )
    keyboard.add(
        types.InlineKeyboardButton(text="🔌 Запустить сессию", callback_data="connect"),
     #   types.InlineKeyboardButton(text="📞 Связь с администрацией", callback_data="contact_admin")
    )
    keyboard.add(
        types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        types.InlineKeyboardButton(text="🏆 Топ 100 пользователей по балансу", callback_data="leaderboard"),
    #    types.InlineKeyboardButton(text="🎟️ Активировать промокод", callback_data="activate_promo"),
    )
    if chat_type == 'private':
        keyboard.add(
        types.InlineKeyboardButton(text="🎁 Бонус", callback_data="get_minute"),
        types.InlineKeyboardButton(text="📞 Связь с администрацией", callback_data="contact_admin"),
        types.InlineKeyboardButton(text="🎟️ Активировать промокод", callback_data="activate_promo")
    )


    keyboard.add(
        types.InlineKeyboardButton(text="📈 Общее количество пользователей", callback_data="total_users"),
    )

    if user_id in admin_ids:
        keyboard.add(
            types.InlineKeyboardButton(text="📧 Разсылка", callback_data="broadcast"),
            types.InlineKeyboardButton(text="💸 Пополнить всем баланс", callback_data="add_balance_all"),
            types.InlineKeyboardButton(text="💸 Пополнить баланс пользователю", callback_data="add_balance_user"),
            types.InlineKeyboardButton(text="🚫 Заблокировать пользователя", callback_data="block_user"),
            types.InlineKeyboardButton(text="🛠️ Создать промокод", callback_data="create_promo"),
            types.InlineKeyboardButton(text="📧 Ответы на вопросы", callback_data="admin_responses"),
            types.InlineKeyboardButton(text="🔄 Изменить лимит ботов", callback_data="change_max_bots"),
            types.InlineKeyboardButton(text="❌ Закрыть все сессии", callback_data="stop_all_bots"),
            types.InlineKeyboardButton(text="🛠 Перезагрузить бота", callback_data="restart_bot"),
            types.InlineKeyboardButton(text="📧 Просмотреть скрипты", callback_data="view_scripts"),
        )

    bot.send_message(user_id, "Выберите действие:", reply_markup=keyboard)
    
user_last_log_time = {}
user_last_click = {}
log_cooldown_seconds = 15

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global user_last_log_time
    global user_last_click

    user_id = call.message.chat.id
    user_name = call.from_user.username
    current_time = datetime.now()
    
    last_log_time = user_last_log_time.get(call.from_user.id)
    
    if last_log_time:
        elapsed_time = (current_time - last_log_time).total_seconds()
        if elapsed_time < log_cooldown_seconds:
            remaining_time = log_cooldown_seconds - elapsed_time
            print(f"Пользователь {user_name} (ID: {call.from_user.id}) пытался логировать слишком часто.")
            try:
                bot.answer_callback_query(call.id, f"⏰ Подождите еще {int(remaining_time)} секунд перед следующим действием.", show_alert=True)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка при ответе на запрос: {e}")
            return

    user_last_log_time[call.from_user.id] = current_time

    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[BOT LOG] Date: [{timestamp}] Пользователь: {user_name} ID: {call.from_user.id} в чате ID: {user_id} нажал на кнопку."
    print(log_message)

    if call.message.chat.type in ['group', 'supergroup']:
        bot.send_message(user_id, log_message)
        
    user_last_click[user_id] = current_time

    if call.data == "info":
        bot.send_message(user_id, "ℹ️ Этот бот создан для блокировки возможности играть другим людям. Используйте команды и кнопки для выполнения различных действий.\n\n"
                          "💬 Перед тем как установить бота убедитесь что человек находится в offline и сервер не полон иначе могут возникнуть проблемы с подключением и да, при желании вы можете добавить данного бота с свою группу 🔥\n\n"
                          "🔥 Обновление по тарифам и услугам 🔥\n\n"
                          "💬 Если вы хотите активировать префикс в боте, стоимость составляет 15 рублей.\n\n"
                          "💬 Так-же если вы хотите добавить айпи в black list, стоимость составляет 850 рублей.\n\n"
                          "⏳ Для пользователей, желающих продлить сессию, 120 минут обойдутся в 20 рублей.\n\n"
                          "💬 Так-же если вы хотите купить рекламу, стоимость составляет 500 рублей.\n\n"
                          "🔓 Хотите добавить получить дополнительный слот? Это будет стоить 80 рублей.\n\n"
                          "❗ Важно: Для получения дополнительной информации и общения с другими пользователями, присоединяйтесь к нашему общему чату: none [BANNED GROUP]")
    elif call.data == "stats":
        bot.send_message(user_id, "📊 Загрузка данных...")
        stats = get_system_stats()
        bot.send_message(user_id, stats)
    elif call.data == "contact_admin":
        bot.send_message(user_id, "📞 Отправьте свой вопрос, и он будет передан администратору.")
        bot.register_next_step_handler(call.message, forward_question_to_admin)
    if test == 1:
        bot.send_message(call.message.chat.id, "⛔ Бот временно недоступен из-за технических работ. Приносим извинения за неудобства.")
        return
    elif call.data == "stop_all_bots":
        stop_all_bots(user_id)
    if call.data == "count_proxies":
        bot.send_message(user_id, f"Общее количество прокси: {count_proxies()}")
    elif call.data == "view_proxies":
        send_proxies(user_id)
    elif call.data == "view_scripts":
        send_lua_scripts(user_id)
    elif call.data == "restart_bot":
        bot.send_message(user_id, "Перезагрузка бота...")
        restart_bot()
    elif call.data == "connect":
        if user_info[user_id]['active_bots'] < user_info[user_id]['max_bots']:
            command = "/addbot Sam_Mason 127.0.0.1 7777 15"
            bot.send_message(user_id, f"<b>Введите команду в формате:</b> <code>{command}</code>\n\n"
                                      "<b>где:</b>\n"
                                      "<b>Sam_Mason</b> - ник\n"
                                      "<b>127.0.0.1</b> - IP-адрес\n"
                                      "<b>7777</b> - порт\n"
                                      "<b>15</b> - количество минут.",
                             parse_mode="HTML")
           # bot.register_next_step_handler(call.message, ask_for_time)
        else:
            bot.send_message(user_id, "❌ Вы достигли лимита на одновременное подключение ботов.")
    elif call.data == "profile":
        user_data = user_info.get(user_id)
        profile_info = (
            f"👤 Ваш профиль:\n"
            f"💰 Баланс: {user_data['balance']} минут\n"
            f"🏷️ Тэг: {user_data['tag']}\n"
            f"📅 Дата регистрации: {user_data['registration_date']}\n"
            f"⚙️ Статус: {user_data['status']}\n"
            f"🆔 Ваш ID: {user_id}\n"
            f"👤 Текущие боты: {user_data['nickname']}\n"
            f"🔄 Лимит ботов: {user_data['max_bots']}\n"
        )
        bot.send_message(user_id, profile_info)
    elif call.data == "leaderboard":
            leaderboard = generate_leaderboard(user_info, user_id)
            bot.send_message(user_id, leaderboard)
    if call.data == "testing":
           bot.send_message(call.message.chat.id, agreement_text)
    elif call.data == "broadcast":
        if user_id in admin_ids:
            bot.send_message(user_id, "📧 Введите сообщение для рассылки.")
            bot.register_next_step_handler(call.message, broadcast_message)
    elif call.data == "add_balance_all":
        if user_id in admin_ids:
            bot.send_message(user_id, "💸 Введите сумму для пополнения всем пользователям.")
            bot.register_next_step_handler(call.message, add_balance_all_users)
    elif call.data == "add_balance_user":
        if user_id in admin_ids:
            bot.send_message(user_id, "💸 Введите ID пользователя и сумму для пополнения в формате: ID сумма.")
            bot.register_next_step_handler(call.message, add_balance_user)
    elif call.data == "block_user":
        if user_id in admin_ids:
            bot.send_message(user_id, "🚫 Введите ID пользователя для блокировки.")
            bot.register_next_step_handler(call.message, block_user)
    elif call.data == "create_promo":
        if user_id in admin_ids:
            bot.send_message(user_id, "🛠️ Введите промокод и количество минут в формате: промокод минуты.")
            bot.register_next_step_handler(call.message, create_promo)
    elif call.data == "activate_promo":
        bot.send_message(user_id, "🎟️ Введите промокод для активации.")
        bot.register_next_step_handler(call.message, activate_promo)
    elif call.data == "admin_responses":
        if user_id in admin_ids:
            bot.send_message(user_id, "📧 Введите ID вопроса и ответ в формате: ID ответ.")
            bot.register_next_step_handler(call.message, admin_responses)
    elif call.data == "stop_all_bots":
        if user_id in admin_ids:
           stop_all_bots()
           bot.send_message(user_id, "✅ Все боты были завершены.")
    elif call.data == "total_users":
            bot.send_message(user_id, f"Общее количество пользователей: {user_counter}")
    elif call.data == "change_max_bots":
        if user_id in admin_ids:
            bot.send_message(user_id, "🔄 Введите ID пользователя и новый лимит ботов в формате: ID лимит.")
            bot.register_next_step_handler(call.message, change_max_bots)
    elif call.data == "get_minute":
        print("Кнопка нажата")
        chat_type = bot.get_chat(call.message.chat.id).type
        print(f"Тип чата: {chat_type}")
        
        if chat_type == 'private':
            user_id = call.from_user.id
            last_bonus_date = user_info.get(user_id, {}).get('last_bonus', None)
            today_date = datetime.now().strftime("%Y-%m-%d")

            if last_bonus_date != today_date:
                user_info.setdefault(user_id, {})['balance'] += 15
                user_info[user_id]['last_bonus'] = today_date
                save_user_data(user_info)

                try:
                    bot.send_message(user_id, "🎁 Вы получили 15 минут!")
                except Exception as e:
                    print(f"Ошибка при отправке сообщения: {e}")
            else:
                try:
                    bot.send_message(user_id, "⏰ Вы уже получали бонус сегодня. Попробуйте завтра.")
                except Exception as e:
                    print(f"Ошибка при отправке сообщения: {e}")
        else:
            bot.answer_callback_query(call.id, "⛔ Эта кнопка доступна только в личных сообщениях.", show_alert=True)

            
def generate_leaderboard(user_info, current_user_id):
    sorted_users = sorted(user_info.items(), key=lambda x: x[1]['balance'], reverse=True)
    leaderboard = "🏆 Топ 100 пользователей по балансу:\n\n"
    
    for i, (user_id, data) in enumerate(sorted_users[:100]):
        leaderboard += f"{i+1}. 🆔 {data['tag']} - 💰 {data['balance']} минут\n"
    
    for i, (user_id, data) in enumerate(sorted_users):
        if user_id == current_user_id:
            if i >= 10:
                leaderboard += "\n🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆\n"
                leaderboard += f"(Вы) - {i+1}. 🆔 {data['tag']} - 💰 {data['balance']} минут"
                leaderboard += "\n🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆\n"
            break
    
    return leaderboard


def stop_user_bots():
    for user_id, user_data in user_info.items():
        if user_data.get('active_bots', 0) > 0:
            for proc in psutil.process_iter():
                if proc.name() == "RakSAMPLite.exe":
                    proc.terminate()

            user_data['active_bots'] = 0
            bot.send_message(user_id, "⛔ Информация: Все боты были завершены одним из администраторов по технической причине.")
    
    save_user_data(user_info)
    time.sleep(5)



def get_server_info(ip, port):
    try:
        with SampClient(address=ip, port=port) as client:
            info = client.get_server_info()
        return info
    except Exception as e:
        print(f"Ошибка при запросе к серверу: {e}")
        return None

def create_bot(user_id, nickname, ip, port, time_minutes):
    if not is_ip_allowed(ip):
        bot.send_message(user_id, "⛔ Этот IP-адрес заблокирован администратором.")
        return

    user_data = user_info[user_id]

    if user_data['balance'] < time_minutes:
        time.sleep(5)
        bot.send_message(user_id, "⏳ У вас недостаточно минут на балансе. Пополните баланс или получите ежедневный бонус.")
        return

    if user_data['active_bots'] >= user_data['max_bots']:
        time.sleep(5)
        bot.send_message(user_id, "❌ Вы достигли лимита на количество активных ботов.")
        return

    server_info = get_server_info(ip, port)
    if not server_info:
        bot.send_message(user_id, "⚠️ Возможно, сервер выключен или наш IP находится в бане. Попробуйте подключить бота к другому серверу или повторите попытку позже.")
        return

    user_data['balance'] -= time_minutes
    save_user_data(user_info)

    if time_minutes >= 60 and random.random() <= 0.5:
        cashback_amount = int(time_minutes * 0.05)
        user_info[user_id]['balance'] += cashback_amount
        save_user_data(user_info)
        bot.send_message(user_id, f"🎉 Сегодня вам повезло, и вы получили кешбек в виде {cashback_amount} минут!")

    user_data['active_bots'] += 1
    save_user_data(user_info)

    bot_command = ["RakSAMPLite.exe", "-h", ip, "-p", str(port), "-n", nickname, "-z"]

    bot_process = subprocess.Popen(bot_command)

    time.sleep(2)
    bot.send_message(user_id, f"🤖 Бот {nickname} успешно запущен. Сервер: {ip}:{port} сессия будет длится {time_minutes} минут!")

    server_message = f"📊 Сервер: {server_info.hostname}\nРежим: {server_info.gamemode}\nОнлайн: {server_info.players}/{server_info.max_players}"
    if hasattr(server_info, 'ping'):
        server_message += f"\nПинг: {server_info.ping}"

    bot.send_message(user_id, server_message)

    time.sleep(20)
    bot.send_message(user_id, f"📢 - Если бот {nickname} не подключился, пожалуйста, предоставьте доказательства администрации. Возможно, вам будут возвращены минуты.")

    for admin_id in admin_ids:
        bot.send_message(admin_id, f"📢 Пользователь {user_id} запустил бота с ником {nickname} на {time_minutes} минут {ip}:{port}.")

    def stop_bot():
        bot_process.terminate()
        bot.send_message(user_id, f"⏰ Время истекло! Бот {nickname} был отключен от {ip}:{port}.")
        
        user_data['active_bots'] -= 1
        save_user_data(user_info)

    timer = threading.Timer(time_minutes * 60, stop_bot)
    timer.start()

#def ask_for_time(message):
#    user_id = message.chat.id
#    try:
#        data = message.text.split()
#        if len(data) != 5:
 #           raise ValueError("Неверный формат команды")
 #       nickname, ip, port, time_minutes = data[1:]
#       create_bot(user_id, nickname, ip, port, int(time_minutes))
#    except ValueError:
#        bot.send_message(user_id, "❌ Неверный формат команды. Попробуйте снова. (Не забудьте нажать кнопку подключить бота снова!)")
        
def forward_question_to_admin(message):
    user_id = message.chat.id
    question = message.text
    for admin_id in admin_ids:
        bot.send_message(admin_id, f"❓ Вопрос от пользователя {user_id}: {question}")
    bot.send_message(user_id, "✅ Ваш вопрос отправлен администратору. Ожидайте ответа.")

def notify_admin_about_new_user(user_id):
    for admin_id in admin_ids:
        bot.send_message(admin_id, f"📢 Новый пользователь зарегистрирован: ID: {user_id}")


def broadcast_message(message):
    if message.chat.id in admin_ids:
        admin_note = " 📢 Рассылка от одного из администраторов:\n\n\n "
        text = admin_note + message.text
        for user_id in user_info.keys():
            try:
                bot.send_message(user_id, text)
            except telebot.apihelper.ApiTelegramException as e:
                if e.error_code == 403:
                    print(f"User {user_id} blocked the bot, skipping. [РАЗЗСЫЛКА]")
                else:
                    raise e



def add_balance_all_users(message):
    try:
        amount = int(message.text)
        for user_id in user_info.keys():
            user_info[user_id]['balance'] += amount
        save_user_data(user_info)
        bot.send_message(message.chat.id, f"💸 Баланс всех пользователей пополнен на {amount} минут.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат суммы. Попробуйте снова.")

def add_balance_user(message):
    try:
        user_id, amount = message.text.split()
        user_id = int(user_id)
        amount = int(amount)
        if user_id in user_info:
            user_info[user_id]['balance'] += amount
            save_user_data(user_info)
            bot.send_message(message.chat.id, f"💸 Баланс пользователя {user_id} пополнен на {amount} минут.")
        else:
            bot.send_message(message.chat.id, "❌ Пользователь с таким ID не найден.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат ввода. Попробуйте снова.")

def block_user(message):
    try:
        user_id = int(message.text)
        if user_id in user_info:
            user_info[user_id]['status'] = 'заблокирован'
            save_user_data(user_info)
            bot.send_message(message.chat.id, f"🚫 Пользователь {user_id} заблокирован.")
        else:
            bot.send_message(message.chat.id, "❌ Пользователь с таким ID не найден.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат ввода. Попробуйте снова.")

def create_promo(message):
    try:
        promo_code, minutes = message.text.split()
        minutes = int(minutes)
        promo_codes[promo_code] = minutes
        bot.send_message(message.chat.id, f"🛠️ Промокод {promo_code} создан и даёт {minutes} минут.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат ввода. Попробуйте снова.")

def activate_promo(message):
    user_id = message.chat.id
    promo_code = message.text
    if promo_code in promo_codes:
        minutes = promo_codes[promo_code]
        user_info[user_id]['balance'] += minutes
        save_user_data(user_info)
        bot.send_message(user_id, f"🎉 Промокод {promo_code} активирован! Ваш баланс пополнен на {minutes} минут.")
        del promo_codes[promo_code]
    else:
        bot.send_message(user_id, "❌ Неверный промокод. Попробуйте снова.")


def admin_responses(message):
    try:
        print(f"Received message: {message.text}")
        
        question_id, response = message.text.split(maxsplit=1)
        question_id = int(question_id)
        
        if question_id not in user_info:
            bot.send_message(message.chat.id, "❌ Пользователь с таким ID не найден.")
            return
        
        bot.send_message(question_id, f"📧 Сообщение от администратора: {response}")
        bot.send_message(message.chat.id, "✅ Ответ отправлен пользователю.")
    except ValueError as e:
        print(f"Error: {e}")
        bot.send_message(message.chat.id, "❌ Неверный формат ввода. Попробуйте снова.")


def change_max_bots(message):
    try:
        user_id, new_limit = message.text.split()
        user_id = int(user_id)
        new_limit = int(new_limit)
        if user_id in user_info:
            user_info[user_id]['max_bots'] = new_limit
            save_user_data(user_info)
            bot.send_message(message.chat.id, f"🔄 Лимит ботов пользователя {user_id} изменён на {new_limit}.")
        else:
            bot.send_message(message.chat.id, "❌ Пользователь с таким ID не найден.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат ввода. Попробуйте снова.")

def start_bot():
    bot.polling(none_stop=True)

def reset_bots_and_notify_users():
    for user_id, data in user_info.items():
        data['active_bots'] = 0
        try:
           # bot.send_message(user_id, "🤖 Телеграм бот был перезапущен автоматически иза возникновения ошибки. Пожалуйста, введите команду /start для начала работы.")
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == "RakSAMPLite.exe":
                   proc.terminate()
        except telebot.apihelper.ApiTelegramException as e:
            if 'chat not found' in e.result_json.get('description', '').lower():
                print(f"Chat with user ID {user_id} not found. Skipping...")
            else:
                print(f"Error sending message to user {user_id}: {e}")
    save_user_data(user_info)


def send_message_safe(user_id, message):
    try:
        bot.send_message(user_id, message)
    except telebot.apihelper.ApiTelegramException as e:
        if e.result_json['description'] == 'Forbidden: bot was blocked by the user' or \
           e.result_json['description'] == 'Forbidden: bot was kicked from the supergroup chat':
            print(f"User with ID {user_id} has blocked or kicked the bot. Skipping...")
        else:
            raise

reset_bots_and_notify_users()

@bot.message_handler(commands=['addbot'])
def add_bot_command(message):
    if test2 == 1 and message.chat.type != 'private':
        bot.send_message(message.chat.id, "<b>⛔ Эта команда доступна только в личных сообщениях.</b>", parse_mode='HTML')
        return

    try:
        data = message.text.split()
        
        if len(data) < 4 or len(data) > 5:
            raise ValueError("❌ <b>Неверный формат команды. Используйте:</b>\n"
                             "<code>/addbot &lt;ник&gt; &lt;IP:порт&gt; &lt;время в минутах&gt;</code> \n"
                             "<b>или</b>\n"
                             "<code>/addbot &lt;IP&gt; &lt;порт&gt; &lt;время в минутах&gt;</code>")

        nickname = data[1]
        
        if ':' in data[2]:
            ip, port = data[2].split(':')
            time_minutes = int(data[3])
        else:
            ip = data[2]
            port = data[3]
            time_minutes = int(data[4])

        create_bot(message.chat.id, nickname, ip, port, time_minutes)
    except ValueError as e:
        bot.send_message(message.chat.id, str(e), parse_mode='HTML')

def start_bot():
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20, long_polling_timeout=40)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(15)

def restart_bot():
    print("Перезапуск бота...")
    sys.exit(1)

def schedule_restart():
    schedule.every(1).hours.do(restart_bot)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0, timeout=20, long_polling_timeout=40)
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()
