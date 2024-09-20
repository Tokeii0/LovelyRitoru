import re

__plugin_name__ = "Flag_check"
__description__ = "flag{...} 格式的内容"

def __checktype__(file_path):
    return True  # 允许检查所有文件类型

def __start__(file_path):
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
        
        # 尝试以不同的编码解码文件内容
        encodings = ['utf-8', 'gbk', 'iso-8859-1']
        decoded_content = None
        for encoding in encodings:
            try:
                decoded_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if decoded_content is None:
            return f"无法解码文件 {file_path} 的内容"
        
        flag_pattern = r'flag{[^}]+}'
        flags = re.findall(flag_pattern, decoded_content)
        
        if flags:
            return f"在文件 {file_path} 中找到以下 flag：\n" + "\n".join(flags)
        else:
            return f"在文件 {file_path} 中未找到 flag。"
    except Exception as e:
        return f"处理文件 {file_path} 时出错：{str(e)}"

def __result__(result):
    # 如果结果中包含 flag，则返回结果，否则返回 None
    if "找到以下 flag" in result:
        return result
    return None