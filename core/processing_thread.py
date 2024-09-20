from PySide6.QtCore import QThread, Signal
import time, os

class ProcessingThread(QThread):
    update_log = Signal(str)
    update_result = Signal(str)
    finished = Signal()


    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.stop_flag = False

    def run(self):
        try:
            self.process_files()
        except Exception as e:
            self.update_log.emit(f"处理过程中发生错误: {str(e)}")
        finally:
            self.finished.emit()

    def process_files(self):
        files_to_process = self.main_window.file_manager.get_all_files().copy()  # 创建文件列表的副本
        processed_files = set()  # 用于跟踪已处理的文件
        check_plugins = self.main_window.get_enabled_plugins(self.main_window.check_plugins_list)
        base_plugins = self.main_window.get_enabled_plugins(self.main_window.base_plugins_list)
        ex_plugins = self.main_window.get_enabled_plugins(self.main_window.ex_plugins_list)

        while files_to_process:
            if self.stop_flag:
                break
            file_path = files_to_process.pop(0)
            if file_path in processed_files:
                continue  # 跳过已处理的文件
            processed_files.add(file_path)
            
            self.update_log.emit(f"正在处理文件: {file_path}")
            
            # 运行check_plugins
            self.run_plugins(check_plugins, file_path, 'check_plugins')
            
            # 运行base_plugins
            new_files = self.run_plugins(base_plugins, file_path, 'base_plugins')
            files_to_process.extend([f for f in new_files if f not in processed_files])
            
            # 运行ex_plugins
            ex_new_files = self.run_plugins(ex_plugins, file_path, 'ex_plugins')
            files_to_process.extend([f for f in ex_new_files if f not in processed_files])
            
        # 最后，对所有处理过的文件再次运行check_plugins
        for file_path in processed_files:
            self.run_plugins(check_plugins, file_path, 'check_plugins')
    def run_plugins(self, plugin_names, file_path, plugin_type):
        new_files = []
        for plugin_name in plugin_names:
            if self.stop_flag:
                break
            plugin = self.main_window.plugin_manager.get_plugin(plugin_type, plugin_name)
            if plugin:
                self.update_log.emit(f"正在执行插件: {plugin_name}")
                if hasattr(plugin, '__checktype__') and plugin.__checktype__(file_path):
                    if hasattr(plugin, '__start__'):
                        result = plugin.__start__(file_path)
                        if isinstance(result, list) and len(result) == 2:
                            self.update_log.emit(f"插件 {plugin_name} 结果:\n{result[0]}")
                            new_files.append(result[1])  # 添加输出文件路径
                        else:
                            self.update_log.emit(f"插件 {plugin_name} 结果:\n{result}")
                        if hasattr(plugin, '__result__'):
                            result_output = plugin.__result__(result)
                            if result_output:
                                self.update_result.emit(result_output)
                        if isinstance(result, list):
                            new_files.extend([f for f in result if isinstance(f, str) and os.path.isfile(f)])
                        elif isinstance(result, str) and os.path.isfile(result):
                            new_files.append(result)
        return new_files

    def stop(self):
        self.stop_flag = True
        self.wait()