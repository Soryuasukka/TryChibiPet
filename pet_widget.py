from PyQt5.QtWidgets import QWidget, QLabel, QMenu, QAction, QSystemTrayIcon
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtCore import QSize, QTimer # 导入 QSize
import random
from PyQt5.QtWidgets import QMessageBox  # 导入 QMessageBox
from config import RELAX_PATH, INTERACT_PATH, STAND_PATH, SIT_PATH, SLEEP_PATH, PET_SIZE, RELAX_SPEED, INTERACT_SPEED, DIE_PATH, SCALE_FACTOR

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口无边框、透明背景、置顶显示
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # QLabel 设置
        self.label_pet = QLabel(self)

        # GIF 加载
        self.relax_gif = self.load_gif(RELAX_PATH, RELAX_SPEED)
        self.interact_gif = self.load_gif(INTERACT_PATH, INTERACT_SPEED)
        self.sit_gif = self.load_gif(SIT_PATH, RELAX_SPEED)
        self.sleep_gif = self.load_gif(SLEEP_PATH, RELAX_SPEED)
        self.die_gif = self.load_gif(DIE_PATH, RELAX_SPEED)
        self.sk2_begin_gif = self.load_gif("pics/sk2begin.gif", RELAX_SPEED)  # 加载漂浮开始动画
        self.sk2_gif = self.load_gif("pics/sk2.gif", RELAX_SPEED)  # 加载漂浮循环动画
        self.sk3_gif = self.load_gif("pics/sk3.gif", RELAX_SPEED)  # 加载治愈动画
        # 加载 move.gif
        self.move_gif = self.load_gif("pics/move.gif", RELAX_SPEED)  # 加载移动动画
        self.stun_gif = self.load_gif("pics/stun.gif", RELAX_SPEED)  # 加载眩晕动画
        self.stunbegin_gif = self.load_gif("pics/stunbegin.gif", RELAX_SPEED)  # 加载眩晕开场动画

        self.dragging = False
        self.offset = QPoint()
        self.last_mouse_pos = QPoint()  # 记录上一次鼠标位置
        self.drag_distance = 0  # 记录拖动距离
        self.drag_start_time = 0  # 记录拖动开始时间

        # 设置初始状态
        self.current_gif = self.relax_gif
        self.set_gif(self.relax_gif)

        # 其他初始化代码...

        # 定时器
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.switch_to_move)  # 定时器触发时切换到 move.gif

        # 如果初始状态是站立状态，启动定时器
        if self.current_gif == self.relax_gif:
            self.start_idle_timer()  # 启动定时器，并设置随机时间

        # 右键菜单
        self.context_menu = QMenu(self)
        self.create_context_menu()

        # 托盘图标
        self.tray_icon = QSystemTrayIcon(QIcon(RELAX_PATH), self)
        self.tray_icon.activated.connect(self.show_pet)
        self.tray_icon.show()

        # 记录鼠标拖动状态
        self.dragging = False
        self.offset = QPoint()

    from config import SCALE_FACTOR  # 导入缩放比例

    def start_idle_timer(self):
        """启动定时器，并设置随机时间（20-40 秒）"""
        random_duration = random.randint(20000, 40000)  # 20-40 秒（单位：毫秒）
        self.idle_timer.start(random_duration)

    def load_gif(self, path, speed):
        """加载 GIF 并等比例缩小"""
        gif = QMovie(path)
        gif.setSpeed(speed)
        gif.start()  # 必须先启动 GIF，才能获取其尺寸
        gif.stop()  # 获取尺寸后停止

        # 获取原始尺寸
        original_size = gif.frameRect().size()

        # 计算缩小后的尺寸
        scaled_width = int(original_size.width() * SCALE_FACTOR)
        scaled_height = int(original_size.height() * SCALE_FACTOR)
        scaled_size = QSize(scaled_width, scaled_height)

        # 设置缩小后的尺寸
        gif.setScaledSize(scaled_size)
        return gif

    def set_gif(self, gif):
        """切换 GIF 并播放，同时调整窗口大小"""
        self.label_pet.setMovie(gif)
        gif.start()

        # 根据缩小后的 GIF 尺寸调整窗口大小
        self.resize(gif.scaledSize())
        self.label_pet.resize(gif.scaledSize())

    def create_context_menu(self):
        """创建右键菜单"""
        self.stand_action = QAction("站立", self,
                                    triggered=lambda: self.change_state(self.relax_gif, self.stand_action))
        self.sit_action = QAction("坐下", self, triggered=lambda: self.change_state(self.sit_gif, self.sit_action))
        self.sleep_action = QAction("睡觉", self,
                                    triggered=lambda: self.change_state(self.sleep_gif, self.sleep_action))
        self.float_action = QAction("漂浮", self,
                                    triggered=lambda: self.change_state(self.sk2_gif, self.float_action))  # 漂浮
        self.heal_action = QAction("治愈", self,
                                   triggered=lambda: self.change_state(self.sk3_gif, self.heal_action))  # 治愈
        self.hide_action = QAction("撤退", self, triggered=self.hide_pet)

        self.context_menu.addAction(self.stand_action)
        self.context_menu.addAction(self.sit_action)
        self.context_menu.addAction(self.sleep_action)
        self.context_menu.addAction(self.float_action)  # 添加漂浮选项
        self.context_menu.addAction(self.heal_action)  # 添加治愈选项
        self.context_menu.addAction(self.hide_action)

    def contextMenuEvent(self, event):
        """右键点击时弹出菜单"""
        self.update_context_menu()
        self.context_menu.exec_(event.globalPos())

    def update_context_menu(self):
        """更新菜单状态，当前状态显示 ‘(当前)’"""
        actions = [self.stand_action, self.sit_action, self.sleep_action, self.float_action, self.heal_action]
        gifs = [self.relax_gif, self.sit_gif, self.sleep_gif, self.sk2_gif, self.sk3_gif]

        for action, gif in zip(actions, gifs):
            if gif == self.current_gif:
                action.setText(action.text().split(" ")[0] + " (当前)")
            else:
                action.setText(action.text().split(" ")[0])

    def change_state(self, gif, action):
        """切换状态"""
        if gif == self.relax_gif:  # 如果是站立状态
            if not self.idle_timer.isActive():  # 如果定时器未启动
                self.start_idle_timer()  # 启动定时器，并设置随机时间
        elif gif == self.sk2_gif:  # 如果是漂浮状态
            self.play_sk2_sequence()  # 播放漂浮开场动画
        else:  # 其他状态
            self.idle_timer.stop()  # 停止定时器

        self.current_gif = gif
        self.set_gif(gif)
        self.update_context_menu()

    def switch_to_move(self):
        """切换到移动状态"""
        if self.current_gif == self.relax_gif:  # 只有在站立状态下才切换
            print("切换到移动状态")
            self.current_gif = self.move_gif
            self.set_gif(self.move_gif)

    def play_sk2_sequence(self):
        """播放漂浮序列动画（sk2begin.gif -> sk2.gif）"""
        print("开始播放漂浮开场动画")
        # 停止当前动画
        self.current_gif.stop()

        # 设置并播放 sk2begin.gif
        self.label_pet.setMovie(self.sk2_begin_gif)
        print(f"sk2begin.gif 帧数: {self.sk2_begin_gif.frameCount()}")
        self.sk2_begin_gif.start()

        # 监听帧变化，检测是否到了最后一帧
        self.sk2_begin_gif.frameChanged.connect(self.check_sk2_begin_end)

    def check_sk2_begin_end(self, frame_number):
        """当 sk2begin.gif 播放到最后一帧时，切换到 sk2.gif"""
        if frame_number == self.sk2_begin_gif.frameCount() - 1:
            print("漂浮开场动画播放完成，切换到循环动画")
            self.sk2_begin_gif.stop()  # 停止播放
            self.sk2_begin_gif.frameChanged.disconnect(self.check_sk2_begin_end)  # 取消监听

            # 切换到 sk2.gif 并循环播放
            self.current_gif = self.sk2_gif
            self.set_gif(self.sk2_gif)

    def hide_pet(self):
        """隐藏桌宠，播放 die.gif 后隐藏并重置状态"""
        print("开始播放 die.gif")
        # 停止当前动画
        self.current_gif.stop()

        # 设置并播放 die.gif
        self.label_pet.setMovie(self.die_gif)
        self.die_gif.start()

        # 监听帧变化，检测是否到了最后一帧
        self.die_gif.frameChanged.connect(self.check_die_end)

    def check_die_end(self, frame_number):
        """当 die.gif 播放到最后一帧时，隐藏桌宠并重置状态"""
        if frame_number == self.die_gif.frameCount() - 1:
            print("die.gif 播放完成，隐藏窗口")
            self.die_gif.stop()  # 停止播放
            self.die_gif.frameChanged.disconnect(self.check_die_end)  # 取消监听

            # 隐藏窗口
            self.hide()

            # 重置状态为 relax.gif
            self.current_gif = self.relax_gif
            self.set_gif(self.relax_gif)
    def check_die_end(self, frame_number):
        """当 die.gif 播放到最后一帧时，隐藏桌宠并重置状态"""
        if frame_number == self.die_gif.frameCount() - 1:
            self.die_gif.stop()  # 停止播放
            self.die_gif.frameChanged.disconnect(self.check_die_end)  # 取消监听

            # 隐藏窗口
            self.hide()

            # 重置状态为 relax.gif
            self.current_gif = self.relax_gif
            self.set_gif(self.relax_gif)

    def show_pet(self, reason):
        """从托盘恢复桌宠"""
        if reason == QSystemTrayIcon.Trigger:  # 左键点击托盘图标
            self.show()  # 显示桌宠
            self.set_gif(self.relax_gif)  # 恢复为站立状态

    def mousePressEvent(self, event):
        """鼠标按下时记录位置"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.pos()
            self.last_mouse_pos = event.globalPos()  # 记录初始位置
            self.drag_distance = 0  # 重置拖动距离
            self.drag_start_time = event.timestamp()  # 记录拖动开始时间

    def mouseMoveEvent(self, event):
        """鼠标拖动桌宠"""
        if self.dragging:
            # 计算拖动距离
            current_mouse_pos = event.globalPos()
            self.drag_distance += (current_mouse_pos - self.last_mouse_pos).manhattanLength()
            self.last_mouse_pos = current_mouse_pos

            # 移动桌宠
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        """鼠标释放时判断是否为点击或快速拖动"""
        if event.button() == Qt.LeftButton:
            self.dragging = False

            # 计算拖动速度
            drag_duration = event.timestamp() - self.drag_start_time  # 拖动持续时间（毫秒）
            drag_speed = self.drag_distance / drag_duration if drag_duration > 0 else 0  # 拖动速度（像素/毫秒）

            # 判断是否为快速拖动
            if drag_speed > 5.0:  # 如果拖动速度大于 1.0 像素/毫秒
                self.play_stun_sequence()  # 播放眩晕序列动画
            elif self.current_gif == self.move_gif:  # 如果当前是移动状态
                self.change_state(self.relax_gif, None)  # 切换回站立状态
            elif self.current_gif == self.relax_gif:  # 如果当前是站立状态
                self.play_interact_gif()  # 播放交互动画
            elif self.current_gif == self.sleep_gif:  # 如果当前是睡觉状态
                self.show_sleep_dialog()  # 显示睡觉对话框

    def play_stun_sequence(self):
        """播放眩晕序列动画（stunbegin.gif -> stun.gif）"""
        # 停止当前动画
        self.current_gif.stop()

        # 记录原始状态
        self.original_gif = self.current_gif

        # 设置并播放 stunbegin.gif
        self.label_pet.setMovie(self.stunbegin_gif)
        self.stunbegin_gif.start()

        # 监听帧变化，检测是否到了最后一帧
        self.stunbegin_gif.frameChanged.connect(self.check_stunbegin_end)

    def check_stunbegin_end(self, frame_number):
        """当 stunbegin.gif 播放到最后一帧时，切换到 stun.gif"""
        if frame_number == self.stunbegin_gif.frameCount() - 1:
            self.stunbegin_gif.stop()  # 停止播放
            self.stunbegin_gif.frameChanged.disconnect(self.check_stunbegin_end)  # 取消监听

            # 切换到 stun.gif 并循环播放
            self.current_gif = self.stun_gif
            self.set_gif(self.stun_gif)

            # 启动定时器，4 秒后恢复原始状态
            self.stun_timer = QTimer(self)
            self.stun_timer.timeout.connect(self.restore_original_state)
            self.stun_timer.start(1000)  # 4 秒后恢复


    def restore_original_state(self):
        """恢复原始状态"""
        if hasattr(self, 'original_gif'):
            self.current_gif = self.original_gif
            self.set_gif(self.original_gif)
            self.stun_timer.stop()  # 停止定时器

    def play_interact_gif(self):
        """播放 interact.gif（只播放一次）"""
        # 停止当前动画
        self.current_gif.stop()

        # 设置并播放 interact.gif
        self.label_pet.setMovie(self.interact_gif)
        self.interact_gif.start()

        # 监听帧变化，检测是否到了最后一帧
        self.interact_gif.frameChanged.connect(self.check_interact_end)

    def check_interact_end(self, frame_number):
        """当 interact_gif 播放到最后一帧时，恢复 relax.gif"""
        if frame_number == self.interact_gif.frameCount() - 1:
            self.interact_gif.stop()  # 停止播放
            self.interact_gif.frameChanged.disconnect(self.check_interact_end)  # 取消监听

            # 恢复为 relax.gif
            self.current_gif = self.relax_gif
            self.set_gif(self.relax_gif)

    def hide_pet_with_message(self):
        """隐藏桌宠并显示提示"""
        # 隐藏桌宠
        self.hide_pet()

        # 弹出对话框
        leave_dialog = QMessageBox(self)
        leave_dialog.setWindowTitle("提示")
        leave_dialog.setText("蒂蒂离开了。")
        leave_dialog.exec_()


    def show_sleep_dialog(self):
        """显示睡觉对话框"""
        # 创建对话框
        dialog = QMessageBox(self)
        dialog.setWindowTitle("提示")
        dialog.setText("蒂蒂在睡觉，不要打扰她！")

        # 添加按钮
        ok_button = dialog.addButton("好吧", QMessageBox.AcceptRole)
        disturb_button = dialog.addButton("就要打扰", QMessageBox.RejectRole)

        # 显示对话框
        dialog.exec_()

        # 处理按钮点击事件
        if dialog.clickedButton() == disturb_button:
            # 有 0.4 的概率隐藏桌宠
            if random.random() < 0.4:
                self.hide_pet_with_message()  # 隐藏桌宠并显示提示
            else:
                self.change_state(self.relax_gif, None)  # 切换到站立状态