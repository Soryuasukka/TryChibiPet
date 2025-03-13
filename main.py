import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.QtCore import Qt, QPoint
from ui_pet import Ui_Form  # UI 文件

class DesktopPet(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 设置无边框 & 透明背景
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # **默认状态 GIF（待机）**
        self.relax_gif = QMovie("pics/relax.gif")  # 默认状态
        self.relax_gif.setSpeed(150)
        self.label_pet.setMovie(self.relax_gif)
        self.relax_gif.start()

        # **交互状态 GIF（点击时触发）**
        self.interact_gif = QMovie("pics/interact.gif")  # 交互状态
        self.interact_gif.setSpeed(150)
        self.interact_gif.setPaused(True)  # 初始时暂停，等待触发
        self.interact_gif.finished.connect(self.restore_relax_gif)  # 播放完毕后恢复 relax.gif

        # 记录鼠标位置
        self.dragging = False
        self.offset = QPoint()

        # **添加系统托盘**
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("pics/relax.gif"))  # 托盘图标
        self.tray_icon.setToolTip("HERE!")  # 鼠标悬停提示
        self.tray_icon.activated.connect(self.on_tray_activated)

        # 托盘菜单
        menu = QMenu()
        show_action = QAction("召唤!", self)
        show_action.triggered.connect(self.show_pet)
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close_app)

        menu.addAction(show_action)
        menu.addAction(exit_action)
        self.tray_icon.setContextMenu(menu)

        self.tray_icon.show()

    def resizeEvent(self, event):
        """窗口缩放时，调整 GIF 尺寸"""
        self.relax_gif.setScaledSize(self.label_pet.size())
        self.interact_gif.setScaledSize(self.label_pet.size())
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        """鼠标单击时播放 interact.gif（只播放 1 次）"""
        if event.button() == Qt.LeftButton:
            self.label_pet.setMovie(self.interact_gif)  # 切换到 interact.gif
            self.interact_gif.setPaused(False)  # 播放 interact.gif
            self.interact_gif.start()

    def restore_relax_gif(self):
        """interact.gif 播放完后恢复 relax.gif"""
        self.label_pet.setMovie(self.relax_gif)
        self.relax_gif.start()

    def mouseMoveEvent(self, event):
        """鼠标拖动桌宠"""
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        """鼠标释放，停止拖动"""
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def mouseDoubleClickEvent(self, event):
        """双击隐藏 / 召唤桌宠"""
        if event.button() == Qt.LeftButton:
            if self.isVisible():
                self.hide()
            else:
                self.show()

    def on_tray_activated(self, reason):
        """点击系统托盘图标，召唤桌宠"""
        if reason == QSystemTrayIcon.Trigger:  # 单击托盘图标
            self.show_pet()

    def show_pet(self):
        """召唤桌宠"""
        self.showNormal()

    def close_app(self):
        """退出应用"""
        self.tray_icon.hide()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())
