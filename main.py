import sys
import time
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建启动画面
    splash_pixmap = QPixmap("start.png")
    #大小0.5倍
    splash_pixmap = splash_pixmap.scaled(splash_pixmap.width() * 0.5, splash_pixmap.height() * 0.5)
    splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setEnabled(False)

    
    splash.setWindowOpacity(0.)
    splash.show()
    start_time = time.time()
    while time.time() - start_time < 1:
        app.processEvents()
    window = MainWindow()
    window.show()
    
    splash.finish(window)
    
    sys.exit(app.exec())