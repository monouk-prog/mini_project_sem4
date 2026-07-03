from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QSpacerItem, QSizePolicy, QButtonGroup)
from PySide6.QtCore import Qt
from ui.game_window import GameWindow 

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tic Tac Toe - Menu")
        self.resize(480, 520)

        self.setStyleSheet("""
            QWidget {
                background-color: #0b0c10;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #8f94fb;
                font-weight: bold;
                font-size: 13px;
                letter-spacing: 1px;
                margin-top: 20px;
                text-transform: uppercase;
            }
            QLabel#TitleLabel {
                font-size: 34px;
                color: #00f2fe;
                font-weight: 900;
                letter-spacing: 4px;
                margin-bottom: 10px;
                margin-top: 10px;
            }
            QLabel#SubtitleLabel {
                font-size: 12px;
                color: #45a29e;
                font-weight: 600;
                letter-spacing: 2px;
                margin-top: 0px;
                margin-bottom: 25px;
            }
            QPushButton {
                background-color: #1f2833;
                color: #c5c6c7;
                border: 2px solid #2c3e50;
                border-radius: 10px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2b3746;
                border-color: #45a29e;
                color: white;
            }
            QPushButton:checked {
                background-color: #1a252f;
                color: #00f2fe;
                border: 2px solid #00f2fe;
            }
            QPushButton#PlayButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff007f, stop:1 #ff4757);
                color: white;
                border: none;
                padding: 16px;
                font-size: 20px;
                font-weight: 900;
                letter-spacing: 2px;
                border-radius: 12px;
                margin-top: 30px;
            }
            QPushButton#PlayButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff2a9d, stop:1 #ff6b81);
                cursor: pointer;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        # Title Block
        self.title = QLabel("TIC TAC TOE")
        self.title.setObjectName("TitleLabel")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        self.subtitle = QLabel("MEMORIZED TIC-TAC-TOE")
        self.subtitle.setObjectName("SubtitleLabel")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.subtitle)

        # Mode Selection
        self.layout.addWidget(QLabel("Select Match Type"))
        self.mode_layout = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        
        self.btn_pvp = QPushButton("Local PvP")
        self.btn_pva = QPushButton("Vs Computer")
        
        for btn in (self.btn_pvp, self.btn_pva):
            btn.setCheckable(True)
            self.mode_group.addButton(btn)
            self.mode_layout.addWidget(btn)
            
        self.btn_pvp.setChecked(True) 
        self.btn_pva.toggled.connect(self.toggle_ai_options)
        self.layout.addLayout(self.mode_layout)

        # AI Difficulty Block
        self.ai_label = QLabel("Computer Subroutine")
        self.layout.addWidget(self.ai_label)
        
        self.diff_layout = QHBoxLayout()
        self.diff_group = QButtonGroup(self)
        
        self.btn_easy = QPushButton("Easy")
        self.btn_med = QPushButton("Medium")
        self.btn_hard = QPushButton("Hard")
        
        for btn in (self.btn_easy, self.btn_med, self.btn_hard):
            btn.setCheckable(True)
            self.diff_group.addButton(btn)
            self.diff_layout.addWidget(btn)
            
        self.btn_easy.setChecked(True)
        self.layout.addLayout(self.diff_layout)
        
        # Hide AI options initially
        self.ai_label.hide()
        for i in range(self.diff_layout.count()):
            self.diff_layout.itemAt(i).widget().hide()

        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Launch Button
        self.start_btn = QPushButton("ENGAGE SYSTEM")
        self.start_btn.setObjectName("PlayButton")
        self.start_btn.clicked.connect(self.launch_game)
        self.layout.addWidget(self.start_btn)

        self.active_game = None

    def toggle_ai_options(self, is_ai_mode):
        self.ai_label.setVisible(is_ai_mode)
        for i in range(self.diff_layout.count()):
            self.diff_layout.itemAt(i).widget().setVisible(is_ai_mode)

    def launch_game(self):
        selected_mode = "Player vs AI" if self.btn_pva.isChecked() else "Player vs Player"
        difficulty = "easy"
        if self.btn_med.isChecked(): difficulty = "medium"
        elif self.btn_hard.isChecked(): difficulty = "hard"

        game_settings = {
            "size": 3,
            "mode": selected_mode,
            "difficulty": difficulty if selected_mode == "Player vs AI" else None
        }

        self.active_game = GameWindow(settings=game_settings)
        self.active_game.show()
        self.close()