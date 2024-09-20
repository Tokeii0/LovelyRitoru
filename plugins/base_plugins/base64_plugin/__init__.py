import base64
import os

__plugin_name__ = "Base64解码"
__description__ = "解码Base64"
def __checktype__(file_path):
    """
    检查文件是否可能包含Base64编码的内容
    """
    # 这里我们简单地检查文件扩展名是否为.b64或.base64
    # 您可以根据需要修改或增加更复杂的检查逻辑
    return file_path.lower().endswith(('.b64', '.base64','.txt'))

def __start__(file_path):
    try:
        with open(file_path, 'r') as f:
            encoded_content = f.read().strip()
        
        # 解码Base64内容
        decoded_content = base64.b64decode(encoded_content)
        
        # 创建输出文件
        output_dir = os.path.join("output", "base64_decoded")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.splitext(os.path.basename(file_path))[0] + "_decoded"+".b64"
        output_path = os.path.join(output_dir, output_filename)
        
        # 尝试将解码后的内容写入文件
        try:
            with open(output_path, 'wb') as f:
                f.write(decoded_content)
        except:
            # 如果写入二进制文件失败,尝试写入文本文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(decoded_content.decode('utf-8', errors='ignore'))
        
        return [output_path]
    except Exception as e:
        return f"处理文件 {file_path} 时出错：{str(e)}"
    
