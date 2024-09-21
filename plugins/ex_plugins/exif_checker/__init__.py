from PIL import Image
from PIL.ExifTags import TAGS
import os
import re

__plugin_name__ = "EXIF检测器"
__description__ = "检测图片的EXIF信息"

def __checktype__(file_path):
    return file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))

def clean_value(value):
    if isinstance(value, bytes):
        try:
            value = value.decode('utf-8', errors='ignore')
        except:
            value = str(value)
    return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(value))

def __start__(file_path, password_list=None):
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()

        if not exif_data:
            return f"文件 {file_path} 没有EXIF信息。", None

        exif_info = []
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            cleaned_value = clean_value(value)
            exif_info.append(f"{tag}: {cleaned_value}")

        # 修改输出文件的保存位置和命名方式
        output_dir = os.path.dirname(file_path)
        output_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_exif.txt"
        #取完整路径
        output_path = os.path.abspath(os.path.join(output_dir, output_filename))

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"EXIF信息 - {file_path}:\n")
            f.write("\n".join(exif_info))

        summary = "\n".join(exif_info[:5])
        if len(exif_info) > 5:
            summary += "\n..."

        log_message = f"成功提取EXIF信息，已保存到 {output_path[1]}\n\nEXIF信息摘要:\n{summary}"
        
        return log_message, [None,output_path]

    except Exception as e:
        return f"处理文件 {file_path} 时出错：{str(e)}", None

def __result__(result):
    # if isinstance(result, tuple) and len(result) == 2:
    #     _, output_path = result
    #     if output_path:
    #         return f"完整EXIF信息已保存到: {output_path[1]}"
    return None