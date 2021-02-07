from scripts.pdf抽取图片 import pdf_extract
from scripts.pic图片切割 import pic_cut
from scripts.tts_ws_python3 import tts_run_total
from scripts.audio_convert import wav2mp3_whole_folder_convert_with_file_move, mp3tomp4
from scripts.cancat_audio import cancat_audio
from scripts.txt文本切分 import txt_cut
from constants.common import CommonConstants
import os
import time
import argparse
import sys


def ensemble_run(pdf_path, output_mp4: bool, margin_top=0, margin_bottom=0, cut_length=10000):
    os.environ[CommonConstants.WORKON_HOME] = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(os.getenv(CommonConstants.WORKON_HOME), 'bin'))
    pdf_path = os.path.abspath(pdf_path)
    image_folder_path = os.path.join(os.path.dirname(pdf_path), f'{os.path.splitext(os.path.basename(pdf_path))[0]}_image')
    btime = time.time()

    if not os.path.exists(image_folder_path):
        print('第一次从PDF抽取图片...')
        image_folder_path = pdf_extract(pdf_path)
        print('可以开始查看图像坐标了...')
    else:
        # print('删除第一次的图片...')
        # shutil.rmtree(image_folder_path)
        # print('第二次从PDF抽取图片...')
        # image_folder_path = pdf_extract(pdf_path)  # 20200107 没看懂第二次为什么把图片删除重新抽一次，姑且先把第二次的抽取环节去除了
        os.environ[CommonConstants.PW] = input("没想到吧，输入密码！")
        print('复用第一次抽取的图片...')
        page_count = len(os.listdir(image_folder_path))
        print('开始切图...')
        pic_cut(image_folder_path, margin_top, margin_bottom)
        print('开始过OCR...')
        from scripts.OCR高精度 import ocr_high_precision
        ocr_txt_path = ocr_high_precision(image_folder_path)
        print('开始过TTS...')
        audio_folder_path = tts_run_total(ocr_txt_path)
        print('开始转换音频...')
        wav2mp3_whole_folder_convert_with_file_move(audio_folder_path)
        print('开始合并音频...')
        cancat_folder_path = cancat_audio(audio_folder_path, 4)
        if output_mp4:
            print('把合并后的mp3转为mp4...')
            mp3tomp4(cancat_folder_path)
        print('开始切分文本...')
        txt_cut(ocr_txt_path, cut_length)
        process_duration = time.time()-btime
        print('处理完毕，处理{}页，共耗时{}秒，平均每页耗时{}秒...'.format(page_count, int(process_duration), int(process_duration/page_count)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('pdf_path', help='PDF文件的完整地址')
    parser.add_argument('-no4', '--not_output_mp4', help='是否不要转换生成mp4文件', action='store_false')
    parser.add_argument('-t', '--top', help='margin_top：切图时页面上边距', default=0, type=int)
    parser.add_argument('-b', '--bottom', help='margin_bottom：切图时页面下边距', default=0, type=int)
    args = parser.parse_args()
    ensemble_run(
        args.pdf_path,
        output_mp4=args.not_output_mp4,
        margin_top=args.top,
        margin_bottom=args.bottom,
        cut_length=10000
    )
