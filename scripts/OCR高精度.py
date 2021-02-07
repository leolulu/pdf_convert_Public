from constants.common import CommonConstants
from utils.utils import requests_with_retry
from utils.crypt import decrypt_express
import json
import base64
import os
import time
from tqdm import tqdm


class OCRError:
    def __init__(self, code=None):
        self.code = code


class GenerateUrl:
    URL = None
    CLIENT_ID = decrypt_express(os.getenv(CommonConstants.PW), CommonConstants.OCR_CLIENT_ID)
    CLIENT_SECRET = decrypt_express(os.getenv(CommonConstants.PW), CommonConstants.OCR_CLIENT_SECRET)
    HOST = CommonConstants.OCR_AUTH_URL.format(CLIENT_ID, CLIENT_SECRET)

    @classmethod
    def get_url(cls):
        if not GenerateUrl.URL:
            GenerateUrl.URL = CommonConstants.OCR_ENDPOINT + json.loads(requests_with_retry(GenerateUrl.HOST).content)[CommonConstants.ACCESS_TOKEN]
        return GenerateUrl.URL


def get_ocr_reslut(image_path):
    with open(image_path, 'rb') as f:
        img = base64.b64encode(f.read())
        data = {"image": img}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = json.loads(requests_with_retry(GenerateUrl.get_url(), method='POST', headers=headers, data=data).content)
    if CommonConstants.WORDS_RESULT not in response:
        error_reason = response.get(CommonConstants.ERROR_MSG)
        if not error_reason:
            error_reason = response.text
        print('OCR获取文字结果失败，原因：', error_reason)
        return OCRError(response.get(CommonConstants.ERROR_CODE))
    return ''.join([i[CommonConstants.WORDS] for i in response[CommonConstants.WORDS_RESULT]])


def ocr_high_precision(folder_path):

    pic_path_list = [os.path.join(folder_path, i) for i in os.listdir(folder_path)]
    pic_path_list.sort(key=lambda x: os.path.basename(x).split('.')[0].split('_')[-1].zfill(5))

    ocr_txt_path = os.path.join(os.path.dirname(folder_path), f'{os.path.basename(folder_path)}_ocr_result.txt')
    idx = 0
    btime = time.time()
    print('开始请求OCR了...')
    while idx < len(pic_path_list):
        ocr_result = get_ocr_reslut(pic_path_list[idx])
        if isinstance(ocr_result, OCRError):
            if ocr_result.code == CommonConstants.REQUEST_REACH_LIMIT_ERROR_CODE:
                print('中断OCR处理！')
                break
            else:
                continue
        with open(ocr_txt_path, 'a', encoding='utf-8') as f:
            f.write(ocr_result + '\n')
        idx += 1
        minutes_left = ((time.time()-btime)/((idx+1)/len(pic_path_list)))/60
        print(f"处理了第{idx+1}张，总共{len(pic_path_list)}张，还需要{round(minutes_left,1)}分钟...")
    return ocr_txt_path


if __name__ == "__main__":
    get_ocr_reslut(r"C:\Dpan\python-script\pdf_convert\数据\精要主义 如何应对拥挤不堪的工作与生活\精要主义 如何应对拥挤不堪的工作与生活 _image\精要主义 如何应对拥挤不堪的工作与生活 _7.png")
