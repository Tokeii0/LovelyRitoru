from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton, QMessageBox, QMenu, QGroupBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction,QIcon
import os
import subprocess

class FileStructureWindow(QWidget):
    add_to_main_list = Signal(str)  # 新增信号

    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.setWindowTitle("文件结构")
        self.setGeometry(200, 200, 400, 600)
        self.setWindowIcon(QIcon("logo.ico"))
        main_layout = QVBoxLayout()

        # 创建文件结构组
        file_structure_group = QGroupBox("输出文件结构")
        file_structure_layout = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("输出文件")
        self.tree.itemDoubleClicked.connect(self.open_file)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        file_structure_layout.addWidget(self.tree)

        refresh_button = QPushButton("刷新")
        refresh_button.clicked.connect(self.populate_tree)
        file_structure_layout.addWidget(refresh_button)

        file_structure_group.setLayout(file_structure_layout)
        main_layout.addWidget(file_structure_group)

        self.setLayout(main_layout)
        self.populate_tree()

    def show_context_menu(self, position):
        item = self.tree.itemAt(position)
        if item is not None:
            menu = QMenu()
            add_action = QAction("添加到主文件列表", self)
            add_action.triggered.connect(lambda: self.add_to_main_list.emit(item.data(0, Qt.UserRole)))
            menu.addAction(add_action)
            menu.exec(self.tree.viewport().mapToGlobal(position))

    def populate_tree(self):
        self.tree.clear()
        output_dir = self.file_manager.get_output_dir()
        root = QTreeWidgetItem(self.tree, [output_dir])
        self.add_files(output_dir, root)
        self.tree.expandAll()  # 展开所有节点

    def add_files(self, path, parent):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            tree_item = QTreeWidgetItem(parent, [item])
            tree_item.setData(0, Qt.UserRole, item_path)  # 存储完整路径
            if os.path.isdir(item_path):
                self.add_files(item_path, tree_item)

    def open_file(self, item, column):
        file_path = item.data(0, Qt.UserRole)
        if os.path.isfile(file_path):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                elif os.name == 'posix':  # macOS 和 Linux
                    subprocess.call(('xdg-open', file_path))
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法打开文件: {str(e)}")
        else:
            QMessageBox.information(self, "提示", "这是一个文件夹，无法直接打开。")