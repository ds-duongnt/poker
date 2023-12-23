import telebot
from telebot import types
from telebot.callback_data import CallbackDataFilter
from bot import bot

from telegram_bot import TELEGRAM_BANK_ID

class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_admin'
    @staticmethod
    def check(message: telebot.types.Message):
        return bot.get_chat_member(message.chat.id,message.from_user.id).status in ['administrator','creator']
    
class IsBank(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_bank'
    @staticmethod
    def check(message: telebot.types.Message):
        return message.from_user.id in TELEGRAM_BANK_ID

class PlayerCallbackFilter(telebot.AdvancedCustomFilter):
    key = 'player_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)