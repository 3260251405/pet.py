import locale
import os
import shutil
import sys
import random
import time

from configparser import ConfigParser
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from functools import *

config = ConfigParser()
config.read("config.ini")

del_extension = {
    '.tmp': '临时文件',
    '._mp': '临时文件_mp',
    '.log': '日志文件',
    '.gid': '临时帮助文件',
    '.chk': '磁盘检查文件',
    '.old': '临时备份文件',
    '.xlk': 'Excel备份文件',
    '.bak': '临时备份文件bak',
    'null': '空文件'
}


def get_size(b):
    kb = b // 1024
    if kb > 1024:
        mb = kb // 1024
        if mb > 1024:
            gb = mb // 1024
            return "%dG" % gb
        else:
            return "%dM" % mb
    else:
        return "%dKb" % kb


def del_file(root):
    try:
        if os.path.isfile(root):
            os.remove(root)
        elif os.path.isdir(root):
            shutil.rmtree(root)
    except WindowsError:
        print(root, "无法删除")


def open_log():
    QDesktopServices.openUrl(QUrl("log.txt"))
    # os.system("log.txt")


class TablePet(QWidget):
    def __init__(self, x=random.randint(0, 1700), y=random.randint(0, 800), flag=0, name="菜虚坤"):
        super(TablePet, self).__init__()

        self.x = x
        self.y = y
        self.flag = flag
        self.name = name

        self.desktop = QApplication.desktop()

        self.w = 100
        self.h = 100
        self.speed = 10
        self.walkSpeed = 5
        self.direction = 1
        self.frame = 3
        self.action = 1
        self.state = 0
        self.temp = 0
        self.jumps = 0
        self.age = 0

        self.land = self.desktop.height() - self.h
        self.mouse_pos = self.pos()

        self.isWalking = False
        self.isTouching = False
        self.doubleJump = False
        self.isGood = False
        self.isEgg = True

        self.label = QLabel(self)

        self.timer = QTimer(self)
        self.actTimer = QTimer(self)
        self.ageTimer = QTimer(self)

        self.tray()
        self.initView()
        self.show()

    def initView(self):
        self.write_log("鸡哥出生了!")

        self.ageTimer.timeout.connect(self.add_age)
        self.ageTimer.start(60000)
        self.timer.timeout.connect(self.do_action)
        self.timer.start(100)
        self.actTimer.timeout.connect(partial(self.change_state, -2))

        self.get_img()

        self.setGeometry(self.x, self.y, self.w, self.h)
        self.setMaximumSize(self.w, self.h)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def do_action(self):
        if self.isHidden():
            return
        self.check_state()
        self.action_state()
        self.get_img()
        self.move(self.x, self.y)

    def check_state(self):
        match self.state:
            case -1:
                if self.y >= self.land:
                    if self.age >= 5:
                        self.change_state(random.randint(1, 3))
                    else:
                        self.change_state(0)
            case 0:
                if self.y < self.land:
                    self.change_state(-1)
                else:
                    if self.age < 5:
                        self.change_state(0)
                    else:
                        self.change_state(1)
            case 1:
                if self.y < self.land:
                    self.change_state(-1)
            case 2:
                if self.speed >= 0:
                    if self.doubleJump:
                        self.change_state(2)
                    else:
                        self.change_state(-1)
            case 4:
                if self.temp >= 20:
                    self.change_state(random.randint(0, 4))

    def change_state(self, state):
        if self.state == state and not self.doubleJump:
            return
        preState = self.state
        if preState == 1 or preState == 0:
            self.actTimer.stop()
        if state == -2:
            state = random.randint(0, 4)
        self.state = state
        match state:
            case -1:
                if preState == 2:
                    self.isWalking = True
                self.write_log("鸡哥下落中...")
                self.speed = 10
                self.action = 3
                if self.jumps >= 2:
                    self.isGood = True
                self.jumps = 0
            case 0:
                if self.age >= 5:
                    self.actTimer.start(random.randint(2000, 5000))
                else:
                    self.change_state(0)
                self.write_log("思考鸡生中...")
                self.y = self.land
            case 1:
                if self.isGood:
                    self.write_log("鸡哥发出得意的鸡叫")
                    self.play_sound(2)
                    self.isGood = False
                self.isWalking = False
                self.actTimer.start(random.randint(3000, 15000))
                self.speed = 10
                self.y = self.land
                self.action = 1
                self.walkSpeed = random.randint(2, 20)
                self.write_log("鸡哥狂奔中...\t" + "速度为：%d" % self.walkSpeed)
            case 2:
                self.play_sound(3)
                self.speed = random.randint(-50, -20)
                self.jumps += 1
                self.action = 3
                a = random.randint(0, 5)
                if a == 0:
                    self.doubleJump = True
                else:
                    self.doubleJump = False
                if self.jumps <= 1:
                    self.write_log("鸡哥起飞!\t" + "高度为：%d" % abs(self.speed))
                else:
                    self.write_log("鸡哥%d连跳!\t" % self.jumps + "高度为：%d" % abs(self.speed))
            case 3:
                self.change_direction()
                self.y = self.land
                self.change_state(random.randint(0, 2))
            case 4:
                self.write_log("鸡哥拿起了他的麦克风，一展歌喉!")
                self.temp = 0
                self.action = 2
                self.y = self.land
                self.play_sound(0)
        preState = state

    def action_state(self):
        match self.state:
            case -1:
                if self.isTouching:
                    return
                self.speed += 1
                self.y += self.speed
                if self.isWalking:
                    self.land_action()
            case 0:
                self.frame = 3
            case 1:
                self.land_action()
            case 2:
                self.speed += 2
                self.y += self.speed
                self.land_action()
            case 4:
                self.land_action()
                self.temp += 1

    def land_action(self):
        if self.direction == 1:
            self.x -= self.walkSpeed
        else:
            self.x += self.walkSpeed

        if self.x <= 0:
            self.direction = 2
            self.write_log("鸡哥撞到墙了...")
        elif self.x >= self.desktop.width() - self.w:
            self.direction = 1
            self.write_log("鸡哥撞到墙了...")

    def mousePressEvent(self, event, **kwargs):
        if event.button() == Qt.LeftButton:
            self.isTouching = True
            self.mouse_pos = event.globalPos() - self.pos()
            event.accept()
            self.play_sound(1)
            self.setCursor(Qt.OpenHandCursor)
        elif event.button() == Qt.RightButton:
            self.change_direction()

    def mouseMoveEvent(self, event, **kwargs):
        if Qt.LeftButton and self.isTouching:
            self.move(event.globalPos() - self.mouse_pos)
            event.accept()
            xy = self.pos()
            self.x, self.y = xy.x(), xy.y()

    def mouseDoubleClickEvent(self, event, **kwargs):
        self.play_sound(0)

    def mouseReleaseEvent(self, event, **kwargs):
        self.isTouching = False
        self.setCursor(Qt.ArrowCursor)

    def tray(self):
        tp = QSystemTrayIcon(self)
        tp.setIcon(QIcon('pet\\c111.png'))
        tp.setToolTip("桌面宠物 v0.8")

        action_quit = QAction("退出", self, triggered=self.quit)
        self.action_option = QAction("音效", self)
        self.action_option.setCheckable(True)
        self.action_option.setChecked(True)
        action_about = QAction("主菜单", self, triggered=self.main_menu)
        action_log = QAction("日志", self, triggered=open_log)
        action_hide = QAction("隐藏", self, toggled=self.hide_action)
        action_hide.setCheckable(True)
        action_egg = QAction("生蛋", self, toggled=self.set_egg)
        action_egg.setCheckable(True)
        action_egg.setChecked(True)

        menu = QMenu(self)
        subMenu = QMenu(self)
        subMenu.setTitle("设置")
        subMenu.addAction(self.action_option)
        subMenu.addAction(action_hide)
        subMenu.addAction(action_egg)
        menu.addAction(action_log)
        menu.addAction(action_about)
        menu.addMenu(subMenu)
        menu.addSeparator()
        menu.addAction(action_quit)

        tp.setContextMenu(menu)
        tp.activated.connect(partial(self.main_action, action_hide, tp))
        tp.show()

    def get_img(self):
        if self.age < 5:
            picUrl = "pet\\egg.png"
        else:
            picUrl = 'pet\\c' + str(self.direction) + str(self.action) + str(self.frame) + '.png'
        self.label.setGeometry(0, 0, self.w, self.h)
        self.label.setPixmap(QPixmap(picUrl))
        self.label.setScaledContents(True)
        self.frame += 1
        if self.frame > 3:
            self.frame = 1

    def play_sound(self, index):
        sound = QSound
        if not self.action_option.isChecked():
            return
        match index:
            case 0:
                sound.play("pet\\beautiful.wav")
            case 1:
                sound.play("pet\\waht.wav")
            case 2:
                sound.play("pet\\good.wav")
            case 3:
                sound.play("pet\\chicken.wav")

    def change_direction(self):
        if self.direction == 1:
            self.direction = 2
        else:
            self.direction = 1

    def main_action(self, action, tp, flag):
        match flag:
            case 3:
                if self.isHidden():
                    self.hide_action(False)
                    action.setChecked(False)
            case 2:
                tp.showMessage("提醒", "坤坤正在为你清理电脑垃圾，快说谢谢坤坤~")
                self.message_box()

    def hide_action(self, boo):
        if not boo:
            self.show()
        else:
            self.hide()

    def show_about(self, s, size):
        ss = ','
        sp = ss.join(s)

        messageBox = QMessageBox(QMessageBox.Question, "询问",
                                 "坤坤为你扫描出\n%s垃圾文件\n共计%s，是否删除？" % (sp, size))
        yes = messageBox.addButton(self.tr("确定"), QMessageBox.YesRole)
        no = messageBox.addButton(self.tr("取消"), QMessageBox.NoRole)
        messageBox.exec_()
        if messageBox.clickedButton() == yes:
            for path in self.clean.del_file_paths:
                del_file(path)
            messageBox2 = QMessageBox(QMessageBox.Information, "提示", "删除成功!")
            messageBox2.exec_()
        else:
            return

    def quit(self):
        self.write_log("0")
        os.system('%s%s' % ("taskkill /F /IM ", "Notepad.exe"))
        self.close()
        sys.exit(0)

    def closeEvent(self, event, **kwargs):
        event.ignore()

    def write_log(self, s):
        if self.flag == 1:
            return
        locale.setlocale(locale.LC_CTYPE, 'chinese')
        t = time.strftime("%Y年%m月%d日%H时%M分%S秒", time.localtime())
        with open("log.txt", "a+", encoding="utf-8") as f:
            f.write(t + ":\t" + s + "\n")
            if s == "0":
                f.truncate(0)
        # os.remove("log.txt")

    def set_egg(self, boo):
        self.isEgg = boo

    def add_age(self):
        self.age += 1
        self.write_log("菜虚坤%s岁了!" % self.age)
        if self.age % random.randint(7, 11) == 0 and self.isEgg:
            name = config["attr"]["name"]
            names = name.split(" ")
            self.pet = TablePet(self.x, self.y, 1, names[random.randint(0, len(names) - 1)])
            self.write_log("鸽鸽下蛋了!")

    def message_box(self):
        self.clean = diskClean()
        self.clean.to_clean()
        self.show_about(self.clean.show_detail(), get_size(self.clean.totalSize))

    def main_menu(self):
        self.menu = Menu(self)
        self.menu.show()


class diskClean(object):
    def __init__(self):
        self.del_info = {}
        self.del_file_paths = []
        self.totalSize = 0

        for i, j in del_extension.items():
            self.del_info[i] = dict(name=j, count=0)

    def to_clean(self):
        paths = ["D:\\", "C:\\"]
        for path in paths:
            self.scan_dist(path)

    def scan_dist(self, path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_extension = os.path.splitext(file)[1]
                if file_extension in self.del_info:
                    full_path = os.path.join(root, file)
                    self.del_file_paths.append(full_path)
                    self.del_info[file_extension]['count'] += 1
                    self.totalSize += os.path.getsize(full_path)

    def show_detail(self):
        s = []
        for info in self.del_info.values():
            if info['count'] > 0:
                s.append(info['name'] + str(info['count']) + "个")
        return s


class Menu(QWidget):
    def __init__(self, pet):
        super(Menu, self).__init__()
        self.pet = pet
        self.setWindowTitle("桌面宠物-%s v0.8" % pet.name)
        self.resize(500, 500)

        self.message_box()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.box)
        self.setLayout(mainLayout)

    def message_box(self):
        self.box = QGroupBox("主菜单")
        nameLabel = QLabel("姓名:")
        nameLabel2 = QLabel(self.pet.name)
        personLabel = QLabel("性格:")
        ageLabel = QLabel("年龄:")
        ageLabel2 = QLabel(str(self.pet.age) + "岁")
        personComboBox = QComboBox(self)
        personComboBox.addItem('普通')
        personComboBox.addItem('活泼')
        personComboBox.addItem("懒惰")
        personComboBox.setCurrentIndex(0)

        bodyLabel = QLabel("日志:")
        bodyEdit = QTextEdit()
        bodyEdit.setPlainText(config["content"]["log"])
        bodyEdit.setReadOnly(True)

        layout = QGridLayout()
        layout.addWidget(nameLabel, 0, 0)
        layout.addWidget(nameLabel2, 0, 1)
        layout.addWidget(ageLabel, 1, 0)
        layout.addWidget(ageLabel2, 1, 1)
        layout.addWidget(personLabel, 2, 0)
        layout.addWidget(personComboBox, 2, 1)
        layout.addWidget(bodyLabel, 3, 0)
        layout.addWidget(bodyEdit, 3, 1, 1, 3)
        layout.setColumnStretch(3, 1)
        layout.setRowStretch(3, 1)
        self.box.setLayout(layout)

    def closeEvent(self, a0, **kwargs):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myPet = TablePet()
    sys.exit(app.exec_())
