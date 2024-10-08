__plugin_name__ = "解压插件"
__description__ = "解压压缩包"

import os
import zipfile
import hashlib

def __checktype__(file_path):
    return file_path.lower().endswith('.zip')

def get_file_hash(file_path):
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    return file_hash.hexdigest()

def __start__(file_path, password_list=None):
    try:
        processed_files = set()
        output_files = []
        
        def extract_zip(zip_path, depth=0):
            if depth > 5:  # 限制解压深度
                return
            
            file_hash = get_file_hash(zip_path)
            if file_hash in processed_files:
                return
            processed_files.add(file_hash)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                output_dir = os.path.join("output", os.path.splitext(os.path.basename(zip_path))[0])
                os.makedirs(output_dir, exist_ok=True)
                
                for file_info in zip_ref.infolist():
                    try:
                        zip_ref.extract(file_info, output_dir)
                    except RuntimeError:  # 需要密码
                        if password_list:
                            for password in password_list:
                                try:
                                    zip_ref.extract(file_info, output_dir, pwd=password.encode())
                                    break  # 如果成功解压,跳出循环
                                except:
                                    continue  # 如果密码错误,尝试下一个密码
                            else:
                                print(f"无法解压文件 {file_info.filename}：所有密码都失败")
                        else:
                            print(f"文件 {file_info.filename} 需要密码解压,但没有提供密码列表")
                
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    output_files.append(file_path)
                    if file.lower().endswith('.zip'):
                        extract_zip(file_path, depth + 1)
        
        extract_zip(file_path)
        return f"成功解压文件 {file_path}", output_files
    except Exception as e:
        return f"处理文件 {file_path} 时出错：{str(e)}", []

def __result__(result):
    return None  # 返回None，这样就不会将结果添加到结果窗口