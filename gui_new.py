import sys
from PyQt6.QtWidgets import (QApplication,
                             QButtonGroup,
                             QGridLayout,
                             QHBoxLayout,
                             QLabel,
                             QLineEdit,
                             QMainWindow,
                             QPushButton,
                             QStackedWidget,
                             QWidget)
from PyQt6.QtGui import QFont, QAction, QPixmap
from PyQt6.QtCore import Qt

from translations import Translations
from general import constants as const
from general import log_file_builder as log
from authentication import credentials, string_hasher
from database import connection_controller as conn

index_intro_frame = 0
index_open_door_frame = 1
index_admin_frame = 2
index_about_frame = 3


def initialize_font_sizes(window_width, window_height):
    fonts = [0, 0, 0]

    if window_width == 1920 and window_height == 1080:
        fonts[0] = const.FONT_LARGE
        fonts[1] = const.FONT_MEDIUM
        fonts[2] = const.FONT_SMALL

    if window_width == 1280 and window_height == 720:
        fonts[0] = round(const.FONT_LARGE / 1.5)
        fonts[1] = round(const.FONT_MEDIUM / 1.5)
        fonts[2] = round(const.FONT_SMALL / 1.5)

    return fonts


def initialize_image_sizes(window_width, window_height):
    rescaler = 0

    if window_width == 1920 and window_height == 1080:
        rescaler = const.IMAGE_RESCALER_FHD

    if window_width == 1280 and window_height == 720:
        rescaler = const.IMAGE_RESCALER_HD

    return rescaler


def create_rows_cols(layout):
    layout.setRowStretch(0, 1)
    layout.setRowStretch(1, 0)
    layout.setRowStretch(2, 1)
    layout.setRowStretch(3, 0)
    layout.setRowStretch(4, 1)

    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(1, 0)
    layout.setColumnStretch(2, 1)


class Frame(QWidget):
    def __init__(self):
        super().__init__()

        self.grid_layout = QGridLayout()
        create_rows_cols(self.grid_layout)

        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.grid_layout)

    def create_items(self):
        self.label_main_title = QLabel(Translations.get_translation("system_authentication"))
        self.label_main_title.setFont(QFont(const.FONT_RALEWAY_BOLD, font_large))
        self.grid_layout.addWidget(self.label_main_title, 0, 1, Qt.AlignmentFlag.AlignCenter)

    def clear_items(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.grid_layout.removeItem(item)


class IntroFrame(Frame):
    def __init__(self, switch_frames, update_menubar_items_translations):
        super().__init__()

        self.switch_frames = switch_frames
        self.update_menubar_items_translations = update_menubar_items_translations

        self.create_items()

    def create_items(self):
        super().create_items()

        self.button_open_door = QPushButton(Translations.get_translation("open_door", True))
        self.button_open_door.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        self.button_open_door.clicked.connect(lambda: self.switch_frames(1))
        self.grid_layout.addWidget(self.button_open_door, 2, 1, Qt.AlignmentFlag.AlignCenter)

        languages_layout = QHBoxLayout()

        button_sk = QPushButton("SK")
        button_en = QPushButton("EN")
        button_sk.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_medium))
        button_en.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_medium))
        if Translations.get_language() == "SK":
            button_sk.setEnabled(False)
        else:
            button_en.setEnabled(False)

        button_sk.setStyleSheet("QPushButton { padding: 20px 30px; margin: 0px; }")
        button_en.setStyleSheet("QPushButton { padding: 20px 30px; margin: 0px; }")

        button_sk.clicked.connect(lambda: self.change_language("SK", button_sk, button_en))
        button_sk.clicked.connect(lambda: self.update_menubar_items_translations())
        button_en.clicked.connect(lambda: self.change_language("EN", button_en, button_sk))
        button_en.clicked.connect(lambda: self.update_menubar_items_translations())

        languages_layout.addWidget(button_sk)
        languages_layout.addWidget(button_en)
        self.grid_layout.addLayout(languages_layout, 3, 1, Qt.AlignmentFlag.AlignCenter)

        image_label = QLabel()
        self.grid_layout.addWidget(image_label, 4, 1, Qt.AlignmentFlag.AlignCenter)
        image_pixmap = QPixmap('VAS - logo.png')
        scaled_pixmap = image_pixmap.scaled(round(image_pixmap.width() / rescale_factor),
                                            round(image_pixmap.height() / rescale_factor))
        image_label.setPixmap(scaled_pixmap)
        image_label.setStyleSheet("margin-top: 40px; margin-bottom: 40px")

    def change_language(self, language, button_clicked, button_unclicked):
        Translations.set_language(language)
        button_clicked.setEnabled(False)
        button_unclicked.setEnabled(True)
        self.update_translations()

    def update_translations(self):
        self.label_main_title.setText(Translations.get_translation("system_authentication"))
        self.button_open_door.setText(Translations.get_translation("open_door", True))


class OpenDoorFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()


class AdminFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()


class AboutFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()

        label_thesis = QLabel(Translations.get_translation("thesis", True))
        label_thesis.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_medium))
        self.grid_layout.addWidget(label_thesis, 1, 1, Qt.AlignmentFlag.AlignCenter)

        label_about_project = QLabel(
            Translations.get_translation("topic_new") + "\n" + Translations.get_translation(
                "student_new") + "\n" + Translations.get_translation(
                "mentor_new") + "\n" + Translations.get_translation(
                "year_new"))
        label_about_project.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
        self.grid_layout.addWidget(label_about_project, 2, 1, Qt.AlignmentFlag.AlignCenter)

        label_school = QLabel(Translations.get_translation("university") + "\n\n" + Translations.get_translation(
            "faculty_new") + "\n\n" + Translations.get_translation("department_new"))
        label_school.setFont(QFont(const.FONT_RALEWAY_MEDIUM, round(font_small / 1.4)))
        label_school.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(label_school, 3, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.clicked.connect(lambda: self.switch_frames(0))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignLeft)

        entry_password = QLineEdit()
        entry_password.setEchoMode(QLineEdit.EchoMode.Password)
        entry_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        entry_password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(entry_password, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_password = QPushButton(Translations.get_translation("confirm", True))
        button_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_password.clicked.connect(lambda: self.verify_password(entry_password.text()))
        self.grid_layout.addWidget(button_password, 4, 2, Qt.AlignmentFlag.AlignRight)

    def verify_password(self, value):
        is_password_correct = string_hasher.check_string(value, credentials.authentication_password, credentials.authentication_salt)

        if is_password_correct and conn.check_internet_connection():
            msg_success = "Entered password was correct."
            log.log_info(msg_success)
        else:
            msg_warning = "Entered password was incorrect."
            log.log_warning(msg_warning)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.showFullScreen()

        self.menu_bar = None

        font_sizes = initialize_font_sizes(self.geometry().width(), self.geometry().height())
        global font_large, font_medium, font_small, rescale_factor
        font_large, font_medium, font_small = font_sizes[0], font_sizes[1], font_sizes[2]
        rescale_factor = initialize_image_sizes(self.geometry().width(), self.geometry().height())

        self.setWindowTitle(Translations.get_translation("system_authentication"))

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.intro_frame = IntroFrame(self.switch_frame, self.update_menubar_items_translations)
        self.open_door_frame = OpenDoorFrame(self.switch_frame)
        self.admin_frame = AdminFrame(self.switch_frame)
        self.about_frame = AboutFrame(self.switch_frame)

        self.stacked_widget.addWidget(self.intro_frame)
        self.stacked_widget.addWidget(self.open_door_frame)
        self.stacked_widget.addWidget(self.admin_frame)
        self.stacked_widget.addWidget(self.about_frame)

        self.create_menu()
        self.apply_styles()

    def create_menu(self):
        self.menu_bar = self.menuBar()
        self.menu_bar.setFont(QFont(const.FONT_RHD_MEDIUM, font_small))

        intro_action = QAction(Translations.get_translation("intro"), self)
        intro_action.triggered.connect(lambda: self.switch_frame(0))

        about_action = QAction(Translations.get_translation("about_project"), self)
        about_action.triggered.connect(lambda: self.switch_frame(3))

        admin_action = QAction(Translations.get_translation("admin"), self)
        admin_action.triggered.connect(lambda: self.switch_frame(2))

        exit_action = QAction(Translations.get_translation("exit"), self)
        exit_action.triggered.connect(lambda: sys.exit())

        self.menu_bar.addActions([intro_action, about_action, admin_action, exit_action])

    def update_menubar_items_translations(self):
        self.setWindowTitle(Translations.get_translation("system_authentication"))
        self.menu_bar.actions()[0].setText(Translations.get_translation("intro"))
        self.menu_bar.actions()[1].setText(Translations.get_translation("about_project"))
        self.menu_bar.actions()[2].setText(Translations.get_translation("admin"))
        self.menu_bar.actions()[3].setText(Translations.get_translation("exit"))

    """
        indexes:
            0 - intro_frame
            1 - open_door_frame
            2 - admin_frame
            3 - about_frame
    """

    def switch_frame(self, index):
        self.stacked_widget.currentWidget().clear_items()
        self.stacked_widget.setCurrentIndex(index)
        self.stacked_widget.currentWidget().create_items()

    """
        color palette:
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
            QLineEdit {
                background-color: #58a6d4;
                color: #000000;
                padding: 30px 80px;
                border-radius: 15px;
                border: 5px solid #000000;
            }
        """)


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
