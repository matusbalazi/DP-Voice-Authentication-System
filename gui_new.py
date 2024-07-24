import sys
from PyQt6.QtWidgets import (QApplication,
                             QButtonGroup,
                             QGridLayout,
                             QHBoxLayout,
                             QLabel,
                             QMainWindow,
                             QPushButton,
                             QStackedWidget,
                             QWidget)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt

from translations import Translations
from general import constants as const

def initialize_font_sizes(width, height):
    fonts = [0, 0, 0]

    if width == 1920 and height == 1080:
        fonts[0] = const.FONT_LARGE
        fonts[1] = const.FONT_MEDIUM
        fonts[2] = const.FONT_SMALL

    if width == 1280 and height == 720:
        fonts[0] = round(const.FONT_LARGE / 1.5)
        fonts[1] = round(const.FONT_MEDIUM / 1.5)
        fonts[2] = round(const.FONT_SMALL / 1.5)

    return fonts

def create_grid(layout):
    layout.setRowStretch(0, 1)
    layout.setRowStretch(1, 0)
    layout.setRowStretch(2, 1)
    layout.setRowStretch(3, 0)
    layout.setRowStretch(4, 1)

    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(1, 0)
    layout.setColumnStretch(2, 1)

class IntroFrame(QWidget):
    def __init__(self, switch_function, update_menubar_items_translations):
        super().__init__()
        self.switch_function = switch_function
        self.update_menubar_items_translations = update_menubar_items_translations
        layout = QGridLayout()

        create_grid(layout)

        self.label_main_title = QLabel(Translations.get_translation("system_authentication"))
        self.label_main_title.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.label_main_title.setFont(QFont(const.FONT_RALEWAY_BOLD, font_large))
        layout.addWidget(self.label_main_title, 0, 1, Qt.AlignmentFlag.AlignCenter)

        self.button_open_door = QPushButton(Translations.get_translation("open_door"))
        self.button_open_door.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        self.button_open_door.clicked.connect(lambda: self.switch_function(2))
        layout.addWidget(self.button_open_door, 2, 1, Qt.AlignmentFlag.AlignCenter)

        language_layout = QHBoxLayout()

        button_sk = QPushButton("SK")
        button_en = QPushButton("EN")
        button_sk.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_medium))
        button_en.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_medium))
        button_sk.setEnabled(False)

        button_sk.setStyleSheet("QPushButton { padding: 20px 30px; margin: 0px; }")
        button_en.setStyleSheet("QPushButton { padding: 20px 30px; margin: 0px; }")

        button_sk.clicked.connect(lambda: self.change_language("SK", button_sk, button_en))
        button_sk.clicked.connect(lambda: self.update_menubar_items_translations())
        button_en.clicked.connect(lambda: self.change_language("EN", button_en, button_sk))
        button_en.clicked.connect(lambda: self.update_menubar_items_translations())

        radio_group = QButtonGroup(self)
        radio_group.addButton(button_sk)
        radio_group.addButton(button_en)

        language_layout.addWidget(button_sk)
        language_layout.addWidget(button_en)
        layout.addLayout(language_layout, 4, 1, Qt.AlignmentFlag.AlignCenter)

        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

    def change_language(self, language, button_clicked, button_unclicked):
        Translations.set_language(language)
        button_clicked.setEnabled(False)
        button_unclicked.setEnabled(True)
        self.update_translations()

    def update_translations(self):
        self.label_main_title.setText(Translations.get_translation("system_authentication"))
        self.button_open_door.setText(Translations.get_translation("open_door"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.showFullScreen()

        self.menu_bar = None

        font_sizes = initialize_font_sizes(self.geometry().width(), self.geometry().height())
        print(self.size().width())
        print(self.size().height())
        global font_large, font_medium, font_small
        font_large, font_medium, font_small = font_sizes[0], font_sizes[1], font_sizes[2]

        self.setWindowTitle(Translations.get_translation("system_authentication"))

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.intro_frame = IntroFrame(self.switch_frame, self.update_menubar_items_translations)
        self.stacked_widget.addWidget(self.intro_frame)

        self.create_menu()
        self.apply_styles()

    def create_menu(self):
        self.menu_bar = self.menuBar()
        self.menu_bar.setFont(QFont(const.FONT_RHD_MEDIUM, font_small))

        intro_action = QAction(Translations.get_translation("intro"), self)
        intro_action.triggered.connect(lambda: self.switch_frame(1))

        about_action = QAction(Translations.get_translation("about_project"), self)
        about_action.triggered.connect(lambda: self.switch_frame(4))

        admin_action = QAction(Translations.get_translation("admin"), self)
        admin_action.triggered.connect(lambda: self.switch_frame(3))

        exit_action = QAction(Translations.get_translation("exit"), self)
        exit_action.triggered.connect(lambda: sys.exit())

        self.menu_bar.addActions([intro_action, about_action, admin_action, exit_action])

    def update_menubar_items_translations(self):
        self.menu_bar.actions()[0].setText(Translations.get_translation("intro"))
        self.menu_bar.actions()[1].setText(Translations.get_translation("about_project"))
        self.menu_bar.actions()[2].setText(Translations.get_translation("admin"))
        self.menu_bar.actions()[3].setText(Translations.get_translation("exit"))

    """
        1 - intro_frame
        2 - open_door_frame
        3 - admin_frame
        4 - about_frame
    """
    def switch_frame(self, index):
        self.stacked_widget.setCurrentIndex(index)

    """
        orange - #f47e21
        blue - #58a6d4
        light blue - #a2d5ec
        black - #000000
        white - #ffffff
    """
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #a2d5ec;
            }
            QMenuBar {
                background-color: #58a6d4;
                color: #000000;
            }
            QMenuBar::item {
                padding: 30px 40px;
                margin: 0px 20px;
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #f47e21;
                color: #000000;
                border-radius: 15px;
                border: 5px solid #000000;
            }
            QPushButton {
                background-color: #f47e21;
                color: #000000;
                padding: 30px 80px;
                margin: 20px;
                border-radius: 15px;
                border: 5px solid #000000;
            }
            QPushButton:hover {
                background-color: #58a6d4;
            }
            QPushButton:disabled {
                background-color: #58a6d4;
            }
            QLabel {
                color: #000000; 
                padding: 20px;
            }
        """)


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())


