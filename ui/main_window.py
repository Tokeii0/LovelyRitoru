from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QListWidget, QTextEdit, QFileDialog,
                               QGroupBox, QLabel, QListWidgetItem, QCheckBox,QSplitter,QMenu,QApplication,QLineEdit,QGridLayout,QMessageBox)
from PySide6.QtGui import QAction,QIcon
from PySide6.QtCore import Qt, QTimer, QRect

from core.file_manager import FileManager
from core.processing_thread import ProcessingThread
from core.plugin_manager import PluginManager
from .file_structure_window import FileStructureWindow

import shutil
import os
import zipfile
from datetime import datetime
import time, os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LovelyRitoru")
        self.setGeometry(100, 100, 1200, 600)
        # logo.ico
        self.setWindowIcon(QIcon("logo.ico"))

        self.file_manager = FileManager()
        self.plugin_manager = PluginManager()
        self.results_list = None  # 添加这行
        self.file_structure_window = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.password_list = QListWidget()
        self.password_input = QLineEdit()
        self.add_password_button = QPushButton("添加")
        self.init_ui()

        self.processing_thread = None
        self.connect_signals()
    def connect_signals(self):
        self.start_button.clicked.connect(self.start_processing)
        self.stop_button.clicked.connect(self.stop_processing)
        if self.processing_thread:
            self.processing_thread.update_password.connect(self.update_password_slot)
    def init_ui(self):
        



        central_widget = QWidget()
        main_layout = QHBoxLayout()

        # 左侧布局
        left_layout = QVBoxLayout()

        # 文件导入部分
        file_import_group = QGroupBox("文件导入")
        file_import_layout = QVBoxLayout()
        self.file_import_button = QPushButton("导入文件")
        self.file_import_button.clicked.connect(self.import_files)
        file_import_layout.addWidget(self.file_import_button)
        self.file_list = QListWidget()
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置自定义上下文菜单策略
        self.file_list.customContextMenuRequested.connect(self.show_file_context_menu)  # 连接自定义上下文菜单信号
        file_import_layout.addWidget(self.file_list)
        file_import_group.setLayout(file_import_layout)
        left_layout.addWidget(file_import_group, 2)
        # 在文件导入部分下方添加密码槽
        password_slot_group = QGroupBox("密码槽")
        password_slot_layout = QVBoxLayout()
        self.password_list = QListWidget()
        self.password_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.password_list.customContextMenuRequested.connect(self.show_password_context_menu)
        password_slot_layout.addWidget(self.password_list)
        # 添加密码输入框和按钮
        password_input_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.add_password_button = QPushButton("添加")
        self.add_password_button.clicked.connect(self.add_custom_password)
        password_input_layout.addWidget(self.password_input)
        password_input_layout.addWidget(self.add_password_button)
        password_slot_layout.addLayout(password_input_layout)

        password_slot_group.setLayout(password_slot_layout)
        left_layout.addWidget(password_slot_group, 1)  # 添加到左侧布局
        # 检测插件部分
        check_plugins_group = QGroupBox("检测插件")
        check_plugins_layout = QVBoxLayout()
        check_plugins_layout.setSpacing(2)
        self.check_plugins_list = QListWidget()
        check_plugins_layout.addWidget(self.check_plugins_list)
        check_plugins_group.setLayout(check_plugins_layout)
        left_layout.addWidget(check_plugins_group, 3)

        # 中间布局
        middle_layout = QVBoxLayout()
        middle_layout.setSpacing(5)

        # 控制组（包含搜索和按钮）
        control_group = QGroupBox("控制")
        control_layout = QVBoxLayout()
        control_layout.setSpacing(5)

        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索插件:")
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        control_layout.addLayout(search_layout)

        # 按钮布局
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)

        # 第一排按钮
        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(5)

        self.start_button = QPushButton("开始")
        self.start_button.clicked.connect(self.start_processing)
        first_row_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("停止")
        self.stop_button.clicked.connect(self.stop_processing)
        first_row_layout.addWidget(self.stop_button)

        self.refresh_button = QPushButton("刷新插件")
        self.refresh_button.clicked.connect(self.refresh_plugins)
        first_row_layout.addWidget(self.refresh_button)

        button_layout.addLayout(first_row_layout)

        # 第二排按钮
        second_row_layout = QHBoxLayout()
        second_row_layout.setSpacing(5)

        self.clear_button = QPushButton("清空")
        self.clear_button.clicked.connect(self.clear_all)
        second_row_layout.addWidget(self.clear_button)

        self.deduplicate_button = QPushButton("结果去重")
        self.deduplicate_button.clicked.connect(self.deduplicate_results)
        second_row_layout.addWidget(self.deduplicate_button)

        self.package_button = QPushButton("打包结果")
        self.package_button.clicked.connect(self.package_results)
        second_row_layout.addWidget(self.package_button)

        button_layout.addLayout(second_row_layout)

        control_layout.addLayout(button_layout)
        control_group.setLayout(control_layout)
        middle_layout.addWidget(control_group)

        # 修改基础工具模块
        base_plugins_group = QGroupBox("基础工具模块")
        base_plugins_layout = QGridLayout()
        base_plugins_layout.setSpacing(2)
        self.base_plugins_list = QListWidget()
        base_plugins_layout.addWidget(self.base_plugins_list, 0, 0, 1, 2)
        base_plugins_group.setLayout(base_plugins_layout)
        middle_layout.addWidget(base_plugins_group)

        # 修改进阶工具模块
        ex_plugins_group = QGroupBox("进阶工具模块")
        ex_plugins_layout = QGridLayout()
        ex_plugins_layout.setSpacing(2)
        self.ex_plugins_list = QListWidget()
        ex_plugins_layout.addWidget(self.ex_plugins_list, 0, 0, 1, 2)
        ex_plugins_group.setLayout(ex_plugins_layout)
        middle_layout.addWidget(ex_plugins_group)

        # 右侧布局
        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)

        # 修改日志显示部分
        log_group = QGroupBox("日志")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        right_layout.addWidget(log_group)

        # 修改检测结果部分
        results_group = QGroupBox("检测结果")
        results_layout = QVBoxLayout()
        self.results_list = QListWidget()
        self.results_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_list.customContextMenuRequested.connect(self.show_context_menu)
        results_layout.addWidget(self.results_list)
        results_group.setLayout(results_layout)
        right_layout.addWidget(results_group)

        # 设置布局比例
        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(middle_layout, 3)
        main_layout.addLayout(right_layout, 6)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.load_plugins()
        self.load_and_display_plugins()
    def on_search_text_changed(self):
        self.search_timer.start(300)  # 300ms 延迟

    def perform_search(self):
        search_text = self.search_input.text().lower()
        self.filter_plugins(self.check_plugins_list, search_text)
        self.filter_plugins(self.base_plugins_list, search_text)
        self.filter_plugins(self.ex_plugins_list, search_text)

    def package_results(self):
        output_dir = self.file_manager.get_output_dir()
        if not os.path.exists(output_dir):
            self.log_text.append("输出目录不存在，无法打包结果。")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"results_{timestamp}.zip"
        zip_path = os.path.join(os.path.dirname(output_dir), zip_filename)

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, output_dir)
                        zipf.write(file_path, arcname)

            self.log_text.append(f"结果已打包到: {zip_path}")
        except Exception as e:
            self.log_text.append(f"打包结果时出错: {str(e)}")

    def filter_plugins(self, list_widget, search_text):
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            widget = list_widget.itemWidget(item)
            label = widget.layout().itemAt(1).widget()
            if search_text in label.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)  

    def show_file_context_menu(self, position):
        menu = QMenu()
        delete_action = menu.addAction("删除")
        action = menu.exec_(self.file_list.mapToGlobal(position))
        if action == delete_action:
            self.delete_selected_file()

    def delete_selected_file(self):
        current_item = self.file_list.currentItem()
        if current_item:
            file_path = current_item.text()
            self.file_manager.remove_file(file_path)
            self.file_list.takeItem(self.file_list.row(current_item))
            self.log_text.append(f"已删除文件: {file_path}")

    def show_context_menu(self, pos):
        menu = QMenu(self)
        copy_action = QAction("复制", self)
        copy_action.triggered.connect(self.copy_selected_results)
        menu.addAction(copy_action)
        menu.exec(self.results_list.mapToGlobal(pos))

    def copy_selected_results(self):
        selected_items = self.results_list.selectedItems()
        if selected_items:
            clipboard = QApplication.clipboard()
            text = "\n".join([item.text() for item in selected_items])
            clipboard.setText(text)
    def load_plugins(self):
        self.populate_plugin_list(self.base_plugins_list, 'base_plugins')
        self.populate_plugin_list(self.ex_plugins_list, 'ex_plugins')
        self.populate_plugin_list(self.check_plugins_list, 'check_plugins')

    def clear_plugin_lists(self):
        self.base_plugins_list.clear()
        self.ex_plugins_list.clear()
        self.check_plugins_list.clear()

    def populate_plugin_list(self, list_widget, dir_name):
        list_widget.clear()
        plugins = self.plugin_manager.get_plugins(dir_name)
        for plugin_name in plugins:
            item = QListWidgetItem(list_widget)
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(2, 2, 2, 2)  # 减小边距
            layout.setSpacing(2)  # 减小控件之间的间距
            
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            
            label = QLabel(plugin_name)
            label.setWordWrap(True)
            
            layout.addWidget(checkbox)
            layout.addWidget(label, 1)
            
            item.setSizeHint(widget.sizeHint())
            list_widget.addItem(item)
            list_widget.setItemWidget(item, widget)

    def load_and_display_plugins(self):
        self.plugin_manager.load_all_plugins()  # 加载所有插件
        self.populate_plugin_list(self.base_plugins_list, 'base_plugins')
        self.populate_plugin_list(self.ex_plugins_list, 'ex_plugins')
        self.populate_plugin_list(self.check_plugins_list, 'check_plugins')

    def import_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "导入文件")
        if file_paths:
            for file_path in file_paths:
                self.file_manager.add_file(file_path)
                self.file_list.addItem(file_path)
            self.log_text.append(f"已导入 {len(file_paths)} 个文件")

    def start_processing(self):
        if self.processing_thread is None or not self.processing_thread.isRunning():
            self.processing_thread = ProcessingThread(self)
            self.processing_thread.update_log.connect(self.update_log)
            self.processing_thread.update_result.connect(self.update_result)
            self.processing_thread.update_password.connect(self.update_password_slot)
            self.processing_thread.finished.connect(self.processing_finished)
            self.processing_thread.start()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.log_text.append("开始新的处理过程...")
        else:
            self.log_text.append("处理已在进行中，无法启动新的处理过程。")

    def update_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)

    def update_result(self, result):
        # 检查结果是否已存在
        items = [self.results_list.item(i).text() for i in range(self.results_list.count())]
        if result not in items:
            self.results_list.addItem(result)
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.append(f"[{timestamp}] 重复结果: {result}")
        
    def update_password_slot(self, password):
        timestamp = datetime.now().strftime("%H:%M:%S")
        items = [self.password_list.item(i).text() for i in range(self.password_list.count())]
        if password not in items:
            self.password_list.addItem(password)
            self.log_text.append(f"[{timestamp}] 添加新密码到密码槽: {password}")
            
            self.log_text.append(f"[{timestamp}] 尝试重新启动处理过程...")
            if self.processing_thread and self.processing_thread.isRunning():
                self.log_text.append(f"[{timestamp}] 处理线程已在运行，停止当前线程...")
                self.stop_processing()
            self.start_processing()
        else:
            #标准日志格式
            self.log_text.append(f"[{timestamp}] 密码 '{password}' 已存在")
    def deduplicate_results(self):
        timestamp = datetime.now().strftime("%H:%M:%S")
        original_count = self.results_list.count()
        unique_results = []
        seen = set()
        
        for i in range(original_count):
            item = self.results_list.item(i)
            text = item.text()
            if text not in seen:
                seen.add(text)
                unique_results.append(text)
        
        self.results_list.clear()
        for result in unique_results:
            self.results_list.addItem(result)
        
        removed_count = original_count - len(unique_results)
        self.log_text.append(f"[{timestamp}]去重完成，共删除 {removed_count} 条重复结果。")

    def stop_processing(self):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.stop()
            self.log_text.append(f"[{timestamp}]正在停止处理...")

    def refresh_plugins(self):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.plugin_manager.refresh_plugins()
        self.load_plugins()
        self.log_text.append(f"[{timestamp}] 插件已刷新。")

    def processing_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.log_text.append("处理完成。")
        self.show_file_structure()  # 在处理完成后自动显示文件结构

    def get_enabled_plugins(self, list_widget):
        enabled_plugins = []
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            widget = list_widget.itemWidget(item)
            checkbox = widget.layout().itemAt(0).widget()
            if checkbox.isChecked():
                plugin_name = widget.layout().itemAt(1).widget().text()
                enabled_plugins.append(plugin_name)
        return enabled_plugins
    
    def clear_all(self):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.clear()
        self.file_manager.clear_files()
        self.file_list.clear()
        self.results_list.clear()
        
        self.log_text.append(f"[{timestamp}] 已清空所有内容。")

    def show_file_structure(self):
        if self.file_structure_window is None:
            self.file_structure_window = FileStructureWindow(self.file_manager)
            self.file_structure_window.add_to_main_list.connect(self.add_file_from_structure)  # 连接信号
        
        # 获取主窗口的几何信息
        main_geometry = self.geometry()
        
        # 计算文件结构窗口的位置
        file_structure_x = main_geometry.right()
        file_structure_y = main_geometry.top()
        
        # 设置文件结构窗口的几何信息
        self.file_structure_window.setGeometry(QRect(
            file_structure_x,
            file_structure_y,
            400,  # 宽度
            main_geometry.height()  # 高度与主窗口相同
        ))
        
        self.file_structure_window.populate_tree()  # 刷新树
        self.file_structure_window.show()
    def add_file_from_structure(self, file_path):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if os.path.isfile(file_path):
            self.file_manager.add_file(file_path)
            self.file_list.addItem(file_path)
            self.log_text.append(f"[{timestamp}] 已添加文件: {file_path}")
        else:
            self.log_text.append(f"[{timestamp}] 无法添加文件夹: {file_path}")


    def show_password_context_menu(self, position):
        menu = QMenu()
        delete_action = menu.addAction("删除")
        action = menu.exec_(self.password_list.mapToGlobal(position))
        if action == delete_action:
            self.delete_selected_password()

    def delete_selected_password(self):
        current_item = self.password_list.currentItem()
        if current_item:
            self.password_list.takeItem(self.password_list.row(current_item))

    def add_custom_password(self):
        password = self.password_input.text().strip()
        if password:
            self.password_list.addItem(password)
            self.password_input.clear()    
    def closeEvent(self, event):
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.stop()
            self.processing_thread.wait()  # 等待线程完成

        output_dir = self.file_manager.get_output_dir()
        if os.path.exists(output_dir) and os.listdir(output_dir):
            reply = QMessageBox.question(self, '确认操作',
                                         "是否要打包并删除 output 文件夹中的文件？",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                         QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.package_results()
                try:
                    shutil.rmtree(output_dir)
                    os.makedirs(output_dir)
                    self.log_text.append("output 文件夹已清空。")
                except Exception as e:
                    self.log_text.append(f"清空 output 文件夹时出错: {str(e)}")
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return

        event.accept()