from PIL import Image
from PIL.ExifTags import TAGS
import os
import re

__plugin_name__ = "EXIF检测器"
__description__ = "检测图片的EXIF信息"

def __checktype__(file_path):
    return file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))

def __start__(file_path):
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()

        if not exif_data:
            return f"文件 {file_path} 没有EXIF信息。"

        exif_info = []
        flag = None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'XPComment' and isinstance(value, bytes):
                decoded_value = value.decode('utf-16le', errors='ignore').rstrip('\x00')
                flag_match = re.search(r'flag{[^}]+}', decoded_value)
                if flag_match:
                    flag = flag_match.group(0)
            # 去除无意义字符
            if isinstance(value, str):
                value = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', value)
            elif isinstance(value, bytes):
                value = value.decode('utf-8', errors='ignore')
                value = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', value)
            exif_info.append(f"{tag}: {value}")

        # 创建输出文件
        output_dir = os.path.join("output", "exif_info")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.splitext(os.path.basename(file_path))[0] + "_exif.txt"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"EXIF信息 - {file_path}:\n")
            f.write("\n".join(exif_info))

        result = f"EXIF信息已保存到 {output_path}\n" + "\n".join(exif_info[:5]) + "\n..."
        if flag:
            result += f"\n在EXIF信息中找到flag: {flag}"
        
        return [result, output_path]  # 返回结果字符串和输出文件路径

    except Exception as e:
        return f"处理文件 {file_path} 时出错：{str(e)}"

def __result__(result):
    if isinstance(result, list) and len(result) == 2:
        if "EXIF信息已保存到" in result[0] or "在EXIF信息中找到flag" in result[0]:
            return result[0]
    return None