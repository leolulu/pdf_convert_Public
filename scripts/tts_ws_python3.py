# -*- coding:utf-8 -*-
#
#   author: iflytek
#
#  本demo测试时运行的环境为：Windows + Python3.7
#  本demo测试成功运行时所安装的第三方库及其版本如下：
#   cffi==1.12.3
#   gevent==1.4.0
#   greenlet==0.4.15
#   pycparser==2.19
#   six==1.12.0
#   websocket==0.2.1
#   websocket-client==0.56.0
#
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os
import traceback
from tqdm import tqdm
import wave
from .audio_convert import pcm2wav
from utils.crypt import decrypt_express
from constants.common import CommonConstants


STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8"}
        # print(self.Text)
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url


def text_byte_num_cut(text, byte_limit):
    split_text_list = []
    single_text = ''
    for char_ in text:
        if len((single_text+char_).encode('utf-8')) >= byte_limit:
            split_text_list.append(single_text)
            single_text = ''
        single_text += char_
    split_text_list.append(single_text)
    return split_text_list


def run_tts(Text, serial_no, input_file_path):
    audio_name_prefix = os.path.basename(os.path.dirname(input_file_path))
    audio_output_path = os.path.join(os.path.dirname(input_file_path), '{}_audio'.format(audio_name_prefix))

    if os.path.exists(os.path.join(audio_output_path, '{}-{}.wav'.format(audio_name_prefix, serial_no))):
        return

    try:
        os.mkdir(audio_output_path)
    except:
        pass

    txt_path = os.path.join(audio_output_path, '{}-{}.txt'.format(audio_name_prefix, serial_no))
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(Text)

    def on_message(ws, message):
        pcm_path = os.path.join(audio_output_path, '{}-{}.pcm'.format(audio_name_prefix, serial_no))
        # wav_path = os.path.join(audio_output_path, '{}-{}.wav'.format(audio_name_prefix, serial_no))
        try:
            message = json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            if status == 2:
                print("ws is closed")
                ws.close()
            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                with open(pcm_path, 'ab') as f:
                    f.write(audio)
        except Exception as e:
            print("receive msg,but parse exception:", e)
            print(traceback.format_exc())

    def on_error(ws, error):
        print("### error:", error)

    def on_close(ws):
        print("### closed ###")

    def on_open(ws):
        def run(*args):
            d = {"common": wsParam.CommonArgs,
                 "business": wsParam.BusinessArgs,
                 "data": wsParam.Data,
                 }
            d = json.dumps(d)
            # print("------>开始发送文本数据")
            ws.send(d)
            # if os.path.exists('./demo.pcm'):
            #     os.remove('./demo.pcm')

        thread.start_new_thread(run, ())

    wsParam = Ws_Param(
        APPID=decrypt_express(os.getenv(CommonConstants.PW), CommonConstants.TTS_APPID),
        APIKey=decrypt_express(os.getenv(CommonConstants.PW), CommonConstants.TTS_APIKEY),
        APISecret=decrypt_express(os.getenv(CommonConstants.PW), CommonConstants.TTS_APISECRET),
        Text=Text
    )
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    for pcm_file in [os.path.join(audio_output_path, i) for i in os.listdir(audio_output_path) if os.path.splitext(i)[-1] == '.pcm']:
        pcm2wav(pcm_file)
        os.remove(pcm_file)


def tts_run_total(txt_file_path):
    #  待合成文本内容
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        text = f.read().replace('\n', "")
    print('总字数：', len(text))
    text_list = text_byte_num_cut(text, 7998)
    print('分段数：', len(text_list))

    for i, text in enumerate(tqdm(text_list), start=1):
        i = str(i).zfill(3)
        run_tts(text, i, txt_file_path)

    return os.path.join(os.path.dirname(txt_file_path), '{}_audio'.format(os.path.basename(os.path.dirname(txt_file_path))))


if __name__ == "__main__":
    tts_run_total(r"E:\python\pdf_convert\数据\精要主义 如何应对拥挤不堪的工作与生活\精要主义 如何应对拥挤不堪的工作与生活 _image_ocr_result.txt")
