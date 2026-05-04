import os
from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler, Event
# from linebot.v3.exceptions import InvalidSignatureError  (這裡你原本有重複引入，我幫你留下面 v2 版本的即可)
# from linebot.v3.messaging.models import TextMessage
from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    MessageEvent, 
    TextMessage, 
    TextSendMessage,
    ImageSendMessage,
    FlexSendMessage  # 👈 新增這行：引入 Flex 訊息模組
)
from linebot.exceptions import InvalidSignatureError
import logging

# 加載 .env 文件中的變數
load_dotenv()

# 從環境變數中讀取 LINE 的 Channel Access Token 和 Channel Secret
line_token = os.getenv('LINE_TOKEN')
line_secret = os.getenv('LINE_SECRET')

# 檢查是否設置了環境變數
if not line_token or not line_secret:
    print(f"LINE_TOKEN: {line_token}")  # 調試輸出
    print(f"LINE_SECRET: {line_secret}")  # 調試輸出
    raise ValueError("LINE_TOKEN 或 LINE_SECRET 未設置")

# 初始化 LineBotApi 和 WebhookHandler
line_bot_api = LineBotApi(line_token)
handler = WebhookHandler(line_secret)

# 創建 Flask 應用
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# 設置一個路由來處理 LINE Webhook 的回調請求
@app.route("/", methods=['POST'])
def callback():
    # 取得 X-Line-Signature 標頭
    signature = request.headers['X-Line-Signature']

    # 取得請求的原始內容
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # 驗證簽名並處理請求
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 設置一個事件處理器來處理 TextMessage 事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: Event):
    if event.message.type == "text":
        user_message = event.message.text  # 使用者的訊息
        app.logger.info(f"收到的訊息: {user_message}")

        # 👈 這裡開始是修改的地方：判斷使用者是不是輸入「選單」
        if user_message == "選單":
            # 這是我們剛剛在模擬器做好的網格版 JSON
            flex_json = {
              "type": "bubble",
              "size": "mega",
              "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "text",
                    "text": "我撿到的種類",
                    "weight": "bold",
                    "size": "xl",
                    "align": "center",
                    "margin": "md"
                  },
                  {
                    "type": "text",
                    "text": "請選擇你的狀況",
                    "size": "md",
                    "color": "#888888",
                    "align": "center",
                    "margin": "md"
                  },
                  {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "margin": "xl",
                    "contents": [
                      {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "md",
                        "contents": [
                          {"type": "button", "style": "secondary", "action": {"type": "message", "label": "電子產品", "text": "電子產品"}},
                          {"type": "button", "style": "secondary", "action": {"type": "message", "label": "衣服", "text": "衣服"}}
                        ]
                      },
                      {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "md",
                        "contents": [
                          {"type": "button", "style": "secondary", "action": {"type": "message", "label": "鞋子", "text": "鞋子"}},
                          {"type": "button", "style": "secondary", "action": {"type": "message", "label": "證件", "text": "證件"}}
                        ]
                      },
                      {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "md",
                        "contents": [
                          {"type": "button", "style": "secondary", "action": {"type": "message", "label": "錢包", "text": "錢包"}},
                          {"type": "button", "style": "secondary", "action": {"type": "message", "label": "雨傘", "text": "雨傘"}}
                        ]
                      },
                      {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "md",
                        "contents": [
                          {"type": "button", "style": "secondary", "action": {"type": "message", "label": "書籍", "text": "書籍"}},
                          {"type": "button", "style": "secondary", "action": {"type": "message", "label": "其他", "text": "其他"}}
                        ]
                      },
                      {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                          {"type": "button", "style": "secondary", "action": {"type": "message", "label": "配飾 (耳環、項鍊、手鏈)", "text": "配飾"}}
                        ]
                      }
                    ]
                  }
                ]
              }
            }

            # 建立 FlexSendMessage 物件並回傳
            flex_message = FlexSendMessage(
                alt_text="失物招領選單",
                contents=flex_json
            )
            line_bot_api.reply_message(
                event.reply_token,
                flex_message
            )

        else:
            # 如果輸入其他內容，就維持原本的 Echo 功能
            reply_text = ("你說了：" + user_message)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )

# 應用程序入口點
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
