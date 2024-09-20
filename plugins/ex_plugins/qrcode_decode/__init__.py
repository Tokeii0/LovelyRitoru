import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import os

__plugin_name__ = "QR码解码器"
__description__ = "解码图片中的QR码"

def __checktype__(file_path):
    return file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))

def __start__(file_path):
    try:
        # 读取图片
        img = cv2.imread(file_path)
        if img is None:
            return "无法读取图片"
        
        # 解码QR码
        decoded_objects = pyzbar.decode(img)
        if not decoded_objects:
            return "未找到QR码"
        
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

        result = f"QR码信息已保存到 {output_path}\n"
        result += f"QR码内容: {qr_data}"
        # 返回结果，文件位置
        return [result, output_path]
    except Exception as e:
        return f"解码QR码时发生错误: {str(e)}"

def __result__(result):
    return result
