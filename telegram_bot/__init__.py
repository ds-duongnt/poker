import os

import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SOURCE_SHEET = os.getenv('SOURCE_SHEET')
REGISTER_NAME = os.getenv('REGISTER_NAME')
TELEGRAM_BANK_ID = [int(v) for v in os.getenv('TELEGRAM_BANK_ID').split(',')]

POKER_ONLINE_TOPIC = int(os.getenv('POKER_ONLINE_TOPIC'))
BOT_TOPIC = int(os.getenv('BOT_TOPIC'))
# NHOAE_TOPIC = int(os.getenv('NHOAE_TOPIC'))

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

from telegram_bot.filter import IsAdmin, IsBank, PlayerCallbackFilter
from telegram_bot.util import format_telegram_message, profit_convert
from telegram_bot.keyboard import player_list_keyboard
from telegram_bot.config import BACK, CANCEL, ALL, player_factory

bot.add_custom_filter(PlayerCallbackFilter())
bot.add_custom_filter(IsAdmin())
bot.add_custom_filter(IsBank())

# connect sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('./service_account.json', scope)
client = gspread.authorize(creds)

source_sheet = client.open_by_key('1y0TPHW5jaaWIOl5l1ITQI1XVsNVjxUikwS9LR3HFVOs')

# /hello
@bot.message_handler(commands=['hello'])
def hello(message):
    print(message)
    bot.send_message(message.chat.id, """Con đây ạ\!""", 'MarkdownV2', message_thread_id = message.message_thread_id)

# /apologize
@bot.message_handler(commands=['apologize'])
def apologize(message):
    bot.send_message(message.chat.id, """Con sai rồi ạ\!""", 'MarkdownV2', message_thread_id = message.message_thread_id)

# /miss
@bot.message_handler(is_admin=True, commands=['nho'])
def miss(message):
    if message.message_thread_id: 
        bot.send_message(message.chat.id, format_telegram_message('Sang topic > `Nhớ anh em`  sử dụng nhé ạ'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    # Get current list
    sheet = source_sheet.worksheet('Register')
    current_list = sheet.get_all_values()[1:]

    tag_list = [f"[{v[1] if v[-1] == '' else v[-1]}](tg://user?id={v[0]})" for v in current_list]
    tag_text = ' '.join(tag_list)
    
    bot.send_message(message.chat.id, text = f'Nhớ anh em {tag_text}', parse_mode = 'Markdown', message_thread_id = message.message_thread_id)
    return

# /register
@bot.message_handler(commands=['register'])
def register(message):
    if message.message_thread_id != POKER_ONLINE_TOPIC:
        bot.send_message(message.chat.id, format_telegram_message('Sang topic > `Poker Online` sử dụng nhé ạ'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    # Get current list
    sheet = source_sheet.worksheet('Register')
    current_list = sheet.get_all_values()
    id_list = [v[0] for v in current_list]
    # User requesting
    user =  message.from_user
    if str(user.id) in id_list:
        bot.send_message(message.chat.id, format_telegram_message('Đăng kí 1 lần thôi pa 😐'), 'MarkdownV2', message_thread_id = message.message_thread_id)
    else:
        data = [user.id, user.first_name, user.last_name, user.username]
        push = sheet.append_row(data)
        noti_text = push['updates']['updatedRange']
        bot.send_message(message.chat.id, format_telegram_message('Đăng kí thành công!'), 'MarkdownV2', message_thread_id = message.message_thread_id)

# /deposit /withdraw
@bot.message_handler(commands=['mua', 'ban'])
def request(message):
    # print(message)
    if message.message_thread_id != POKER_ONLINE_TOPIC:
        bot.send_message(message.chat.id, format_telegram_message('Sang topic > Poker Online sử dụng nhé ạ'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    eng_vn = {
        'mua': 'deposit',
        'ban': 'withdraw'
    }
    command = message.text
    content = command.split(' ')
    # Open topup sheet
    sheet = source_sheet.worksheet('Poker Online')

    ### player
    player_id = str(message.from_user.id)
    reg_sh = source_sheet.worksheet('Register')
    id_list = reg_sh.col_values(1)
    try:
        index = id_list.index(player_id)
        player = reg_sh.col_values(2)[index]
    except:
        bot.send_message(message.chat.id, format_telegram_message(f'Chưa đăng kí mà đã đòi chơi? Gõ lệnh /register đi nghen'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return 
    ### tx_id
    current = sheet.col_values(1)[-1]
    last_num = 0 if current == 'tx_id' else int(current)
    ### timestamp
    date = message.date
    date = datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M')
    ### category
    category = eng_vn[content[0][1:]]
    ### status
    status = f'=IF(H{last_num+2}=True,"COMPLETED",if(I{last_num+2}=True,"COMPLETED","PENDING"))'
    ### Chip
    try:
        chip = int(content[1])
    except:
        bot.send_message(message.chat.id, format_telegram_message('Sai cú pháp rồi! /mua {chip} cơ mà?'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    data = [last_num+1, date, category, status, player, chip] # [No, timestamp, category, status, player, chip]

    source_sheet.values_update(
        f'Poker Online!A{last_num+2}:F{last_num+2}',
        params= {
        'valueInputOption': 'USER_ENTERED'
        },
        body = {
            'values': [data]
        })
    bot_response = bot.send_message(message.chat.id, format_telegram_message(f'`[Request]` `{player}` {content[0][1:]} {chip}, @khangtt2 xác nhận txId này nhé: `({last_num+1})`'), 'MarkdownV2', message_thread_id = message.message_thread_id)
    bot.pin_chat_message(message.chat.id, message_id=bot_response.message_id)
    sheet.update_acell(f'J{last_num+2}', bot_response.message_id)
    return

# /admin
@bot.message_handler(is_admin=True, commands=['admin'])
def admin(message):
    if message.message_thread_id != POKER_ONLINE_TOPIC:
        bot.send_message(message.chat.id, format_telegram_message('Sang topic > Poker Online sử dụng nhé ạ'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    command = message.text
    content = command.split(' ')
    # Open topup sheet
    sheet = source_sheet.worksheet('Poker Online')

    # tx_id
    try:
        tx_id = int(content[1])
    except:
        bot.send_message(message.chat.id, format_telegram_message('Sai cú pháp rồi! /admin {tx_id} cơ mà?'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    id_list = sheet.col_values(1)[1:] # id
    id_list = [int(v) for v in id_list]
    if tx_id not in id_list:
        bot.send_message(message.chat.id, format_telegram_message(f'txId: {tx_id} not found!'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    index = id_list.index(tx_id)
    message_id = sheet.col_values(10)[1:][index] # message_id
    player = sheet.col_values(5)[1:][index] # player
    category = sheet.col_values(3)[1:][index] # category
    chip = sheet.col_values(6)[1:][index] # chip
    bank_tag = '[Janey](tg://user?id=6235420250)'
    vnd = int(chip)*100

    sheet.update_acell(f'G{tx_id+1}', True)
    # message_id = sheet.acell(f'J{tx_id+1}').value
    bot.send_message(message.chat.id, format_telegram_message(f'Admin > txId: {tx_id} thành công'), 'MarkdownV2', message_thread_id = message.message_thread_id)
    # bot.unpin_chat_message(message.chat.id, message_id= message_id)
    payment_text = f'`[Payment:({tx_id})]` `{player}` {"mua" if category == "deposit" else "bán"} {chip}, {bank_tag} {"thu tiền" if category == "deposit" else "trả tiền"} nhé: `{vnd:,.0f}đ`'
    bot.edit_message_text(chat_id=message.chat.id, message_id=message_id, text = payment_text, parse_mode = 'Markdown')
    return

# /payment
@bot.message_handler(is_bank=True, commands=['payment'])
def payment(message):
    if message.message_thread_id != POKER_ONLINE_TOPIC:
        bot.send_message(message.chat.id, format_telegram_message('Sang topic > Poker Online sử dụng nhé ạ'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    command = message.text
    content = command.split(' ')
    # Open topup sheet
    sheet = source_sheet.worksheet('Poker Online')

    # tx_id
    try:
        tx_id = int(content[1])
    except:
        bot.send_message(message.chat.id, format_telegram_message('Sai cú pháp rồi! /payment {tx_id} cơ mà?'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    id_list = sheet.col_values(1)[1:] # id
    id_list = [int(v) for v in id_list]
    if tx_id not in id_list:
        bot.send_message(message.chat.id, format_telegram_message(f'txId: {tx_id} not found!'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    index = id_list.index(tx_id)
    message_id = sheet.col_values(10)[1:][index] # message_id
    sheet.update_acell(f'H{tx_id+1}', True)

    bot.send_message(message.chat.id, format_telegram_message(f'Payment > txId: {tx_id} thành công'), 'MarkdownV2', message_thread_id = message.message_thread_id)
    bot.unpin_chat_message(message.chat.id, message_id= message_id)
    return

# /void
@bot.message_handler(is_admin=True, commands=['void'])
def payment(message):
    if message.message_thread_id != POKER_ONLINE_TOPIC:
        bot.send_message(message.chat.id, format_telegram_message('Sang topic > Poker Online sử dụng nhé ạ'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    command = message.text
    content = command.split(' ')
    # Open topup sheet
    sheet = source_sheet.worksheet('Poker Online')

    # tx_id
    try:
        tx_id = int(content[1])
    except:
        bot.send_message(message.chat.id, format_telegram_message('Sai cú pháp rồi! /void {tx_id} cơ mà?'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    id_list = sheet.col_values(1)[1:] # id
    id_list = [int(v) for v in id_list]
    if tx_id not in id_list:
        bot.send_message(message.chat.id, format_telegram_message(f'txId: {tx_id} not found!'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    index = id_list.index(tx_id)
    message_id = sheet.col_values(10)[1:][index] # message_id
    sheet.update_acell(f'I{tx_id+1}', True)

    bot.send_message(message.chat.id, format_telegram_message(f'Void > txId: {tx_id} thành công'), 'MarkdownV2', message_thread_id = message.message_thread_id)
    bot.unpin_chat_message(message.chat.id, message_id= message_id)
    return

# /record
@bot.message_handler(is_admin=True, commands=['record'])
def record(message):
    if message.message_thread_id: 
        bot.send_message(message.chat.id, format_telegram_message('Sang topic > `Nhớ anh em`  sử dụng nhé ạ'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    command = message.text
    content = command.split(' ')

    # tx_id
    try:
        src = ' '.join(content[1:])
        src_sh = source_sheet.worksheet(src)
    except:
        bot.send_message(message.chat.id, format_telegram_message('Sai cú pháp hoặc không tìm thấy sheet! /record {src} mà?'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    dest = src_sh.row_values(1)[1]
    dest_sh = source_sheet.worksheet(dest)
    try:
        col_push = dest_sh.row_values(2).index('') + 1
    except:
        bot.send_message(message.chat.id, format_telegram_message('Sheet hết chỗ trống, tạo thêm column đi nhé'), 'MarkdownV2', message_thread_id = message.message_thread_id)
        return
    
    data = src_sh.get_all_values()[2:]
    data = [profit_convert(v[3]) for v in data]
    
    for i, v in enumerate(data):
        dest_sh.update_cell(i+2, col_push, v)
    
    bot.send_message(message.chat.id, text = f'Record thành công!', parse_mode = 'Markdown', message_thread_id = message.message_thread_id)
    return
