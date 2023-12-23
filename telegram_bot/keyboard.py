from telegram_bot.config import CANCEL, BACK, ALL, player_factory
from telebot import types

def player_list_keyboard(data, cancel=True, back=False, All=True):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    if back:
        keyboard.add(
            types.InlineKeyboardButton(
                text='⬅',
                callback_data = player_factory.new(player_id=BACK))
        )

    keyboard.add(*[
        types.InlineKeyboardButton(
            text=player[1],
            callback_data=player_factory.new(player_id=player[0])
        )
    for player in data]) # player [_id, _name]

    # print(len(keyboard.keyboard))

    if len(keyboard.keyboard) > 1 and All:
        keyboard.add(
            types.InlineKeyboardButton(
                text='All',
                callback_data = player_factory.new(player_id=ALL))
        )

    if cancel:
        keyboard.add(
            types.InlineKeyboardButton(
                text='Cancel',
                callback_data = player_factory.new(player_id=CANCEL))
        )

    return keyboard

