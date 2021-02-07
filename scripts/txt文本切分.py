import math
import os


def txt_cut(txt_file, cut_length):
    txt_file_name = os.path.basename(txt_file).split('_')[0]
    output_txt_path = os.path.join(os.path.dirname(txt_file), txt_file_name+'_text_cut')
    with open(txt_file, 'r', encoding='utf-8') as f:
        txt_data = f.read()
    try:
        os.mkdir(output_txt_path)
    except:
        pass
    for serial_no, block in enumerate([txt_data[i*cut_length:(i+1)*cut_length] for i in range(math.ceil(len(txt_data)/cut_length))]):
        with open(os.path.join(output_txt_path, txt_file_name+f'_{serial_no}.txt'), 'a', encoding='utf-8') as f:
            f.write(block+'\n')


if __name__ == "__main__":
    txt_cut(r"C:\Python\脚本\pdf_convert\数据\刻意练习\刻意练习_image_ocr_result.txt", 10000)
