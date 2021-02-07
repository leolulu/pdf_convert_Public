from tqdm import tqdm
import os
from pydub import AudioSegment
from functools import reduce
import math


def cancat_audio(folder_path, cancat_num):
    title_name = os.path.basename(folder_path)
    path_list = [os.path.join(folder_path, i) for i in os.listdir(folder_path) if os.path.splitext(i)[-1] == '.mp3']
    path_list.sort(key=lambda x: os.path.basename(x).split('.')[0].split('-')[-1].zfill(5))
    # path_list = np.array_split(path_list, int(len(path_list)/cancat_num) if len(path_list) >= cancat_num else 1)
    path_list = [path_list[i*cancat_num:(i+1)*cancat_num] for i in range(math.ceil(len(path_list) / cancat_num))]
    print(path_list)

    inner_folder_path = os.path.join(folder_path, title_name+'_合并音频')
    try:
        os.makedirs(inner_folder_path)
    except:
        pass

    for i, every_list_part in enumerate(tqdm(path_list)):
        audio_list = map(lambda x: AudioSegment.from_mp3(x), every_list_part)
        reduce(lambda x, y: x+y, audio_list).export(
            os.path.join(
                inner_folder_path,
                '{}_concat_audio_{}.mp3'.format(title_name, str(i).zfill(3))
            ),
            format='mp3'
        )

    return inner_folder_path


if __name__ == "__main__":
    cancat_audio(r'D:\OneDrive - Office.Inc\小文件中转站\懂得选择的女人更幸福_audio', 4)
