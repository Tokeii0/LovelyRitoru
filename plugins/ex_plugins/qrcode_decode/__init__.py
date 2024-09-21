import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import os

__plugin_name__ = "QR码解码器"
__description__ = "解码图片中的QR码"

def __checktype__(file_path):
    return file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))

def __start__(file_path, password_list=None):
    try:
        # 读取图片
        img = cv2.imread(file_path)
        if img is None:
            return "无法读取图片", []

        # 解码QR码
        decoded_objects = pyzbar.decode(img)
        if not decoded_objects:
            return "未找到QR码", []

        # 提取QR码内容
        qr_data = decoded_objects[0].data.decode('utf-8')

        # 创建输出文件
        output_dir = os.path.join("output", "qrcode_info")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.splitext(os.path.basename(file_path))[0] + "_qrcode.txt"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"QR码信息 - {file_path}:\n")
            f.write(f"QR码内容: {qr_data}\n")

        log_message = f"成功解码QR码，内容已保存到 {output_path}"
        return log_message, [output_path, qr_data]
    except Exception as e:
        return f"解码QR码时发生错误: {str(e)}", []

def __result__(result):
    if isinstance(result, tuple) and len(result) == 2:
        _, data = result
        if isinstance(data, list) and len(data) > 1:
            return f"QR码内容: {data[1]}"
    return None