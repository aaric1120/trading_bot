import requests as req


class TelegramBot:
    def __init__(self):
        self.token = "8176153946:AAE6kDdy3yR0InCvvCfByvpGUMDQBTgxPVg"
        self.chat_id = "7293486487"
        self.base_url = f"https://api.telegram.org/bot{self.token}/"

    def send_message(self, trade_type, symbol, action, price, qty, time):
        """
        Send message with given parameters on Telegram...
        :param trade_type:
        :param symbol:
        :param action:
        :param price:
        :param qty:
        :param time:
        :return:
        """
        message = (
            f"🚀 <b>{trade_type}</b> 🚀\n"
            f"Symbol: {symbol}\n"
            f"Action: {action}\n"
            f"Price: ${price}\n"
            f"Qty: {qty}\n"
            f"Time: {time}"
        )

        url = self.base_url + "sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = req.post(url, json=payload)
        return response.json()

# Initialize bot (replace with your credentials)
# bot = TelegramBot()
#
# bot.send_message("TEST TAKE PROFIT","NVDA","BUY",150.25,100,"dt.datetime.now()")