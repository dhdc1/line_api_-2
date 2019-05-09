# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import errno
import os
import sys
import tempfile

from flask import Flask, request, abort, send_from_directory, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)

import requests
import json
import mysql.connector

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)

api_reply = "https://api.line.me/v2/bot/message/reply"
api_push = "https://api.line.me/v2/bot/message/multicast"

# เปลี่ยนเป็นของ chanel ตัวเอง
channel_secret = "fb0fed31522e4da273fd1856ef6489a9"
channel_access_token = "IEl91F7L1MnAuHDD3kxAYgF27xXSQJW41LpAoLMf0RjuuXNBjuN5E2uhYRHPyqcUKjRSgdwWconYrYivZLmyk/ECjXV+pNwjgQQoji+ZNs1wtUwwzkz3xMOjqbabRexZUCt2vbadhK7UwZkxBs9R+gdB04t89/1O/w1cDnyilFU="

if channel_secret is None:
    print('LINE_CHANNEL_SECRET is None.')
    sys.exit(1)
if channel_access_token is None:
    print('LINE_CHANNEL_ACCESS_TOKEN is None')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')


# function

def is_member(event):
    user_id = event.source.user_id    
    if not user_id  == '00000':       
        return False
    else :
        return True

def liff_regis(event):
    line_message_reply(event,[
        {
            "type": "template",
            "altText": "this is a buttons template",
            "template": {
                "type": "buttons",
                "actions": [
                    {
                        "type": "uri",
                        "label": ">> คลิก <<",
                        "uri": "line://app/1572556016-pjGyJe9Y"
                    }
                ],
                "title": "ลงทะเบียน",
                "text": "หากไม่ลงทะเบียนจะไม่ตอบอะไรเลย"
            }
        }
    ])




def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise


def con_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="112233",
        database="his",
        port=3306
    )
    return db


def get_user_profile(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    return profile


def line_message_reply(event, messages):
    payload = {
        'replyToken': event.reply_token,
        "messages": messages
    }
    headers = {
        'Authorization': 'Bearer {0}'.format(channel_access_token),
        'Content-Type': 'application/json'
    }
    r = requests.post(api_reply, data=json.dumps(payload), headers=headers)
    print(r)


def line_message_push(to, messages):
    payload = {
        'to': to,
        'messages': messages
    }

    headers = {
        'Authorization': 'Bearer {0}'.format(channel_access_token),
        'Content-Type': 'application/json'
    }
    r = requests.post(api_push, data=json.dumps(payload), headers=headers)
    print(r)


# url-routing
@app.route('/regis', methods=['GET', 'POST'])
def regis():
    if request.method == 'GET':
        return render_template('regis.html')
    if request.method == 'POST':
        cid = request.form['cid']
        print(cid)
        print('xxx')
        return render_template('ok.html')


@app.route('/push', methods=['GET'])
def push():
    line_message_push(['lineid','dd',''], [
        {
            "type": "text",
            "text": "ข้อความเสียโควต้า message "
        }
    ])
    return 'OK'


# end-routing


# webhook
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    print(body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(FollowEvent)  # มีคนมา add , มีคน unblock
def handle_follow(event):
    print(event)

    if not is_member(event):
        liff_regis(event)
    else:
        profile = get_user_profile(event)
        line_bot_api.reply_message(event.reply_token,[
            
            #process data query in 30 sec
            TextSendMessage(text='สวัสดีจ้า...' + profile.display_name ),
            TextSendMessage(text='ให้ช่วยอะไรจ๊ะ...'),
            TextSendMessage(text='บอกมาได้เลย....')
        ])


@handler.add(UnfollowEvent) #มีคน block
def handle_unfollow(event):
    print(event)


@handler.add(MessageEvent, message=TextMessage) # มีคนส่งข้อความแบบ text มาหา bot
def handle_text_message(event):
    #print(event)
    text = event.message.text
    if not is_member(event):
        liff_regis(event)
    else:

        if text == 'test':
            line_message_reply(event,[           
                {
                'type':'text',
                'text':'ยินดีที่เป็นเพื่อนกัน...'  
                }
            ])

        if text == 'จองคิว':
            line_message_reply(event,[
                {
                'type':'text',
                'text':'ได้เลยจ้า'  
                }
            ])

        if text == 'ดีๆ':
            msg1 =  {
                "type": "sticker",
                "packageId": "1",
                "stickerId": "102"
            }
            msg2 =  {
                "type": "sticker",
                "packageId": "3",
                "stickerId": "191"
            }
            line_message_reply(event,[
                msg1,
                msg2,
                {
                'type':'text',
                'text':'ก็ดีเหมือนกันนะ...'  
                }
            ])

        if text == 'ที่ไหน':
            addr = "แถวนี้น่าอยู่..."
            loc =  {
                "type": "location",
                "title": "ที่นี่แหละ",
                "address": addr,
                "latitude": 16,
                "longitude": 100
            }
            line_message_reply(event,[
                loc,
                {
                    'type':'text',
                    'text':'ก็มาดิ....'
                }
            ])

        if text == 'confirm':
            msg = {
                "type": "template",
                "altText": "this is a confirm template",
                "template": {
                    "type": "confirm",
                    "actions": [
                        {
                            "type": "postback",
                            "label": "อืม",
                            "text": "yes",
                            "data": "data1"
                        },
                        {
                            "type": "uri",
                            "label": "ไม่",
                            "uri": "line://nv/camera/"
                        }
                    ],
                    "text": "มาจริงปะละ?"
                }
            }
            line_message_reply(event,[
                msg
            ])




@handler.add(MessageEvent, message=StickerMessage)  #มีคนส่งสติกเกอร์
def handle_sticker_message(event):
    print(event)
    line_message_reply(event,[
        {
            "type": "sticker",
            "packageId": event.message.package_id,
            "stickerId": event.message.sticker_id
        }
    ])



@handler.add(MessageEvent, message=LocationMessage) #มีคนส่ง location
def handle_location_message(event):
    print(event)
    lat, lon ,user_id = event.message.latitude, event.message.longitude , event.source.user_id
    profile = get_user_profile(event)
    user_name = profile.display_name
    line_message_reply(event,[
        {
            'type':'text',
            'text': user_name+" , "+str(lat) +" , "+  str(lon) 
        }
    ])
    



@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage)) #ส่ง multimedia
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    url = request.url_root + 'static/tmp/' + dist_name
    print(url)


@handler.add(MessageEvent, message=FileMessage) #ส่งไฟล์
def handle_file_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='file-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '-' + event.message.file_name
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)
    url = request.host_url + '/static/tmp/' + dist_name
    print(url)


@handler.add(JoinEvent)  # bot เข้ากลุ่ม
def handle_join(event):
    print(event)


@handler.add(LeaveEvent) # bot ออกจากกลุ่ม 
def handle_leave(event):
    print(event)


@handler.add(PostbackEvent)  # ข้อความส่งมาแบบเบื้องหลัง
def handle_postback(event):
    print(event)


@handler.add(BeaconEvent)  # เข้าไปในพื้นที่ beacon
def handle_beacon(event):
    print(event)


@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # create tmp dir for download content
    make_static_tmp_dir()

    app.run(debug=True, port=8000)
