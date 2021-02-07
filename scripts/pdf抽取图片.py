from pdf2image import convert_from_path
import os
from PIL import Image
from tqdm import tqdm
from constants.common import CommonConstants


def pdf_extract(pdf_path):
    working_dir = os.getenv(CommonConstants.WORKON_HOME)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_folder = os.path.join(os.path.dirname(pdf_path), f'{pdf_name}_image')
    temp_folder = os.path.join(working_dir, 'temp')
    try:
        os.mkdir(output_folder)
    except:
        pass
    try:
        os.mkdir(temp_folder)
    except:
        pass

    pdf_pages = convert_from_path(
        pdf_path=pdf_path,
        dpi=200,
        output_folder=temp_folder,
        poppler_path=os.path.join(working_dir, 'bin', 'poppler-0.68.0/bin'),
        paths_only=True
    )

    for i, page in enumerate(tqdm(pdf_pages)):
        print(page)
        page = Image.open(page)
        page.save(os.path.join(output_folder, f'{pdf_name}_{i}.png'), 'png')

    for temp_file in os.listdir(temp_folder):
        try:
            os.remove(os.path.join(temp_folder, temp_file))
        except Exception as e:
            print('删除pdf抽取临时文件错误:', e)
    os.rmdir(temp_folder)

    return output_folder


if __name__ == "__main__":
    pdf_extract(r"C:\Dpan\python-script\pdf_convert\数据\10人以下小团队管理手册-堀之内克彦.pdf")
