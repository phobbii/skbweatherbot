
import time


class Messages(object):

    def __init__(self, auth, sleep_timer):
        self.bot = auth
        self.sleep_timer = sleep_timer

    def __repeat_send_msg(self, chat_id, answer, **kwargs):
        while True:
            try:
                self.bot.send_message(chat_id, answer, **kwargs)
                return True
            except:
                time.sleep(self.sleep_timer)

    def __repeat_send_sticker(self, chat_id, answer, **kwargs):
        while True:
            try:
                self.bot.send_sticker(chat_id, answer, **kwargs)
                return True
            except:
                time.sleep(self.sleep_timer)

    def __repeat_reply_to(self, chat_id, answer, **kwargs):
        while True:
            try:
                self.bot.reply_to(chat_id, answer, **kwargs)
                return True
            except:
                time.sleep(self.sleep_timer)

    def send_action(self, chat_id, action):
        while True:
            try:
                self.bot.send_chat_action(chat_id, action)
                return True
            except:
                time.sleep(self.sleep_timer)

    def send_msg(self, chat_id, answer, **kwargs):
        kwargs_list=[i for i in kwargs.keys()]
        if 'reply_markup' in kwargs_list and 'parse_mode' in kwargs_list:
            self.__repeat_send_msg(chat_id, answer, reply_markup=kwargs['reply_markup'], 
                                   parse_mode=kwargs['parse_mode'])
        elif 'reply_markup' in kwargs_list:
            self.__repeat_send_msg(chat_id, answer, reply_markup=kwargs['reply_markup'])
        else:
            self.__repeat_send_msg(chat_id, answer)

    def send_sticker(self, chat_id, answer, **kwargs):
        kwargs_list=[i for i in kwargs.keys()]
        if 'reply_to_message_id' in kwargs_list and 'reply_markup' in kwargs_list:
            self.__repeat_send_sticker(chat_id, answer, reply_to_message_id=kwargs['reply_to_message_id'], 
                                       reply_markup=kwargs['reply_markup'])
        else:
            self.__repeat_send_sticker(chat_id, answer)

    def reply_to(self, chat_id, answer, **kwargs):
        kwargs_list=[i for i in kwargs.keys()]
        if 'reply_markup' in kwargs_list and 'parse_mode' in kwargs_list:
            self.__repeat_reply_to(chat_id, answer, reply_markup=kwargs['reply_markup'], 
                                   parse_mode=kwargs['parse_mode'])
        elif 'reply_markup' in kwargs_list:
            self.__repeat_reply_to(chat_id, answer, reply_markup=kwargs['reply_markup'])
        else:
            self.__repeat_reply_to(chat_id, answer)