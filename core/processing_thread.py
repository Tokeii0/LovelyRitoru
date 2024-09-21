from PySide6.QtCore import QThread, Signal
import time, os

class ProcessingThread(QThread):
    update_log = Signal(str)
    update_result = Signal(str)
    update_password = Signal(str)
    finished = Signal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.stop_flag = False

    def run(self):
        try:
            self.process_files()
        except Exception as e:
            self.update_log.emit(f"[系统] 处理过程中发生错误: {str(e)}")
        finally:
            self.finished.emit()

    def process_files(self):
        files_to_process = self.main_window.file_manager.get_all_files().copy()
        processed_files = set()
        check_plugins = self.main_window.get_enabled_plugins(self.main_window.check_plugins_list)
        base_plugins = self.main_window.get_enabled_plugins(self.main_window.base_plugins_list)
        ex_plugins = self.main_window.get_enabled_plugins(self.main_window.ex_plugins_list)

        while files_to_process:
            if self.stop_flag:
                break
            file_path = files_to_process.pop(0)
            if file_path in processed_files or file_path is None:
                continue
            processed_files.add(file_path)
            
            self.update_log.emit(f"正在处理文件: {file_path}")
            
            # 运行check_plugins
            self.run_plugins(check_plugins, file_path, 'check_plugins')
            
            # 运行base_plugins
            new_files = self.run_plugins(base_plugins, file_path, 'base_plugins')
            files_to_process.extend([f for f in new_files if f not in processed_files and f is not None])
            
            # 运行ex_plugins
            ex_new_files = self.run_plugins(ex_plugins, file_path, 'ex_plugins')
            files_to_process.extend([f for f in ex_new_files if f not in processed_files and f is not None])
            
            # 检查output目录是否有新生成的文件
            output_dir = os.path.join(os.getcwd(), "output")
            for root, dirs, files in os.walk(output_dir):
                for new_file in files:
                    new_file_path = os.path.join(root, new_file)
                    if new_file_path not in processed_files and new_file_path not in files_to_process:
                        files_to_process.append(new_file_path)
                        self.update_log.emit(f"发现新文件: {new_file_path}")
        
        # 最后，对所有处理过的文件再次运行check_plugins
        for file_path in processed_files:
            if file_path is not None:
                self.run_plugins(check_plugins, file_path, 'check_plugins')

    def run_plugins(self, plugin_names, file_path, plugin_type):
        new_files = []
        for plugin_name in plugin_names:
            if self.stop_flag:
                break
            plugin = self.main_window.plugin_manager.get_plugin(plugin_type, plugin_name)
            if plugin:
                actual_plugin_name = plugin_name.split(':')[0].strip()
                if file_path is not None and hasattr(plugin, '__checktype__') and plugin.__checktype__(file_path):
                    if hasattr(plugin, '__start__'):
                        password_list = [self.main_window.password_list.item(i).text() 
                                    for i in range(self.main_window.password_list.count())]    
                        result = plugin.__start__(file_path, password_list)
                        if isinstance(result, tuple) and len(result) == 2:
                            log_message, flags = result
                            self.update_log.emit(f"[{actual_plugin_name}] {log_message}")
                            if flags:
                                for flag in flags:
                                    self.update_log.emit(f"[{actual_plugin_name}] 找到 flag: {flag}")
                            if result[1] is not None:
                                new_files.extend([f for f in result[1] if f is not None and isinstance(f, str)])
                        elif isinstance(result, list): 
                            self.update_log.emit(f"[{actual_plugin_name}] 执行完成")
                            new_files.extend([f for f in result[1:] if isinstance(f, str) and os.path.isfile(f)])
                        else:
                            self.update_log.emit(f"[{actual_plugin_name}] {result}")
                        if hasattr(plugin, '__result__'):
                            result_output = plugin.__result__(result)
                            if result_output:
                                formatted_result = f"[{actual_plugin_name}] {result_output}"
                                self.update_result.emit(formatted_result)
                        if hasattr(plugin, '__topasswdlist__'):
                            passwords = plugin.__topasswdlist__(result)
                            for password in passwords:
                                self.update_password.emit(password)
                                self.update_log.emit(f"[{actual_plugin_name}] 添加新密码: {password}")
        return new_files

    def stop(self):
        self.stop_flag = True
        self.wait()