import sys
sys.path.append("/usr/lib/python3/dist-packages")#添加PyQt5运行路径，我的旭日派使用。正常其他板子注释即可。
import cv2
import time
import numpy as np
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, Qt, QRect
from PyQt5.QtGui import QImage, QPixmap, QPainter, QBrush, QColor, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QGridLayout

shared_data = [0] * 9
# 每个小格子的状态出现次数
state_counts = {i: {0: 0, 1: 0, 2: 0} for i in range(9)}

# 记录检测次数
detection_count = 0
max_detection = 10

class VideoWindow(QWidget):
    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)

        # 创建 ChessboardWidget 实例
        # self.chessboard_widget = ChessboardWidget()

        self.top_left = (0, 0)
        self.top_right = (0, 0)
        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)


        self.video_size = (640, 480)
        self.video_label = QLabel()
        self.video_label.setGeometry(50, 50, 640, 480)  # 设置视频显示区域的位置和大小
        # 设置视频对其方式为居中靠上
        self.video_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # 创建一个标签来显示图片11号
        self.image_size = (640, 480)
        self.image_label = QLabel()
        self.image_label.setGeometry(50, 600, 400, 400)  # 设置图片显示区域的位置和大小


        # 创建一个标签来显示图片
        self.image_11_size = (400, 400)
        self.image_11_label = QLabel()
        self.image_11_label.setGeometry(600, 600, 400, 400)  # 设置图片显示区域的位置和大小


        self.switch_button_1 = QPushButton("棋手已下完")
        # 按钮触发事件
        self.switch_button_1.clicked.connect(self.switch_button_1_clicked)# 后面再写逻辑

        # 按钮上写着“切换执棋手”
        self.switch_button = QPushButton("切换执棋手")
        # 按钮触发事件
        self.switch_button.clicked.connect(self.switch_button_clicked)




        # 创建 9 个按钮，用于初始调试用
        # 9个按钮上的文字设置为“空”
        self.square_button_0 = QPushButton("空")
        self.square_button_1 = QPushButton("空")
        self.square_button_2 = QPushButton("空")
        self.square_button_3 = QPushButton("空")
        self.square_button_4 = QPushButton("空")
        self.square_button_5 = QPushButton("空")
        self.square_button_6 = QPushButton("空")
        self.square_button_7 = QPushButton("空")
        self.square_button_8 = QPushButton("空")

        self.square_button_save = QPushButton("未存")
        self.square_button_simulation = QPushButton("系统已落子")

        # 按钮触发事件，用于数字更换
        self.square_button_0.clicked.connect(self.square_button_0_clicked)# 1号格子按下后
        self.square_button_1.clicked.connect(self.square_button_1_clicked)# 2号格子按下后
        self.square_button_2.clicked.connect(self.square_button_2_clicked)# 3号格子按下后
        self.square_button_3.clicked.connect(self.square_button_3_clicked)# 4号格子按下后
        self.square_button_4.clicked.connect(self.square_button_4_clicked)# 5号格子按下后
        self.square_button_5.clicked.connect(self.square_button_5_clicked)# 6号格子按下后
        self.square_button_6.clicked.connect(self.square_button_6_clicked)# 7号格子按下后
        self.square_button_7.clicked.connect(self.square_button_7_clicked)# 8号格子按下后
        self.square_button_8.clicked.connect(self.square_button_8_clicked)# 9号格子按下后

        self.square_button_save.clicked.connect(self.square_button_save_clicked)# 保存阈值按下后
        self.square_button_simulation.clicked.connect(self.square_button_simulation_clicked)# 系统已落子按下后

        # 创建一个文本标签在按钮下方
        self.text_label = QLabel()
        # 文本内容设置为“系统执黑棋”
        self.text_label.setText("系统执黑棋")
        # 设置文本标签的对齐方式为水平居中
        self.text_label.setAlignment(Qt.AlignHCenter)
        # 设置文本标签的字体大小为28号
        self.text_label.setFont(QFont(self.text_label.font().family(), 28))
        # 设置文本标签的背景颜色
        self.text_label.setAutoFillBackground(True)

        # 创建一个文本标签在按钮下方
        self.text_label_dowm_state = QLabel()
        # 文本内容设置为“系统执黑棋”
        self.text_label_dowm_state.setText("等待下棋")
        # 设置文本标签的对齐方式为水平居中
        self.text_label_dowm_state.setAlignment(Qt.AlignHCenter)
        # 设置文本标签的字体大小为25号
        self.text_label_dowm_state.setFont(QFont(self.text_label_dowm_state.font().family(), 25))
        # 设置文本标签的背景颜色
        self.text_label_dowm_state.setAutoFillBackground(True)


        # 创建一个文本标签在按钮下方
        self.text_label_cheat_state = QLabel()
        # 文本内容设置为“系统执黑棋”
        self.text_label_cheat_state.setText("无作弊")
        # 设置文本标签的对齐方式为水平居中
        self.text_label_cheat_state.setAlignment(Qt.AlignHCenter)
        # 设置文本标签的字体大小为25号
        self.text_label_cheat_state.setFont(QFont(self.text_label_cheat_state.font().family(), 25))
        # 设置文本标签的背景颜色
        self.text_label_cheat_state.setAutoFillBackground(True)


        # 9个按钮上面的调试文本
        self.text_label_5 = QLabel()
        # 文本内容设置为“系统执黑棋”
        self.text_label_5.setText("当前剩余_颗黑棋 _颗白棋")
        # 设置文本标签的对齐方式为水平居中
        self.text_label_5.setAlignment(Qt.AlignHCenter)
        # 设置文本标签的字体大小为20号
        self.text_label_5.setFont(QFont(self.text_label_5.font().family(), 20))
        # 设置文本标签的背景颜色
        self.text_label_5.setAutoFillBackground(True)

        # 创建一个文本标签在按钮下方
        self.text_label_1 = QLabel()
        # 文本内容设置为“系统执黑棋”
        self.text_label_1.setText("胜利者：暂无")
        # 设置文本标签的对齐方式为水平居中
        self.text_label_1.setAlignment(Qt.AlignHCenter)
        # 设置文本标签的字体大小为30号
        self.text_label_1.setFont(QFont(self.text_label_1.font().family(), 30))
        # 设置文本标签的背景颜色
        self.text_label_1.setAutoFillBackground(True)



        # 创建一个文本标签在按钮下方
        self.text_label_2 = QLabel()
        # 文本内容设置为“系统执黑棋”
        self.text_label_2.setText("系统决定下第_位")
        # 设置文本标签的对齐方式为水平居中
        self.text_label_2.setAlignment(Qt.AlignHCenter)
        # 设置文本标签的字体大小为32号
        self.text_label_2.setFont(QFont(self.text_label_2.font().family(), 32))
        # 设置文本标签的背景颜色
        self.text_label_2.setAutoFillBackground(True)

        # 创建一个文本标签在按钮下方 结束语
        self.text_label_3 = QLabel()
        # 文本内容设置为“系统执黑棋”
        self.text_label_3.setText("火焰！听从我！")
        # 设置文本标签的对齐方式为水平居中
        self.text_label_3.setAlignment(Qt.AlignHCenter)
        # 设置文本标签的字体大小为34号
        self.text_label_3.setFont(QFont(self.text_label_3.font().family(), 34))
        # 设置文本标签的背景颜色
        self.text_label_3.setAutoFillBackground(True)



        # 设置按钮的格式
        # 设置切换按钮的大小
        self.switch_button.setFixedSize(200, 50)
        # 设置按钮的字体大小为20号
        self.switch_button.setFont(QFont(self.switch_button.font().family(), 20))
        # 设置按钮的背景颜色
        self.switch_button.setAutoFillBackground(True)
        # 设置选手已下完的大小
        self.switch_button_1.setFixedSize(200, 50)
        # 设置按钮的字体大小为20号
        self.switch_button_1.setFont(QFont(self.switch_button.font().family(), 20))
        # 设置按钮的背景颜色
        self.switch_button_1.setAutoFillBackground(True)


        # 9个按钮上面的调试文本
        self.text_label_4 = QLabel()
        # 文本内容设置为“系统执黑棋”
        self.text_label_4.setText("使用前请调试")
        # 设置文本标签的对齐方式为水平居中
        self.text_label_4.setAlignment(Qt.AlignHCenter)
        # 设置文本标签的字体大小为20号
        self.text_label_4.setFont(QFont(self.text_label_4.font().family(), 20))
        # 设置文本标签的背景颜色
        self.text_label_4.setAutoFillBackground(True)


        # 设置9个按钮的格式
        # 1号按钮
        self.square_button_0.setFixedSize(60, 60)
        # 设置按钮的字体大小为20号
        self.square_button_0.setFont(QFont(self.square_button_0.font().family(), 20))
        # 设置按钮的背景颜色
        self.square_button_0.setAutoFillBackground(True)

        # 2号按钮
        self.square_button_1.setFixedSize(60, 60)
        # 设置按钮的字体大小为20号
        self.square_button_1.setFont(QFont(self.square_button_1.font().family(), 20))
        # 设置按钮的背景颜色
        self.square_button_1.setAutoFillBackground(True)

        # 3号按钮
        self.square_button_2.setFixedSize(60, 60)
        # 设置按钮的字体大小为20号
        self.square_button_2.setFont(QFont(self.square_button_2.font().family(), 20))
        # 设置按钮的背景颜色
        self.square_button_2.setAutoFillBackground(True)

        # 4号按钮
        self.square_button_3.setFixedSize(60, 60)
        # 设置按钮的字体大小为20号
        self.square_button_3.setFont(QFont(self.square_button_3.font().family(), 20))
        # 设置按钮的背景颜色
        self.square_button_3.setAutoFillBackground(True)

        # 5号按钮
        self.square_button_4.setFixedSize(60, 60)
        # 设置按钮的字体大小为20号
        self.square_button_4.setFont(QFont(self.square_button_4.font().family(), 20))
        # 设置按钮的背景颜色
        self.square_button_4.setAutoFillBackground(True)

        # 6号按钮
        self.square_button_5.setFixedSize(60, 60)
        # 设置按钮的字体大小为20号
        self.square_button_5.setFont(QFont(self.square_button_5.font().family(), 20))
        # 设置按钮的背景颜色
        self.square_button_5.setAutoFillBackground(True)

        # 7号按钮
        self.square_button_6.setFixedSize(60, 60)
        # 设置按钮的字体大小为20号
        self.square_button_6.setFont(QFont(self.square_button_6.font().family(), 20))
        # 设置按钮的背景颜色
        self.square_button_6.setAutoFillBackground(True)

        # 8号按钮
        self.square_button_7.setFixedSize(60, 60)
        # 设置按钮的字体大小为20号
        self.square_button_7.setFont(QFont(self.square_button_7.font().family(), 20))
        # 设置按钮的背景颜色
        self.square_button_7.setAutoFillBackground(True)

        # 9号按钮
        self.square_button_8.setFixedSize(60, 60)
        # 设置按钮的字体大小为20号
        self.square_button_8.setFont(QFont(self.square_button_8.font().family(), 20))
        # 设置按钮的背景颜色
        self.square_button_8.setAutoFillBackground(True)

        # 保存按钮
        self.square_button_save.setFixedSize(100, 60)
        # 设置按钮的字体大小为20号
        self.square_button_save.setFont(QFont(self.square_button_save.font().family(), 20))
        # 设置按钮的背景颜色
        self.square_button_save.setAutoFillBackground(True)

        # 模拟落子按钮
        self.square_button_simulation.setFixedSize(250, 60)
        # 设置按钮的字体大小为20号
        self.square_button_simulation.setFont(QFont(self.square_button_simulation.font().family(), 20))
        # 设置按钮的背景颜色
        self.square_button_simulation.setAutoFillBackground(True)


        # 把摄像头图像，11号图像依次从上往下排放，为第一个大块
        self.VD_Box = QVBoxLayout()
        self.VD_Box.addWidget(self.video_label)
        self.VD_Box.addWidget(self.image_11_label)


        # 排列9个按钮,第一排3个，第二排3个，第三排3个
        self.Button_chess_0 = QHBoxLayout()
        self.Button_chess_0.addWidget(self.square_button_0)
        self.Button_chess_0.addWidget(self.square_button_1)
        self.Button_chess_0.addWidget(self.square_button_2)

        self.Button_chess_1 = QHBoxLayout()
        self.Button_chess_1.addWidget(self.square_button_3)
        self.Button_chess_1.addWidget(self.square_button_4)
        self.Button_chess_1.addWidget(self.square_button_5)

        self.Button_chess_2 = QHBoxLayout()
        self.Button_chess_2.addWidget(self.square_button_6)
        self.Button_chess_2.addWidget(self.square_button_7)
        self.Button_chess_2.addWidget(self.square_button_8)





        # 三排按钮放在一起
        self.Button_chess_jin = QVBoxLayout()
        self.Button_chess_jin.addWidget(self.text_label_4)
        self.Button_chess_jin.addWidget(self.square_button_save)
        self.Button_chess_jin.addWidget(self.square_button_simulation)
        self.Button_chess_jin.addLayout(self.Button_chess_0)
        self.Button_chess_jin.addLayout(self.Button_chess_1)
        self.Button_chess_jin.addLayout(self.Button_chess_2)

        # 设置检测棋盘和调试棋盘放一起
        self.chess_Box = QHBoxLayout()
        self.chess_Box.addWidget(self.image_label)
        self.chess_Box.addLayout(self.Button_chess_jin)

        #  切换执旗手和告知已经下完的按钮，两个按钮并排放
        self.switchBox = QHBoxLayout()
        self.switchBox.addWidget(self.switch_button)
        self.switchBox.addWidget(self.switch_button_1)

        # 等待下棋和作弊状态并排显示
        self.wait_and_cheat = QHBoxLayout()
        self.wait_and_cheat.addWidget(self.text_label_dowm_state)
        self.wait_and_cheat.addWidget(self.text_label_cheat_state)

        # 右边半块从上往下排好，把棋盘图，双按钮，4个显示文本依次从上往下排放
        self.ButtonBox = QVBoxLayout()
        self.ButtonBox.addLayout(self.chess_Box)
        self.ButtonBox.addLayout(self.switchBox)
        self.ButtonBox.addWidget(self.text_label)
        self.ButtonBox.addLayout(self.wait_and_cheat)
        self.ButtonBox.addWidget(self.text_label_5)
        self.ButtonBox.addWidget(self.text_label_1)
        self.ButtonBox.addWidget(self.text_label_2)
        self.ButtonBox.addWidget(self.text_label_3)


        # 把左半块，右半块等三个大块依次从左往右排
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.VD_Box)
        self.layout.addLayout(self.ButtonBox)


        # 显示整个界面
        self.setLayout(self.layout)
        # 设置界面标题
        self.setWindowTitle('三子棋')
        # 设置界面大小
        self.setGeometry(100, 100, 1000, 1000)

        # 在视频右侧，多加载一张图片
        # 加载图片
        # 加载图片


            # 加载并设置图片
        pixmap1 = QPixmap('/home/sunrise/YOLOv10/try/YOLOv10/ImageTransfer/jiuge.jpg')  # 替换为你的图片路径
        self.image_label.setPixmap(pixmap1.scaled(400, 400, Qt.KeepAspectRatio))

        pixmap1 = QPixmap('/home/sunrise/YOLOv10/try/YOLOv10/ImageTransfer/11号.jpg')  # 替换为你的图片路径
        self.image_11_label.setPixmap(pixmap1.scaled(640, 480, Qt.KeepAspectRatio))

        self.capture = cv2.VideoCapture(8)  # 根据需要调整摄像头索引，我的旭日派是8，其他树莓派应该默认是0
        if not self.capture.isOpened():
            exit(-1)
        print("成功打开USB摄像头")

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # 图像处理函数运行
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000 / 60))  # 以整数值开始定时器



        # 初始化棋子的中心坐标列表
        self.white_pieces = []
        self.black_pieces = []

        # 初始化用于滑动窗口的列表
        self.white_window = [0] * 10  # 这里10可以根据需要调整窗口大小
        self.black_window = [0] * 10  # 这里10可以根据需要调整窗口大小

        # 静态阈值范围 (BGR)（黑白棋的阈值可根据需要自己调试，范围越大，越容易识别圆形棋子。
        self.white_lower = np.array([127, 127, 127])  # 调整为适合你的阈值范围，此处可调
        self.white_upper = np.array([255, 255, 255])  # 调整为适合你的阈值范围，此处不调
        self.black_lower = np.array([0, 0, 0])  # 调整为适合你的阈值范围，此处不调
        self.black_upper = np.array([126, 126, 126])  # 调整为适合你的阈值范围，此处可调

        self.find_rect = 0 # 是否找到矩形的标志位
        self.jiugongge = [0] * 9 # 九宫格的棋子编号, 0表示无棋子，1表示白棋，2表示黑棋
        self.temp_jiugongge = [0] * 9 # 判断人是否作弊的上一局对照棋盘
        self.radius_tolerance = 10  # 去重时设定的半径偏差，偏差范围内的圆形将被视为同一个圆形
        self.radius_average = 0 # 去重时计算的圆形半径平均值
        self.aver_door = 0 # 去重时计算的圆形半径平均值的门锁
        #用完后重置参数
        self.radius_sum = 0
        self.circle_count = 0
        self.consecutive_no_piece_counts = [0] * 9  # 初始化为长度为9，每个元素为0的列表

        # 初始化
        self.weizhi = [(0, 0)] * 9

        self.time_loop = 0

        # 设置具体的画棋子坐标
        self.weizhi = [(36, 36), (170, 30), (303, 36),
                    (36, 170), (170, 170), (303, 170),
                    (36, 303), (170, 303), (303, 303)]
                    # 定义黑色和白色的 HSV 范围
        self.lower_black_hsv = np.array([0, 0, 150])
        self.upper_black_hsv = np.array([180, 255, 256])


        self.state = [0] * 9  # 九宫格初始状态全为0
        self.counter = [0] * 9  # 计数器，用于记录连续检测的次数


        # 计算每个内接圆的颜色平均值
        self.average_colors = []


        # 执棋子手标志位, 1表示系统执黑棋，2表示系统执白棋
        self.zhixing = 1
        # 下一步，棋子要走的位置
        self.move = 0
        # 赢家是谁，系统黑，对手白，1表示系统赢，2表示对手赢，反之同理。0表示平局，-1表示未结束
        self.winner = -1

        # 先手标志位,1为系统，2为对手
        self.no_1 = 1 if self.zhixing == 1 else 2  # 先手标志位

        self.test_jiugongge = [0] * 9 # 九宫格的棋子编号, 0表示无棋子，1表示白棋，2表示黑棋

        self.save_yuzhi = 0

        self.black_max_value_1 = 0
        self.black_max_value_2 = 0
        self.white_min_value_1 = 0
        self.white_min_value_2 = 0
        self.people_move = 0 # 对手是否已经落子
        self.system_move = 0 # 系统是否已经落子
        self.cheat_flag = 0 # 作弊标志位

        # 获取开始时的时钟周期数
        self.start_ticks = cv2.getTickCount()

    def switch_button_clicked(self, event):
        self.zhixing = 1 if self.zhixing == 2 else 2
        self.no_1 = 1 if self.zhixing == 1 else 2
        print(f"切换执棋手为{self.zhixing}")
        if self.zhixing == 1:
            self.text_label.setText("系统执黑棋")
        else:
            self.text_label.setText("系统执白棋")

    def switch_button_1_clicked(self, event):
        self.people_move = 1
        self.system_move = 0
        # 判断self.temp_jiugongself.jiugonggege有1的部分是否相同，如果不同，则提示有作弊，如果相同，则提示未作弊
        if self.zhixing == 1:
            if self.temp_jiugongge != [1 if i == 1 else 0 for i in self.jiugongge]:
                self.text_label_cheat_state.setText("有作弊")
                self.cheat_flag = 1
            else:
                self.text_label_cheat_state.setText("无作弊")
                self.cheat_flag = 0
        # 如果为2，则判断self.temp_jiugongge有2的部分是否相同，如果不同，则提示有作弊，如果相同，则提示未作弊
        else:
            if self.temp_jiugongge != [1 if i == 2 else 0 for i in self.jiugongge]:
                self.text_label_cheat_state.setText("有作弊")
            else:
                self.text_label_cheat_state.setText("无作弊")




    def square_button_simulation_clicked(self, event):
        self.system_move = 1
        self.people_move = 0
        # 系统下完棋后保存当前的棋盘状态，以便在对手下完棋后进行比对判断是否作弊
        # 更新装置自己下的棋盘状态
        if (self.zhixing == 1):
            # 将self.jiugongge数组中判断为1的部分填入self.temp_jiugongge数组
            self.temp_jiugongge = [1 if i == 1 else 0 for i in self.jiugongge]
        else :
            # 将self.jiugongge数组中判断为2的部分填入self.temp_jiugongge数组
            self.temp_jiugongge = [1 if i == 2 else 0 for i in self.jiugongge]

    def square_button_0_clicked(self, event):
        # 如果self.test_jiugongge[0]为0，则变1，如果为1，则变2，如果为2，则变0
        self.test_jiugongge[0] = (self.test_jiugongge[0] + 1) % 3
        # 更新按钮上的文字
        if self.test_jiugongge[0] == 0:
            self.square_button_0.setText("空")
        elif self.test_jiugongge[0] == 1:
            self.square_button_0.setText("黑")
        else:
            self.square_button_0.setText("白")


    def square_button_1_clicked(self, event):
        # 如果self.test_jiugongge[1]为0，则变1，如果为1，则变2，如果为2，则变0
        self.test_jiugongge[1] = (self.test_jiugongge[1] + 1) % 3
        # 更新按钮上的文字
        if self.test_jiugongge[1] == 0:
            self.square_button_1.setText("空")
        elif self.test_jiugongge[1] == 1:
            self.square_button_1.setText("黑")
        else:
            self.square_button_1.setText("白")

    def square_button_2_clicked(self, event):
        # 如果self.test_jiugongge[2]为0，则变1，如果为1，则变2，如果为2，则变0
        self.test_jiugongge[2] = (self.test_jiugongge[2] + 1) % 3
        # 更新按钮上的文字
        if self.test_jiugongge[2] == 0:
            self.square_button_2.setText("空")
        elif self.test_jiugongge[2] == 1:
            self.square_button_2.setText("黑")
        else:
            self.square_button_2.setText("白")


    def square_button_3_clicked(self, event):
        # 如果self.test_jiugongge[3]为0，则变1，如果为1，则变2，如果为2，则变0
        self.test_jiugongge[3] = (self.test_jiugongge[3] + 1) % 3
        # 更新按钮上的文字
        if self.test_jiugongge[3] == 0:
            self.square_button_3.setText("空")
        elif self.test_jiugongge[3] == 1:
            self.square_button_3.setText("黑")
        else:
            self.square_button_3.setText("白")

    def square_button_4_clicked(self, event):
        # 如果self.test_jiugongge[4]为0，则变1，如果为1，则变2，如果为2，则变0
        self.test_jiugongge[4] = (self.test_jiugongge[4] + 1) % 3
        # 更新按钮上的文字
        if self.test_jiugongge[4] == 0:
            self.square_button_4.setText("空")
        elif self.test_jiugongge[4] == 1:
            self.square_button_4.setText("黑")
        else:
            self.square_button_4.setText("白")

    def square_button_5_clicked(self, event):
        # 如果self.test_jiugongge[5]为0，则变1，如果为1，则变2，如果为2，则变0
        self.test_jiugongge[5] = (self.test_jiugongge[5] + 1) % 3
        # 更新按钮上的文字
        if self.test_jiugongge[5] == 0:
            self.square_button_5.setText("空")
        elif self.test_jiugongge[5] == 1:
            self.square_button_5.setText("黑")
        else:
            self.square_button_5.setText("白")

    def square_button_6_clicked(self, event):
        # 如果self.test_jiugongge[6]为0，则变1，如果为1，则变2，如果为2，则变0
        self.test_jiugongge[6] = (self.test_jiugongge[6] + 1) % 3
        # 更新按钮上的文字
        if self.test_jiugongge[6] == 0:
            self.square_button_6.setText("空")
        elif self.test_jiugongge[6] == 1:
            self.square_button_6.setText("黑")
        else:
            self.square_button_6.setText("白")


    def square_button_7_clicked(self, event):
        # 如果self.test_jiugongge[7]为0，则变1，如果为1，则变2，如果为2，则变0
        self.test_jiugongge[7] = (self.test_jiugongge[7] + 1) % 3
        # 更新按钮上的文字
        if self.test_jiugongge[7] == 0:
            self.square_button_7.setText("空")
        elif self.test_jiugongge[7] == 1:
            self.square_button_7.setText("黑")
        else:
            self.square_button_7.setText("白")

    def square_button_8_clicked(self, event):
        # 如果self.test_jiugongge[8]为0，则变1，如果为1，则变2，如果为2，则变0
        self.test_jiugongge[8] = (self.test_jiugongge[8] + 1) % 3
        # 更新按钮上的文字
        if self.test_jiugongge[8] == 0:
            self.square_button_8.setText("空")
        elif self.test_jiugongge[8] == 1:
            self.square_button_8.setText("黑")
        else:
            self.square_button_8.setText("白")

    def square_button_save_clicked(self, event):
        # 对self.save_yuzhi进行判断，如果为0，则变1，如果为1，则变0
        self.save_yuzhi = (self.save_yuzhi + 1) % 2
        # 显示当前状态，0表示未保存，1表示已保存
        if self.save_yuzhi == 0:
            self.square_button_save.setText("未存")
        else:
            self.square_button_save.setText("已存")


    def update_state_probabilistically(self, jiugongge):
        global state_counts, detection_count

        # 更新每个小格子的状态出现次数
        for i in range(9):
            state_counts[i][jiugongge[i]] += 1

        detection_count += 1

        if detection_count >= max_detection:
            new_state = []

            for i in range(9):
                counts = state_counts[i]

                # 计算各状态的概率
                total_counts = sum(counts.values())
                if total_counts == 0:
                    # 如果没有足够的数据，保持当前状态
                    new_state_value = jiugongge[i]
                else:
                    probabilities = {state: count / total_counts for state, count in counts.items()}

                    # 调整概率分布，提高黑棋和白棋的识别率
                    adjusted_probabilities = {
                        0: probabilities.get(0, 0) * 1, # 无棋的识别率
                        1: probabilities.get(1, 0) * 1, # 提高黑棋的识别率
                        2: probabilities.get(2, 0) * 1   # 保持灰色棋子的概率，此处1可以修改权重比
                    }

                    # 重新归一化概率
                    total_adjusted = sum(adjusted_probabilities.values())
                    for state in adjusted_probabilities:
                        adjusted_probabilities[state] /= total_adjusted

                    # 选择概率最高的状态
                    new_state_value = max(adjusted_probabilities, key=adjusted_probabilities.get)

                new_state.append(new_state_value)

            # 更新 jiugongge 变量
            jiugongge[:] = new_state

            # 重置计数器
            state_counts = {i: {0: 0, 1: 0, 2: 0} for i in range(9)}
            detection_count = 0

            return jiugongge
        else:
            return jiugongge


    def distance_fl64(self, point1, point2):
        # 将坐标转换为浮点数
        point1 = np.array(point1, dtype=np.float64)
        point2 = np.array(point2, dtype=np.float64)
        return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

    def distance(self, point1, point2):
        return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

    # def is_point_inside_convex_polygon(self, point, polygon_points):
    #     # 将多边形顶点转换为numpy数组
    #     polygon = np.array([[p[0], p[1]] for p in polygon_points], dtype=np.int32)

    #     # 使用cv2.pointPolygonTest检测点是否在凸多边形内部
    #     # 返回值大于等于0表示点在多边形内部，-1表示在外部，-2表示在边界上
    #     return cv2.pointPolygonTest(polygon, point, False) >= 0

    def is_point_inside_rotated_rectangle(self, point, rect_center, rect_angle, rect_width, rect_height):
        # 将矩形还原到原始状态
        rotation_matrix = np.array([[np.cos(rect_angle), -np.sin(rect_angle)],
                                    [np.sin(rect_angle), np.cos(rect_angle)]])
        inv_rotation_matrix = np.linalg.inv(rotation_matrix)

        # 计算四个顶点在旋转后的位置
        rect_points = np.array([
            [-rect_width / 2, -rect_height / 2],
            [rect_width / 2, -rect_height / 2],
            [rect_width / 2, rect_height / 2],
            [-rect_width / 2, rect_height / 2]
        ])
        rect_points = np.dot(rect_points, rotation_matrix.T) + rect_center

        # 计算点到每条边的距离
        distances = []
        for i in range(4):
            next_point = rect_points[(i + 1) % 4]
            side_vector = next_point - rect_points[i]
            point_vector = point - rect_points[i]
            side_length = np.linalg.norm(side_vector)
            # 使用叉乘计算点到边的距离
            cross_product = abs(np.cross(side_vector, point_vector)) / side_length
            distances.append(cross_product)

        # 如果点到所有边的距离都小于0.5个像素，则认为点在矩形内部
        if all(distance < 0.5 for distance in distances):
            return True
        else:
            return False

    def calculate_probability(self, number):
        # 在这里实现你的概率计算逻辑
        # 这只是一个示例，你需要根据你的需求来修改它
        probability = number / 100  # 假设概率是number除以100
        return probability





    def update_frame(self):

        ret, frame = self.capture.read()
        if ret:

            # # 记录开始时间
            # start_time = time.time()

            if self.people_move == 1 and self.system_move == 0 and self.winner == -1:
                # 人已经落子，系统还未落子
                self.text_label_dowm_state.setText("等待系统落子...")
            elif self.people_move == 0 and self.system_move == 1 and self.winner == -1:
                self.text_label_dowm_state.setText("等待对手落子...")
            else:
                self.text_label_dowm_state.setText("当前游戏结束")



            blurred = cv2.GaussianBlur(frame, (5, 5), 0) # 高斯模糊

            kernel = np.ones((5, 5), np.uint8) # 5*5的卷积核
            opened = cv2.morphologyEx(blurred, cv2.MORPH_OPEN, kernel) # 开运算
            # cv2.imshow("opened", opened) #测试处理后图片



            # 转换为灰度图像
            gray = cv2.cvtColor(opened, cv2.COLOR_BGR2GRAY)
            # cv2.imshow('gray', gray) # 测试灰度图像
            hsv = cv2.cvtColor(opened, cv2.COLOR_BGR2HSV)



            # lower_white_hsv = np.array([0, 0, 200])
            # upper_white_hsv = np.array([180, 55, 255])

            # # 找到黑色和白色的区域
            # black_mask_hsv = cv2.inRange(hsv, self.lower_black_hsv, self.upper_black_hsv)
            # white_mask_hsv = cv2.inRange(hsv, lower_white_hsv, upper_white_hsv)

            # # 将黑色和白色的区域从原始图像中分离出来
            # black_pieces_hsv = cv2.bitwise_and(frame, frame, mask=black_mask_hsv)
            # white_pieces_hsv = cv2.bitwise_and(frame, frame, mask=white_mask_hsv)

            # cv2.imshow('Black pieces', black_pieces_hsv)
            # cv2.imshow('White pieces', white_pieces_hsv)

            # self.lower_black_hsv[0] += 1
            # self.upper_black_hsv[1] -= 1

            # print(f"HSV的S{self.upper_black_hsv[1]}")

            # 取图像的中间部分
            height, width = gray.shape
            left = width // 8
            right = width * 7 // 8
            gray = gray[:, left:right]

            hsv = hsv[:, left:right]

            # 在原图上画出切割的区域
            cv2.rectangle(frame, (left, 0), (right, height), (255, 0, 0), 2)

            # 使用Canny边缘检测
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            # cv2.imshow('edges', edges) # 测试边缘检测
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


            # 寻找面积最大的轮廓
            max_area = 0
            largest_contour = None
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > max_area:
                    max_area = area
                    largest_contour = contour

            # 处理找到的最大轮廓
            if largest_contour is not None:
                # 计算轮廓的边界框
                x, y, w, h = cv2.boundingRect(largest_contour)

                # 如果边界框的面积大于一定值，那么就认为它是一个大的矩形
                if w * h > 40000:  # 测试出来基本4万以上就很稳了，可自行调节
                    # 加上偏移量
                    x += left

                    # 画出当前矩形
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    self.find_rect = 1 # 找到矩形了

                    # 获取旋转矩形的中心点坐标、宽高和旋转角度
                    rect = cv2.minAreaRect(largest_contour)
                    # 获取旋转矩形的四个角点
                    box = cv2.boxPoints(rect)

                    # 将角点坐标转换为整数
                    box = np.intp(box)
                    # 给每个角点的x坐标加上偏移量
                    box[:, 0] += left

                    # 计算四个角点的中心点
                    center_points = np.mean(box, axis=0)

                    # 对四个顶点进行排序，从左到右，从上到下
                    sorted_box = sorted(box, key=lambda p: (p[1], p[0]))
                    # sorted_box = box

                    # 通过中心点坐标的排序
                    top_left = min(sorted_box, key=lambda p: p[0] + p[1])
                    bottom_right = max(sorted_box, key=lambda p: p[0] + p[1])
                    top_right = min(sorted_box, key=lambda p: p[0] - p[1])
                    bottom_left = max(sorted_box, key=lambda p: p[0] - p[1])

                    # 计算左上角到中心点的距离
                    self.xiao_xiebian_half = np.linalg.norm(center_points - top_left) / 3
                    # 计算矩形边长的一半
                    self.bianchang_half = np.linalg.norm(top_right - top_left) / 6
                    # 计算小正方形的边长
                    self.square_size = self.bianchang_half * 2
                    # 后面用的内接圆半径
                    self.neijie_radius = self.square_size // 2


                    sorted_box = [top_left, top_right, bottom_right, bottom_left]

                    # 重新计算四个顶点的坐标
                    self.top_left = tuple(sorted_box[0])
                    self.top_right = tuple(sorted_box[1])
                    self.bottom_right = tuple(sorted_box[2])
                    self.bottom_left = tuple(sorted_box[3])

                    # 计算大矩形的旋转角度
                    self.angle = np.arctan2(self.bottom_right[1] - self.top_right[1], self.bottom_right[0] - self.top_right[0])
                    self.jiaodu = self.angle * 180 / np.pi
                    # print(f"旋转角度: {jiaodu:.2f}")
                    # 创建旋转矩阵
                    rotation_matrix = np.array([[np.cos(self.angle), -np.sin(self.angle)], [np.sin(self.angle), np.cos(self.angle)]])

                    # 初始化一个列表用于存储小正方形的中心点坐标和编号
                    self.squares_center = []
                    # 初始化一个列表用于存储小正方形的四个顶点坐标
                    self.square_points = []

                    # 计算大矩形的中心点
                    self.center_big_square = np.array([(self.top_left[0] + self.bottom_right[0]) / 2, (self.top_left[1] + self.bottom_right[1]) / 2])

                    # 确保 self.royal_rect_points 是一个 NumPy 数组

                    self.royal_rect_points = np.array([self.top_left, self.top_right, self.bottom_right, self.bottom_left], dtype=np.int32)
                    self.royal_rect_points = self.royal_rect_points.reshape((-1, 1, 2))

                    # 计算旋转矩阵的宽度和高度
                    self.width = max(self.distance(self.top_left, self.top_right), self.distance(self.bottom_left, self.bottom_right))
                    self.height = max(self.distance(self.top_left, self.bottom_left), self.distance(self.top_right, self.bottom_right))

                    #绘制出当前矩形
                    cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)
                    # 定义顺序，最左上角开始编号
                    square_order = [
                        (0, 0), (0, 1), (0, 2),
                        (1, 0), (1, 1), (1, 2),
                        (2, 0), (2, 1), (2, 2)
                    ]

                    if self.angle < 0:
                        # 计算每个小正方形的中心点坐标和编号
                        for row, col in square_order:
                            # 计算小正方形的中心点相对于大矩形中心点的坐标
                            relative_center = np.array([(2 * col - 2) * self.width / 6, (2 * row - 2) * self.height / 6])

                            # 使用旋转矩阵来旋转小正方形的中心点
                            rotated_center = np.dot(rotation_matrix, relative_center)

                            # 计算小正方形的中心点的绝对坐标
                            absolute_center = self.center_big_square + rotated_center

                            # 将中心坐标和编号添加到列表中
                            self.squares_center.append((absolute_center, row * 3 + col + 1))
                    else:
                        # 以列为主的顺序计算每个小正方形的中心点坐标和编号
                        for col, row in square_order:
                            # 计算小正方形的中心点相对于大矩形中心点的坐标
                            relative_center = np.array([(2 * col - 2) * self.width / 6, (2 * row - 2) * self.height / 6])
                            # 使用旋转矩阵来旋转小正方形的中心点
                            rotated_center = np.dot(rotation_matrix, relative_center)
                            # 计算小正方形的中心点的绝对坐标
                            absolute_center = self.center_big_square + rotated_center
                            # 将中心坐标和编号添加到列表中
                            self.squares_center.append((absolute_center, row * 3 + col + 1))
                            # 画出每个小正方形的内接圆
                            cv2.circle(frame, (int(absolute_center[0]), int(absolute_center[1])), int(self.neijie_radius), (255, 0, 0), 2)

                    if(self.jiaodu > 0):
                        # 修正不同的格子的所有信息。1号和3号互换，2号和6号互换，5号和7号互换，0,4,8不变
                        self.squares_center[1], self.squares_center[3] = self.squares_center[3], self.squares_center[1]
                        self.squares_center[2], self.squares_center[6] = self.squares_center[6], self.squares_center[2]
                        self.squares_center[5], self.squares_center[7] = self.squares_center[7], self.squares_center[5]

                    # 得到所有小正方形的中心点坐标和四个大矩阵顶点坐标后，使用旋转矩阵计算每个小正方形的四个顶点坐标
                    # 计算每个小正方形的四个顶点坐标
                    self.average_colors.clear()
                    for center, number in self.squares_center:

                        # 计算每个内接圆的颜色平均值
                        mask = np.zeros((height, width), np.uint8)
                        center_int = tuple(center.astype(int))
                        radius_int = int(self.neijie_radius)
                        cv2.circle(mask, center_int, radius_int, 1, thickness=-1) #画出内接圆

                        average_color = cv2.mean(frame, mask=mask)[:3]
                        self.average_colors.append(average_color)

                        # 将average_color[0]的值绘制到对应的方块上
                        text = str(int(average_color[1]))
                        cv2.putText(frame, text, center_int, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    # 判断每个内接圆是否有棋子，以及棋子的颜色
                    # 通过self.test_jiugongge[]数组，调试无，黑，白的阈值部分
                    # # 筛选self.test_jiugongge[]数值中为1的格子
                    # selected_squares = [center for center, value in zip(self.squares_center, self.test_jiugongge) if value == 1]

                    # 得到这些格子的average_color[1]和average_color[2]数值
                    black_selected_colors = [(average_color[1], average_color[2]) for average_color, value in zip(self.average_colors, self.test_jiugongge) if value == 1]
                    if(self.save_yuzhi == 0):
                        # 计算 average_color[1] 和 average_color[2] 的总和
                        black_sum_1 = sum(black_color[0] for black_color in black_selected_colors)
                        black_sum_2 = sum(black_color[1] for black_color in black_selected_colors)

                        # 计算 average_color[1] 和 average_color[2] 的平均值
                        black_average_value_1 = black_sum_1 / len(black_selected_colors) if black_selected_colors else 0
                        black_average_value_2 = black_sum_2 / len(black_selected_colors) if black_selected_colors else 0

                        # 计算 average_color[1] 和 average_color[2] 的最大值
                        self.black_max_value_1 = max(black_color[0] for black_color in black_selected_colors) if black_selected_colors else 0
                        self.black_max_value_2 = max(black_color[1] for black_color in black_selected_colors) if black_selected_colors else 0

                        print(f"黑色最大值1: {self.black_max_value_1}, 黑色最大值2: {self.black_max_value_2}")



                    # 得到这些格子的average_color[0]和average_color[1]数值
                    white_selected_colors = [(average_color[0], average_color[1]) for average_color, value in zip(self.average_colors, self.test_jiugongge) if value == 2]
                    if(self.save_yuzhi == 0):
                        # 计算 average_color[1] 和 average_color[2] 的总和
                        white_sum_1 = sum(white_color[0] for white_color in white_selected_colors)
                        white_sum_2 = sum(white_color[1] for white_color in white_selected_colors)

                        # 计算 average_color[1] 和 average_color[2] 的平均值
                        white_average_value_1 = white_sum_1 / len(white_selected_colors) if white_selected_colors else 0
                        white_average_value_2 = white_sum_2 / len(white_selected_colors) if white_selected_colors else 0

                        # 计算 average_color[1] 和 average_color[2] 的最大值

                        self.white_min_value_1 = min(white_color[0] for white_color in white_selected_colors) if white_selected_colors else 0
                        self.white_min_value_2 = min(white_color[1] for white_color in white_selected_colors) if white_selected_colors else 0

                        print(f"白色最小值1: {self.white_min_value_1}, 白色最小值2: {self.white_min_value_2}")



                    # if len(black_selected_colors) == 0:
                    #     average_value = 0
                    #     max_value = 0
                    # # 计算所有格子这两个值的平均值和最大值
                    # else:
                    #     average_value = sum(black_selected_colors) / len(black_selected_colors)
                    #     max_value = max(black_selected_colors)

                    # print(f"average_value: {average_value}, max_value: {max_value}")


                    for p, average_color in enumerate(self.average_colors):
                        # 白棋赋值
                        if average_color[0] > self.white_min_value_1 - 20 and average_color[1] > self.white_min_value_2 - 20:
                            self.jiugongge[p] = 2
                        # 黑棋赋值
                        elif average_color[1] < self.black_max_value_1 + 20 and average_color[2] < self.black_max_value_2 + 20:
                            self.jiugongge[p] = 1
                        else:
                            # if(self.jiaodu < 0):
                            self.jiugongge[p] = 0

                        # 计算相对于大矩形中心点的坐标
                        relative_points = np.array([(-self.bianchang_half, -self.bianchang_half),
                                                   (self.bianchang_half, -self.bianchang_half),
                                                   (self.bianchang_half, self.bianchang_half),
                                                   (-self.bianchang_half, self.bianchang_half)])
                        # 使用旋转矩阵来旋转顶点坐标
                        rotated_points = np.dot(rotation_matrix, relative_points.T).T
                        # 计算顶点坐标的绝对坐标
                        absolute_points = rotated_points + center
                        # 将顶点坐标添加到列表中
                        self.square_points.append(absolute_points.astype(int))

                        # 在帧上绘制小正方形的中心点及编号
                        for center, number in self.squares_center:
                            # 绘制小正方形
                            cv2.drawContours(frame, [self.square_points[0]], 0, (0, 0, 255), 2) # 画一个小正方形
                            # cv2.drawContours(frame, [absolute_points.astype(int)], 0, (0, 0, 255), 2) # 画一个小正方形
                            # 把小方格的顺序画在中心点上
                            # cv2.putText(frame, str(number), (int(center[0]), int(center[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                # 存储检测到的白色和黑色棋子的数量
                white_count = 0
                black_count = 0
                without_white_count = 0
                without_black_count = 0
                # self.jiugongge = [0] * 9
                # 使用Hough圆变换来检测圆形，调节param2值，值越小，越容易识别，调节合适值即可
                original_circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=20, minRadius=20, maxRadius=50)

                out_yuan = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                count_yuan_in = 0 # 圆在矩阵内总数
                count_yuan_in_Black = 0 # 矩阵内的黑圆数量
                count_yuan_in_White = 0 # 矩阵内的白圆数量
                count_yuan_out = 0 # 圆在矩阵外总数
                count_yuan_out_Black = 0 # 矩阵外的黑圆数量
                count_yuan_out_White = 0 # 矩阵外的白圆数量





                # 如果检测到了圆形
                if original_circles is not None and self.find_rect == 1:
                    original_circles = np.uint16(np.around(original_circles))

                    # 创建一个空列表来存储距离去重后的圆形
                    circles = []


                    threshold = self.xiao_xiebian_half  # 设置距离阈值
                    #打印阈值
                    # print(f"阈值: {threshold}")
                    # print(f"角度{self.jiaodu}")
                    # 遍历每个圆形
                    yuan_point_position = [0] * len(original_circles) # 大于0为矩阵内，等于0为矩阵边界，小于0为矩阵外
                    for i in original_circles[0, :]:
                        # # 检查当前圆形与其他圆形的距离是否都大于阈值
                        # if all(self.distance(i, j) >= threshold for j in original_circles[0, :] if not np.array_equal(i, j)):
                        #     if self.aver_door == 0:#第一次条件可以宽松
                        #         circles.append(i)# 将符合条件的圆形添加到列表中
                        #     #第二次及以后则需要对半径进行审查去重
                        #     elif (abs(i[2] - self.radius_average) < self.radius_tolerance):  # 检查半径是否在radius_average左右的范围内去重后的圆形
                                # circles.append(i)# 将符合条件的圆形添加到列表中
                        circles.append(i)# 将符合条件的圆形添加到列表中

                    for i in circles:
                        center = (i[0] + left, i[1])  # 仅对x坐标添加偏移量
                        radius = i[2]

                        # 检查圆的面积是否在指定范围内
                        if np.pi * (radius ** 2) < 5000:  # 可根据需要调整此值

                            # # 判断检测到的圆形是否重复
                            # is_duplicate = False
                            # for detected_circle in detected_circles:
                            #     if self.distance(center, detected_circle[0]) < self.xiao_xiebian_half:
                            #         is_duplicate = True
                            #         break

                            # if not is_duplicate:
                            #     detected_circles.append((center, radius))

                            # 获取棋子中心点的颜色
                            color = frame[center[1], center[0]]
                            # 打印棋子的颜色值
                            #print(f"棋子中心 ({center[0]}, {center[1]}) 的颜色值: BGR({color[0]}, {color[1]}, {color[2]})")

                            # 掩模清空
                            self.white_mask = None

                            # 生成白色和黑色掩模
                            self.white_mask = cv2.inRange(frame, self.white_lower, self.white_upper)
                            self.black_mask = cv2.inRange(frame, self.black_lower, self.black_upper)




                            # 检查掩模中该位置的像素值
                            if self.white_mask[center[1], center[0]] > 0:
                                white_count += 1

                                circle_color = (0, 0, 0)  # 黑色
                                center_color = (0, 0, 0)  # 黑色
                            elif self.black_mask[center[1], center[0]] > 0:
                                black_count += 1

                                circle_color = (255, 255, 255)  # 白色
                                center_color = (255, 255, 255)  # 白色
                            else:

                                 continue  # 如果不匹配任何颜色范围，则跳过

                            #pt = np.array([center[0], center[1]])  # 将中心点坐标转换为整数，并创建一个包含这两个坐标的 numpy 数组
                            pt = (float(center[0]), float(center[1]))  # 使用元组表示点的坐标
                            circle_in_square = True # 重置参数，用于后面画圆判别条件
                            yuan_point_position = cv2.pointPolygonTest(self.royal_rect_points, pt, False)

                            # 打印结果
                            if yuan_point_position > 0:
                                # print(f"圆 {i} 在矩形内部")
                                count_yuan_in += 1

                            elif yuan_point_position == 0:
                                # print(f"圆 {i} 在矩形边界上")
                                p = 0
                                #不做处理
                            else:
                                # print(f"圆 {i} 在矩形外部")
                                count_yuan_out += 1
                                if self.white_mask[center[1], center[0]] > 0:
                                    count_yuan_out_White += 1
                                elif self.black_mask[center[1], center[0]] > 0:
                                    count_yuan_out_Black += 1
                                circle_in_square = False


                            # 判断是否有棋子中心点到9个正方形的中心坐标的距离是否有小于 self.xiao_xiebian_half 的距离的情况
                            # 计算圆心到每个小正方形中心的距离



                            # # 遍历每个正方形中心和对应的编号
                            # for square_center, number in self.squares_center:
                            #     # 使用pointPolygonTest函数判定圆心是否在小正方形内部，在哪一个小正方形内部
                            #     pt_1 = (float(center[0]), float(center[1]))  # 使用元组表示点的坐标
                            #     self.square_points[number - 1] = self.square_points[number - 1].reshape((-1, 1, 2))
                            #     if cv2.pointPolygonTest(self.square_points[number - 1], pt_1, False) > 0:
                            #         # if circle_color == (255, 255, 255):
                            #         #     g = 0
                            #         #     zheng_fang_black += 1
                            #         circle_in_square = True
                                    #print(f"圆心在第{number-1}个正方形内部")# 测试用


                                    # if(self.jiaodu > 0):
                                    #     if number == 2:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[3] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[3] = 2
                                    #     elif number == 3:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[6] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[6] = 2
                                    #     elif number == 4:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[1] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[1] = 2
                                    #     elif number == 6:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[7] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[7] = 2
                                    #     elif number == 7:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[2] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[2] = 2
                                    #     elif number == 8:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[5] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[5] = 2
                                    # else:
                                    #     if number == 1:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[0] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[0] = 2
                                    #     elif number == 2:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[1] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[1] = 2
                                    #     elif number == 3:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[2] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[2] = 2
                                    #     elif number == 4:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[3] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[3] = 2
                                    #     elif number == 5:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[4] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[4] = 2
                                    #     elif number == 6:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[5] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[5] = 2
                                    #     elif number == 7:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[6] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[6] = 2
                                    #     elif number == 8:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[7] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[7] = 2
                                    #     elif number == 9:
                                    #         if circle_color == (255, 255, 255):
                                    #             self.jiugongge[8] = 1
                                    #         elif circle_color == (0, 0, 0):
                                    #             self.jiugongge[8] = 2






                    # 参考 self.royal_rect_points = np.array([self.top_left, self.top_right, self.bottom_right, self.bottom_left], dtype=np.int32)




                            # if self.distance(center, square_center) < self.xiao_xiebian_half:

                            #     circle_in_square = True

                                #     # 执行适当的逻辑，更新九宫格的棋子状态
                                #     max_probability = 0
                                #     max_probability_number = None

                                #     # 遍历九宫格中的每个小正方形 这里有问题，还在修改
                                #     for square_center_inner, number_inner in self.squares_center:
                                #         g = 0


                            # 如果不在任何一个小正方形内部，则绘制圆形，统计未下子的棋子
                            if not circle_in_square: # 画出棋盘外识别到的圆，需要更换if条件即可
                            # if 1: # 画出所有识别到的圆，需要更换if条件即可

                                # 绘制外圆
                                cv2.circle(frame, center, radius, circle_color, 2)
                                # 绘制圆心
                                cv2.circle(frame, center, 2, center_color, 3)
                                # 获取这些圆的平均半径值
                                self.radius_sum += radius
                                self.circle_count += 1
                                self.radius_average = self.radius_sum / self.circle_count
                                self.aver_door = 1
                                if((without_white_count == 5) and (without_black_count == 5)): # 如果棋盘外黑棋子和白棋子都是满的，棋盘无子
                                    self.jiugongge = [0] * 9

                            #用完后重置参数
                            self.radius_sum = 0
                            self.circle_count = 0



                    # #概率平均数，消除偶尔异常
                    self.jiugongge = self.update_state_probabilistically(self.jiugongge)
                    # 可视化地打印当前九宫格信息
                    for i in range(9):
                        if self.jiugongge[i] == 0:
                            print("0", end=" ")
                        elif self.jiugongge[i] == 1:
                            print("1", end=" ")
                            count_yuan_in_Black += 1
                        else:
                            print("2", end=" ")
                            count_yuan_in_White += 1
                        if i % 3 == 2:
                            print()


                    # self.video_window.chessboard_widget.updateChessboardVisualization(self.jiugongge)#
                    # self.temp_jiugongge = [0, 1, 2, 0, 1, 2, 0, 1, 2].copy()
                    # self.chessboard_widget.update_chessboard_state()

                    # video_window_instance = ChessboardWidget()  # Create an instance
                    # video_window_instance.update_chessboard_state()
                    # print("hjk")
                    # shared_data = self.jiugongge
                    # print(f"第一{shared_data[0]}")




                    self.time_loop += 1

                    if(self.time_loop >= 3):
                        if (self.save_yuzhi == 1 and self.cheat_flag == 0):# 保存完后，棋局正式开始，加了限定条件必须是无作弊状态
                            self.paint_chess()
                            # 检查胜利者
                            self.winner = self.check_win(self.jiugongge)
                            self.move = self.find_best_move(self.jiugongge)
                            if(self.winner == -1):
                                print(f"赢家：{self.winner}")

                                print(f"老登，我下第{self.move+1}个格子")
                                temp1 = self.move + 1
                                self.text_label_2.setText(f"Fairy决定下第{temp1}位")

                            elif (self.zhixing == 1 and self.winner == 1) or (self.zhixing == 2 and self.winner == 2):
                                print(f"老登真菜，我赢了")
                                self.text_label_1.setText("胜利者:Fairy")
                                self.text_label_3.setText("新艾利都最强人工智能")

                            elif(self.zhixing == 1 and self.winner == 2) or (self.zhixing == 2 and self.winner == 1):
                                print(f"稍微让了你一下，你就那么嚣张")
                                self.text_label_1.setText("胜利者:法厄同")
                                self.text_label_3.setText("莫非你就是那个传奇绳匠")
                            elif(self.winner == 0):
                                print(f"平局而已，需要再来一局吗，小菜鸡")
                                self.text_label_1.setText("彼此彼此")
                                self.text_label_3.setText("来一碗超辣拉面")
                            elif(self.winner == -1):
                                print(f"游戏还没结束呢")

                            self.time_loop = 0 # 重新计时

                    # 打印完重置
                    # self.jiugongge = [0] * 9


                    # # 打印当前棋盘外棋子数量
                    # print(f"without_white pieces: {without_white_count}, without_black pieces: {without_black_count}")



                    # 更新棋子数量列表
                    self.white_window.pop(0)
                    self.white_window.append(white_count)
                    self.black_window.pop(0)
                    self.black_window.append(black_count)

                    # 计算最终的棋子数量，取滑动窗口的平均值并四舍五入
                    white_count_avg = round(sum(self.white_window) / len(self.white_window))
                    black_count_avg = round(sum(self.black_window) / len(self.black_window))
                    # print(f"盘中白:{count_yuan_in_White}, 盘中黑:{count_yuan_in_Black}")
                    # print(f"White pieces: {white_count_avg}, Black pieces: {black_count_avg}")
                    # print(f"未落子总数: {count_yuan_out}")text_label_5
                    self.text_label_5.setText(f"当前剩余{count_yuan_out_Black}颗黑棋 {count_yuan_out_White}颗白棋")

                    # print(f"未落子黑棋数: {count_yuan_out_Black}, 未落子白棋数:{count_yuan_out_White}")







            # 将帧转换为RGB格式
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape
            bytesPerLine = 3 * width
            qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            self.video_label.setPixmap(pixmap.scaled(*self.video_size))



            # # 记录结束时间
            # end_time = time.time()

            # # 计算处理时间
            # processing_time = end_time - start_time

            # # 计算帧率
            # fps = 1.0 / processing_time

            # print(f"FPS: {fps}")

    def check_win(self, jiugongge):
        win_conditions = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # 行
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # 列
            (0, 4, 8), (2, 4, 6)  # 对角线
        ]
        for a, b, c in win_conditions:
            if jiugongge[a] == jiugongge[b] == jiugongge[c] != 0:
                return jiugongge[a]
        if 0 not in jiugongge:
            return 0
        return -1

    def evaluate(self, jiugongge):
        winner = self.check_win(jiugongge)
        if winner == self.zhixing:
            return 10
        elif winner == 3 - self.zhixing:
            return -10

        score = 0
        for (a, b, c) in [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]:
            line = [jiugongge[a], jiugongge[b], jiugongge[c]]
            if line.count(self.zhixing) == 2 and line.count(0) == 1:
                score += 5
            if line.count(3 - self.zhixing) == 2 and line.count(0) == 1:
                score -= 4

        return score

    def minimax(self, jiugongge, depth, alpha, beta, is_maximizing):
        score = self.evaluate(jiugongge)
        if score == 10 or score == -10:
            return score
        if 0 not in jiugongge:
            return 0

        if is_maximizing:
            best = -float('inf')
            for i in range(9):
                if jiugongge[i] == 0:
                    jiugongge[i] = self.zhixing
                    best = max(best, self.minimax(jiugongge, depth + 1, alpha, beta, False))
                    jiugongge[i] = 0
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        break
            return best
        else:
            best = float('inf')
            for i in range(9):
                if jiugongge[i] == 0:
                    jiugongge[i] = 3 - self.zhixing
                    best = min(best, self.minimax(jiugongge, depth + 1, alpha, beta, True))
                    jiugongge[i] = 0
                    beta = min(beta, best)
                    if beta <= alpha:
                        break
            return best

    def find_best_move(self, jiugongge):
        best_val = -float('inf')
        self.move = -1

        for i in range(9):
            if jiugongge[i] == 0:
                jiugongge[i] = self.zhixing
                move_val = self.minimax(jiugongge, 0, -float('inf'), float('inf'), False)
                jiugongge[i] = 0

                if move_val > best_val or (move_val == best_val and i == 4):
                    self.move = i
                    best_val = move_val

        return self.move


    def paint_chess(self):
        # 获取当前图像
        pixmap = self.image_label.pixmap().copy()  # 复制现有图像以便在其上绘制

        # 创建 QPainter 对象
        painter = QPainter(pixmap)

        # 依次绘制每个状态的圆形
        for i in range(9):
            # 获取当前位置
            pt2 = self.weizhi[i]

            if self.jiugongge[i] == 0:
                # 白色圆形
                pen = QPen(QColor(255, 255, 255), 10)  # 白色画笔
                brush = QBrush(QColor(255, 255, 255))  # 白色填充
            elif self.jiugongge[i] == 1:
                # 灰色圆形
                pen = QPen(QColor(0, 0, 0), 10)  # 黑色画笔
                brush = QBrush(QColor(0, 0, 0))  # 黑色填充
            elif self.jiugongge[i] == 2:
                # 黑色圆形
                pen = QPen(QColor(192, 192, 192), 10)  # 灰色画笔
                brush = QBrush(QColor(192, 192, 192))  # 灰色填充

            # 设置画笔和填充
            painter.setPen(pen)
            painter.setBrush(brush)

            # 画一个圆形
            painter.drawEllipse(pt2[0], pt2[1], 60, 60)

        # 结束绘制
        painter.end()

        # 更新 QLabel 显示
        self.image_label.setPixmap(pixmap)



    def update_masks(self, frame):
        # 根据当前帧更新白色和黑色掩模
        self.white_mask = cv2.inRange(frame, self.white_lower, self.white_upper)
        self.black_mask = cv2.inRange(frame, self.black_lower, self.black_upper)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    video_window = VideoWindow()
    video_window.show()
    sys.exit(app.exec_())
