from telebot.callback_data import CallbackData

CANCEL = 'x'
BACK = 'back'
ALL = 'all'

player_factory = CallbackData('player_id', prefix='player')