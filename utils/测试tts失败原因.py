# -*- coding: utf-8 -*-
#  语音合成 WebAPI 接口调用示例 接口文档（必看）：https://doc.xfyun.cn/msc_android/%E8%AF%AD%E9%9F%B3%E5%90%88%E6%88%90.html
#  webapi 合成服务参考帖子：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=38997&extra=
#  webapi是单次只支持1000个字节，具体看您的编码格式，计算一下具体支持多少文字
# （Very Important）创建完webapi应用添加合成服务之后一定要设置ip白名单，找到控制台--我的应用--设置ip白名单，如何设置参考：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=41891
#  合成发音人自动添加获取测试权限使用方法：登陆开放平台https://www.xfyun.cn/后--我的应用（必须为webapi类型应用）--添加在线语音合成（已添加的不用添加）--发音人管理---添加发音人--测试代码里需修改发音人参数
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
#  @author iflytek
import requests
import time
import hashlib
import base64
import re
import os
import json
#  合成webapi接口地址
URL = "http://api.xfyun.cn/v1/service/v1/tts"
#  音频编码(raw合成的音频格式pcm、wav,lame合成的音频格式MP3)
AUE = "raw"
#  应用APPID（必须为webapi类型应用，并开通语音合成服务，参考帖子如何创建一个webapi应用：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=36481
APPID = "5c8bb395"
#  接口密钥（webapi类型应用开通合成服务后，控制台--我的应用---语音合成---相应服务的apikey）
API_KEY = "9ebe9c5cbb1a67bb2ab0608640078d83"


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

# 组装http请求头


def getHeader():
    curTime = str(int(time.time()))
    # ttp=ssml
    param = "{\"aue\":\"" + AUE + "\",\"auf\":\"audio/L16;rate=16000\",\"voice_name\":\"xiaoyan\",\"engine_type\":\"intp65\"}"
    # print("param:{}".format(param))

    paramBase64 = str(base64.b64encode(param.encode('utf-8')), 'utf-8')
    # print("x_param:{}".format(paramBase64))

    m2 = hashlib.md5()
    m2.update((API_KEY + curTime + paramBase64).encode('utf-8'))

    checkSum = m2.hexdigest()
    # print('checkSum:{}'.format(checkSum))

    header = {
        'X-CurTime': curTime,
        'X-Param': paramBase64,
        'X-Appid': APPID,
        'X-CheckSum': checkSum,
        'X-Real-Ip': '127.0.0.1',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }
    # print(header)
    return header


def getBody(text):
    data = {'text': text}
    return data


def writeFile(file, content):
    with open(file, 'wb') as f:
        f.write(content)
    f.close()


def test_fail_reason(txt_file_path):
    # txt_file_path = r"C:\Dpan\python-script\pdf_convert\数据\10人以下小团队管理手册-堀之内克彦_image_ocr_result.txt"
    #  待合成文本内容
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        text = f.read().replace('\n', "")
    # print('总字数：',len(text))
    # text_length = 333
    # text_list = re.findall(r".{%d}" % text_length, text)
    # text_list.append(text[len(text_list) * text_length:])
    text_list = text_byte_num_cut(text, 998)
    # print('分段数：',len(text_list))
    try:
        folder_path = os.path.join(r"E:\python\python-post-tencent\讯飞AI\audio", os.path.splitext(os.path.basename(txt_file_path))[0])
        os.makedirs(folder_path)
    except:
        pass

    for i, every_text in enumerate(text_list):
        r = requests.post(URL, headers=getHeader(), data=getBody(every_text))

        contentType = r.headers['Content-Type']
        if contentType == "audio/mpeg":
            sid = r.headers['sid']
            if AUE == "raw":
                #   合成音频格式为pcm、wav并保存在audio目录下
                writeFile(os.path.join(folder_path, '{}.wav'.format(i)), r.content)
                # writeFile( + str(i) + ".wav", r.content)
            else:
                #   合成音频格式为mp3并保存在audio目录下
                writeFile("audio/" + "xiaoyan" + ".mp3", r.content)
            print(i,"success, sid = " + sid)
        else:
            #   错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
            for i in json.loads(r.content).items():
                print(' => '.join(i))

if __name__ == "__main__":
    test_fail_reason(r"C:\Dpan\python-script\pdf_convert\数据\10人以下小团队管理手册-堀之内克彦_image_ocr_result.txt")