from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QPoint, QTime
from ui.ui_pet import Ui_Form  # 引入 UI 文件
from tray_icon import create_tray_icon
from config import GIF_PATH, INTERACT_PATH, PET_SIZE, RELAX_SPEED, INTERACT_SPEED

class DesktopPet(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 加载 UI 设计

        # 设置窗口无边框、透明背景、置顶显示
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # **加载 GIF**
        self.relax_gif = QMovie(GIF_PATH)
        self.relax_gif.setScaledSize(self.label_pet.size())
        self.relax_gif.setSpeed(RELAX_SPEED)

        self.interact_gif = QMovie(INTERACT_PATH)
        self.interact_gif.setScaledSize(self.label_pet.size())
        self.interact_gif.setSpeed(INTERACT_SPEED)

        self.total_frames = self.interact_gif.frameCount()
        self.interact_gif.frameChanged.connect(self.check_frame)

        self.label_pet.setMovie(self.relax_gif)
        self.relax_gif.start()

        # 记录鼠标位置 & 按下时间
        self.dragging = False
        self.offset = QPoint()
        self.mouse_down_time = QTime()
        self.mouse_down_pos = QPoint()

        # 添加系统托盘
        self.tray_icon = create_tray_icon(self)

    def mousePressEvent(self, event):
        """鼠标按下时记录时间 & 位置"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.pos()
            self.mouse_down_time.start()
            self.mouse_down_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        """鼠标释放时判断是单击还是拖动"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            time_elapsed = self.mouse_down_time.elapsed()
            distance = (event.globalPos() - self.mouse_down_pos).manhattanLength()

            if time_elapsed < 200 and distance < 10:
                self.play_interact_gif()

    def mouseMoveEvent(self, event):
        """鼠标移动时拖动窗口"""
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def play_interact_gif(self):
        """播放 interact.gif（只播放 1 次，可多次触发）"""
        self.interact_gif.stop()
        self.interact_gif.jumpToFrame(0)
        self.label_pet.setMovie(self.interact_gif)
        self.interact_gif.start()

    def check_frame(self, frame_number):
        """检查当前帧，如果到达最后一帧，则恢复 relax.gif"""
        if frame_number == self.total_frames - 1:
            self.restore_relax_gif()

    def restore_relax_gif(self):
        """交互动画播放完毕后恢复 relax.gif"""
        self.label_pet.setMovie(self.relax_gif)
        self.relax_gif.start()
