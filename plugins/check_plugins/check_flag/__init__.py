import re

__plugin_name__ = "Flag_check"
__description__ = "flag{...} 格式的内容"

def __checktype__(file_path):
    return True  # 允许检查所有文件类型

def __start__(file_path, password_list=None):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        flag_pattern = r'flag\{[^}]+\}'
        flags = re.findall(flag_pattern, content)
        
        if flags:
            return f"在文件 {file_path} 中找到以下 flag：\n" + "\n".join(flags), flags
        else:
            return f"在文件 {file_path} 中未找到 flag。", None
    except Exception as e:
        return f"处理文件 {file_path} 时出错：{str(e)}", None

def __result__(result):
    if isinstance(result, tuple) and result[1]:
        return "\n".join(result[1])
    return None