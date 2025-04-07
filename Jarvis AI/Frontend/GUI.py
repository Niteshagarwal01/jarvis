from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget,QVBoxLayout,QPushButton,QFrame, QLabel, QSizePolicy, QHBoxLayout
from PyQt5.QtGui import QIcon, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat, QPainter
from PyQt5.QtCore import Qt, QTimer, QSize
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
AssistantName = env_vars.get("AssistantName")
current_dir = os.getcwd()
InitialPath = f"{current_dir}\\Frontend\\Files"
TempDirPath = f"{current_dir}\\Frontend\\Temp"
GraphicsDirPath = f"{current_dir}\\Frontend\\Graphics"

def AnswerModifier(Answer):
    Lines = Answer.split("\n")
    non_empty_lines = [line for line in Lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):

    new_query = Query.lower().strip()
    query_words= new_query.split()
    question_words = ["what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how"]
    
    if any(word + " " in new_query for word in question_words):
        if query_words [-1][-1] in ['.', '?','!']:
            new_query = new_query[ :- 1] + "?"
        else:
            new_query += "?"

    else:
        if query_words[-1][-1] in ['. ', '?', '!']:
            new_query = new_query[ :- 1] + "."
        else:
            new_query  += "?"

    return new_query.capitalize()

def SetAssistantStatus(Status):
    with open(f"{TempDirPath}/Status.data", "w", encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    try:
        with open(f"{TempDirPath}/Status.data", "r", encoding='utf-8') as file:
            Status = file.read().strip()
            return Status if Status else "Idle"
    except FileNotFoundError:
        return "Idle"

def SetMicrophoneStatus(Command):
    with open(f"{TempDirPath}/Mic.data", "w", encoding="utf-8") as file:
        file.write(Command)

def GetMicrophoneStatus():
    try:
        with open(f"{TempDirPath}/Mic.data", "r", encoding="utf-8") as file:
            Status = file.read().strip()
            return Status if Status else "Disabled"
    except FileNotFoundError:
        return "Disabled"

def GraphicsDirectoryPath(filename):
    Path = f"{GraphicsDirPath}/{filename}"
    return Path

def TempDirectoryPath(filename):
    Path = f"{TempDirPath}/{filename}"
    return Path

def ShowTextToScreen(Text):
    with open(f"{TempDirPath}/Responses.data", "w", encoding="utf-8") as file:
        file.write(Text)

class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 40, 40, 100)
        layout.setSpacing(0)

        # Chat text edit
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: black;
                color: white;
                font-size: 14px;
                padding: 10px;
                border: none;
            }
        """)
        layout.addWidget(self.chat_text_edit)

        # Jarvis GIF
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        if movie.isValid():
            max_gif_size_w = 480
            max_gif_size_h = 270
            movie.setScaledSize(QSize(max_gif_size_w, max_gif_size_h))
            self.gif_label.setAlignment(Qt.AlignCenter)
            self.gif_label.setMovie(movie)
            movie.start()
            layout.addWidget(self.gif_label)
        else:
            print("Error: Jarvis.gif not found or invalid")

        # Status container
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(20)

        # Microphone status
        self.mic_label = QLabel("Microphone: Disabled")
        self.mic_label.setStyleSheet("""
            QLabel {
                color: #FF4444;
                font-size: 14px;
                margin-top: 10px;
                border: none;
            }
        """)
        status_layout.addWidget(self.mic_label)

        # Assistant status
        self.label = QLabel("Idle")
        self.label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 16px;
                margin-top: 10px;
                border: none;
            }
        """)
        status_layout.addWidget(self.label)

        layout.addLayout(status_layout)

        # Initialize timers
        self.message_timer = QTimer(self)
        self.message_timer.timeout.connect(self.loadMessages)
        self.message_timer.start(500)

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.updateStatus)
        self.status_timer.start(500)

        self.mic_timer = QTimer(self)
        self.mic_timer.timeout.connect(self.updateMicStatus)
        self.mic_timer.start(500)

    def updateStatus(self):
        status = GetAssistantStatus()
        self.label.setText(status)
        
        # Update status color based on state
        if "listening" in status.lower():
            self.label.setStyleSheet("""
                QLabel {
                    color: #FF4444;
                    font-size: 16px;
                    margin-top: 10px;
                    border: none;
                }
            """)
        elif "speaking" in status.lower() or "translating" in status.lower():
            self.label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 16px;
                    margin-top: 10px;
                    border: none;
                }
            """)
        else:
            self.label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 16px;
                    margin-top: 10px;
                    border: none;
                }
            """)

    def updateMicStatus(self):
        mic_status = GetMicrophoneStatus()
        self.mic_label.setText(f"Microphone: {mic_status}")
        
        # Update microphone status color
        if "true" in mic_status.lower():
            self.mic_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 14px;
                    margin-top: 10px;
                    border: none;
                }
            """)
        else:
            self.mic_label.setStyleSheet("""
                QLabel {
                    color: #FF4444;
                    font-size: 14px;
                    margin-top: 10px;
                    border: none;
                }
            """)

    def loadMessages(self):
        try:
            with open(f"{TempDirPath}/Responses.data", "r", encoding="utf-8") as file:
                messages = file.read().strip()
                if messages:
                    self.chat_text_edit.append(messages)
        except FileNotFoundError:
            pass

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create a container for the GIF and status
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 40, 0, 40)
        content_layout.setSpacing(20)

        # Jarvis GIF
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        if movie.isValid():
            max_gif_size_w = 480
            max_gif_size_h = 270
            movie.setScaledSize(QSize(max_gif_size_w, max_gif_size_h))
            self.gif_label.setAlignment(Qt.AlignCenter)
            self.gif_label.setMovie(movie)
            movie.start()
            content_layout.addWidget(self.gif_label)
        else:
            print("Error: Jarvis.gif not found or invalid")

        # Status container
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(20)

        # Microphone status
        self.mic_label = QLabel("Microphone: Disabled")
        self.mic_label.setStyleSheet("""
            QLabel {
                color: #FF4444;
                font-size: 14px;
                margin-top: 10px;
                border: none;
            }
        """)
        status_layout.addWidget(self.mic_label)

        # Assistant status
        self.label = QLabel("Idle")
        self.label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 16px;
                margin-top: 10px;
                border: none;
            }
        """)
        status_layout.addWidget(self.label)

        content_layout.addLayout(status_layout)

        # Center the content
        container = QWidget()
        container.setLayout(content_layout)
        container.setStyleSheet("""
            QWidget {
                background-color: black;
            }
        """)
        layout.addStretch(1)
        layout.addWidget(container)
        layout.addStretch(1)

        # Set widget properties
        self.setStyleSheet("""
            QWidget {
                background-color: black;
            }
        """)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

        # Initialize timers for status updates
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.updateStatus)
        self.status_timer.start(500)

        self.mic_timer = QTimer(self)
        self.mic_timer.timeout.connect(self.updateMicStatus)
        self.mic_timer.start(500)

    def updateStatus(self):
        status = GetAssistantStatus()
        self.label.setText(status)
        
        # Update status color based on state
        if "listening" in status.lower():
            self.label.setStyleSheet("""
                QLabel {
                    color: #FF4444;
                    font-size: 16px;
                    margin-top: 10px;
                    border: none;
                }
            """)
        elif "speaking" in status.lower() or "translating" in status.lower():
            self.label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 16px;
                    margin-top: 10px;
                    border: none;
                }
            """)
        else:
            self.label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 16px;
                    margin-top: 10px;
                    border: none;
                }
            """)

    def updateMicStatus(self):
        mic_status = GetMicrophoneStatus()
        self.mic_label.setText(f"Microphone: {mic_status}")
        
        # Update microphone status color
        if "true" in mic_status.lower():
            self.mic_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 14px;
                    margin-top: 10px;
                    border: none;
                }
            """)
        else:
            self.mic_label.setStyleSheet("""
                QLabel {
                    color: #FF4444;
                    font-size: 14px;
                    margin-top: 10px;
                    border: none;
                }
            """)

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Chat section
        self.chat_section = ChatSection()
        layout.addWidget(self.chat_section)

        # Set widget properties
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.stacked_widget = stacked_widget
        self.current_screen = None

    def initUI(self):
        # Create horizontal layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Title label
        title_label = QLabel(f"{str(AssistantName).capitalize()} AI")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                background-color: white;
                padding: 0 10px;
                border-right: 1px solid #ccc;
            }
        """)

        # Buttons
        home_button = QPushButton("Home")
        message_button = QPushButton("Chat")
        minimize_button = QPushButton("-")
        self.maximize_button = QPushButton("□")
        close_button = QPushButton("×")

        # Icons
        home_icon = QIcon(GraphicsDirectoryPath('home.png'))
        message_icon = QIcon(GraphicsDirectoryPath('message.png'))
        minimize_icon = QIcon(GraphicsDirectoryPath('minimize.png'))
        maximize_icon = QIcon(GraphicsDirectoryPath('maximize.png'))
        close_icon = QIcon(GraphicsDirectoryPath('close.png'))

        # Set icons
        home_button.setIcon(home_icon)
        message_button.setIcon(message_icon)
        minimize_button.setIcon(minimize_icon)
        self.maximize_button.setIcon(maximize_icon)
        close_button.setIcon(close_icon)

        # Button styles
        buttons = [home_button, message_button, minimize_button, self.maximize_button, close_button]
        for button in buttons:
            button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: none;
                    padding: 5px;
                    margin-left: 5px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)

        # Add widgets to layout
        self.layout.addWidget(title_label)
        self.layout.addStretch(1)
        self.layout.addWidget(home_button)
        self.layout.addWidget(message_button)
        self.layout.addWidget(minimize_button)
        self.layout.addWidget(self.maximize_button)
        self.layout.addWidget(close_button)

        # Line frame
        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("""
            QFrame {
                background-color: #ccc;
                border: none;
            }
        """)
        self.layout.addWidget(line_frame)

        # Connect signals
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button.clicked.connect(self.maximizeWindow)
        close_button.clicked.connect(self.closeWindow)

        # Drag settings
        self.dragable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(QPixmap(GraphicsDirectoryPath('maximize.png')))
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(QPixmap(GraphicsDirectoryPath('restore.png')))

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.dragable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        
        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        
        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        # Set window size and position
        self.setGeometry(0, 0, screen_width, screen_height)

        # Create stacked widget
        stacked_widget = QStackedWidget(self)

        # Initialize screens
        initial_screen = InitialScreen()
        message_screen = MessageScreen()

        # Add screens to stacked widget
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)

        # Set window properties
        self.setStyleSheet("background-color: black;")
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Create and set top bar
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)

        # Set central widget
        self.setCentralWidget(stacked_widget)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()