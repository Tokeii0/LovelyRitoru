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

def __start__(file_path, password_list=None):
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
        
        decode_count = 0
        original_content = content
        
        while True:
            try:
                # 尝试解码
                decoded_content = base64.b64decode(content)
                decode_count += 1
                content = decoded_content.decode('utf-8', errors='ignore')
            except:
                # 如果无法继续解码，跳出循环
                break
        
        if decode_count > 0:
            # 创建输出文件
            output_dir = os.path.join("output", "base64_decoded")
            os.makedirs(output_dir, exist_ok=True)
            output_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_decoded_{decode_count}.b64"
            output_path = os.path.join(output_dir, output_filename)
            
            # 保存最终解码后的内容
            try:
                with open(output_path, 'wb') as f:
                    f.write(decoded_content)
            except:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return ["",output_path]
        else:
            return []
    except Exception as e:
        return f"处理文件 {file_path} 时出错：{str(e)}"

