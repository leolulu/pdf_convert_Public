
from PIL import Image
import os
from tqdm import tqdm


def pic_cut(folder_path, margin_top, margin_bottom):
    pic_file_list = [os.path.join(folder_path, i) for i in os.listdir(folder_path)]

    for pic_path in tqdm(pic_file_list):
        img = Image.open(pic_path)
        img = img.crop((0, margin_top, img.size[0], img.size[1] if margin_bottom == 0 else margin_bottom))  # [左] [上] [右(img.save[0])] [下(img.save(1))]
        img.save(pic_path)


if __name__ == "__main__":
    pic_cut(r'C:\Dpan\python-script\pdf_convert\数据\10人以下小团队管理手册-堀之内克彦_image', 200, 400)
