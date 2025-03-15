from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from config import ICON_PATH


def create_tray_icon(pet):
    """创建系统托盘图标"""
    tray_icon = QSystemTrayIcon(pet)
    tray_icon.setIcon(QIcon(ICON_PATH))
    tray_icon.setToolTip("HERE!")

    menu = QMenu()
    show_action = QAction("召唤!", pet)
    show_action.triggered.connect(pet.showNormal)

    exit_action = QAction("退出", pet)
    exit_action.triggered.connect(pet.close)

    menu.addAction(show_action)
    menu.addAction(exit_action)
    tray_icon.setContextMenu(menu)

    tray_icon.show()
    return tray_icon