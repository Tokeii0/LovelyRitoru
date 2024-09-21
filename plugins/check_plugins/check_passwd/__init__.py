import re

__plugin_name__ = "Password_check"
__description__ = "检测可能的密码格式"

def __checktype__(file_path):
    return True  # 允许检查所有文件类型

def __start__(file_path, password_list=None):
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
            return f"无法解码文件 {file_path} 的内容", []
        
        # 使用正则表达式匹配可能的密码格式
        password_pattern = r'(?:password|passwd|pwd)[:=]\s*(\S+)'
        passwords = re.findall(password_pattern, decoded_content, re.IGNORECASE)
        
        if passwords:
            log_message = f"在文件 {file_path} 找到以下可能的密码:\n" + "\n".join(passwords)
            return log_message, passwords
        else:
            return f"在文件 {file_path} 中未找到可能的密码。", []

    except Exception as e:
        return f"处理文件 {file_path} 时出错：{str(e)}", []

def __result__(result):
    # 只在结果列表中显示一条简洁的消息
    if isinstance(result, tuple) and len(result) == 2:
        _, passwords = result
        if passwords:
            return f"找到可能的密码：{', '.join(passwords)}"
    return None

def __topasswdlist__(result):
    # 从结果中提取密码并返回列表
    if isinstance(result, tuple) and len(result) == 2:
        _, passwords = result
        return passwords
    return []