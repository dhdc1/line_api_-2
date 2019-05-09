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
channel_secret = "d2d9f8b67a4837db81ced2cb47651a4f"
channel_access_token = "ya/3TTMl4IK706X8nqW3A+6qXzRwWwet0LJdplhFtncpNC04cuUL3t25wGPdM9qsggUyQ0Y+H0xu+IpvVCDs2cMm15/A0rPTkiYDwH0vxXpoVnxbImierkix9zeybtxdSgbS4jZEpBCs2ZVLTCPhhwdB04t89/1O/w1cDnyilFU="

if channel_secret is None:
    print('LINE_CHANNEL_SECRET is None.')
    sys.exit(1)
if channel_access_token is None:
    print('LINE_CHANNEL_ACCESS_TOKEN is None')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')


# test

def test_app():
    db = con_db()
    cursor = db.cursor()
    sql = "select concat(count(vn) ,' ' ,'visit') as cc  from vn_stat where vstdate ='2018-09-03'"
    cursor.execute(sql)
    row = cursor.fetchone()
    msg = row[0]
    print(msg)


# function
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
        host="203.157.118.123",
        user="sa",
        passwd="qazwsxedcr112233",
        database="hos",
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
    line_message_push(['Ude27617017e3cbf820dd9aa13b1491ca'], [
        {
            "type": "text",
            "text": "ข้อความเสียสตางค์"
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


@handler.add(FollowEvent)
def handle_follow(event):
    print(event)


@handler.add(UnfollowEvent)
def handle_unfollow(event):
    print(event)


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    print(event)
    text = event.message.text


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    print(event)


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    print(event)


@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
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


@handler.add(MessageEvent, message=FileMessage)
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


@handler.add(JoinEvent)
def handle_join(event):
    print(event)


@handler.add(LeaveEvent)
def handle_leave(event):
    print(event)


@handler.add(PostbackEvent)
def handle_postback(event):
    print(event)


@handler.add(BeaconEvent)
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

    test_app()

    app.run(debug=True, port=8000)
