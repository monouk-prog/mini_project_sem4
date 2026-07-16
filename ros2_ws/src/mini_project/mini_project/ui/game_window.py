from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox
from PySide6.QtCore import Qt, QObject, Signal
import threading

from mini_project.game.logic import GameLogic
import mini_project.ai.easy as aieasy
import mini_project.ai.medium as aimedium
import mini_project.ai.hard as aihard

# ROS2 imports — optional, gracefully skip if not available
try:
    import rclpy
    from rclpy.node import Node
    from tictactoe_msgs.msg import TicTacToeMove
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False
    print("ROS not available")

# Bridge between ROS2 thread and Qt main thread
class RosBridge(QObject):
    key_received = Signal(int)  # sends selected_cell (1-9)

class KeySubscriber(Node):
    def __init__(self, bridge: RosBridge):
        super().__init__('tictactoe_subscriber')
        self.bridge = bridge
        self.create_subscription(TicTacToeMove, 'tictactoe/move', self.callback, 10)

    def callback(self, msg):
        self.get_logger().info(f'Received cell: {msg.selected_cell}')
        self.bridge.key_received.emit(msg.selected_cell)  # thread-safe emit to Qt

class GameWindow(QWidget):
    def __init__(self, settings):
        super().__init__()

        self.setWindowTitle("Tic Tac Toe - Battle")
        self.resize(750, 800)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #0b0c10;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """) 

        self.settings = settings
        self.logic = GameLogic()
        self.mode = settings["mode"]
        self.difficulty = settings.get("difficulty", "easy")

        self.cursor_r = 0
        self.cursor_c = 0
        self.is_returning_to_menu = False

        # ROS2 setup
        self.ros_node = None
        if ROS_AVAILABLE:
            self.ros_bridge = RosBridge()
            self.ros_bridge.key_received.connect(self.handle_ros_move)
            try:
                rclpy.init()
                self.ros_node = KeySubscriber(self.ros_bridge)
                self.ros_thread = threading.Thread(
                    target=rclpy.spin,
                    args=(self.ros_node,),
                    daemon=True
                )
                self.ros_thread.start()
                print("ROS2 subscriber started.")
            except Exception as e:
                print(f"ROS2 init failed: {e}")

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addStretch()

        # Dynamic Game Status Header
        self.info = QLabel()
        self.info.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.info)

        self.h_layout = QHBoxLayout()
        self.h_layout.addStretch() 

        # Game Board Layout
        self.grid = QGridLayout()
        self.grid.setSpacing(14)
        self.buttons = []

        for r in range(self.logic.size):
            row = []
            for c in range(self.logic.size):
                btn = QPushButton("")
                btn.setFixedSize(160, 160)
                btn.setFocusPolicy(Qt.NoFocus)
                btn.clicked.connect(lambda _, x=r, y=c: self.handle_interaction(x, y))
                self.grid.addWidget(btn, r, c)
                row.append(btn)
            self.buttons.append(row)

        self.h_layout.addLayout(self.grid)
        self.h_layout.addStretch() 

        self.main_layout.addLayout(self.h_layout)
        self.main_layout.addStretch()

        # Footer Buttons
        self.action_layout = QHBoxLayout()
        self.action_layout.setSpacing(20)
        self.action_layout.addStretch()

        self.rematch_btn = QPushButton("RESET MATCH")
        self.rematch_btn.setFixedSize(180, 52)
        self.rematch_btn.setFocusPolicy(Qt.NoFocus)
        self.rematch_btn.setStyleSheet("""
            QPushButton { 
                font-size: 15px; font-weight: bold; letter-spacing: 1px;
                background-color: #1f2833; border: 2px solid #00f2fe; 
                border-radius: 10px; color: #00f2fe; 
            } 
            QPushButton:hover { background-color: #00f2fe; color: #0b0c10; }
        """)
        self.rematch_btn.clicked.connect(self.rematch_game)
        self.action_layout.addWidget(self.rematch_btn)

        self.return_btn = QPushButton("EXIT TO MENU")
        self.return_btn.setFixedSize(180, 52)
        self.return_btn.setFocusPolicy(Qt.NoFocus)
        self.return_btn.setStyleSheet("""
            QPushButton { 
                font-size: 15px; font-weight: bold; letter-spacing: 1px;
                background-color: #1f2833; border: 2px solid #ff4757; 
                border-radius: 10px; color: #ff4757; 
            } 
            QPushButton:hover { background-color: #ff4757; color: white; }
        """)
        self.return_btn.clicked.connect(self.return_to_menu)
        self.action_layout.addWidget(self.return_btn)

        self.action_layout.addStretch()
        self.main_layout.addLayout(self.action_layout)
        self.main_layout.addStretch()
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.update_ui()

    def handle_ros_move(self, cell: int):
        """Triggered by ROS2 subscriber — converts cell (1-9) to row/col."""
        key_map = {
            1: (0, 0), 2: (0, 1), 3: (0, 2),
            4: (1, 0), 5: (1, 1), 6: (1, 2),
            7: (2, 0), 8: (2, 1), 9: (2, 2)
        }
        if cell in key_map:
            r, c = key_map[cell]
            self.handle_interaction(r, c)

    def rematch_game(self):
        self.logic = GameLogic()
        self.cursor_r, self.cursor_c = 0, 0
        self.update_ui()

    def is_ai_turn(self):
        return str(self.mode).lower() in ["single", "player vs ai"] and self.logic.current_player == "O"

    def handle_interaction(self, r, c):
        if self.is_ai_turn():
            return
        self.cursor_r, self.cursor_c = r, c

        if self.logic.make_move(r, c):
            self.update_ui()
            if self.is_ai_turn() and not self.logic.game_over:
                self.trigger_ai_move()

    def trigger_ai_move(self):
        if self.difficulty == "easy":
            ai_move = aieasy.get_move(self.logic.board, ai_marker="O", human_marker="X")
        elif self.difficulty == "medium":
            ai_move = aimedium.get_move(self.logic.board, ai_marker="O", human_marker="X")
        else:
            ai_move = aihard.get_move(self.logic.board, ai_marker="O", human_marker="X")

        if ai_move:
            ai_r, ai_c = ai_move
            self.logic.make_move(ai_r, ai_c)
            self.update_ui()

    def update_ui(self):
        if self.logic.game_over:
            self.info.setText(f"PLAYER {self.logic.winner} DOMINATES!")
            glow_color = "#00f2fe" if self.logic.winner == "X" else "#ff9f43"
            self.info.setStyleSheet(f"color: {glow_color}; font-size: 34px; font-weight: 900; letter-spacing: 3px; margin-bottom: 15px;")
        else:
            status_text = f"ACTIVE NODE: PLAYER {self.logic.current_player}"
            if str(self.mode).lower() in ["single", "player vs ai"]:
                status_text += f"   |   AI: {self.difficulty.upper()}"
            self.info.setText(status_text)
            self.info.setStyleSheet("color: #c5c6c7; font-size: 18px; font-weight: bold; letter-spacing: 1px; margin-bottom: 25px;")

        fading_piece = self.logic.get_fading_piece()

        for r in range(self.logic.size):
            for c in range(self.logic.size):
                val = self.logic.board[r][c]
                
                if fading_piece == (r, c):
                    text_color = "rgba(0, 242, 254, 0.25)" if val == "X" else "rgba(255, 159, 67, 0.25)"
                    border_style = "2px dashed #334155"
                else:
                    text_color = "#00f2fe" if val == "X" else "#ff9f43" if val == "O" else "transparent"
                    border_style = "2px solid #1f2833"

                if r == self.cursor_r and c == self.cursor_c and not self.logic.game_over:
                    border_style = "3px solid #ff007f"

                self.buttons[r][c].setText(val)
                self.buttons[r][c].setStyleSheet(f"""
                    QPushButton {{
                        font-size: 75px;
                        font-weight: 900;
                        background-color: #121821;
                        border-radius: 14px;
                        color: {text_color};
                        border: {border_style};
                    }}
                """)

    def keyPressEvent(self, event):
        if self.logic.game_over or self.is_ai_turn():
            return

        key = event.key()
        
        if key == Qt.Key_W and self.cursor_r > 0: self.cursor_r -= 1
        elif key == Qt.Key_S and self.cursor_r < self.logic.size - 1: self.cursor_r += 1
        elif key == Qt.Key_A and self.cursor_c > 0: self.cursor_c -= 1
        elif key == Qt.Key_D and self.cursor_c < self.logic.size - 1: self.cursor_c += 1
        elif key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.handle_interaction(self.cursor_r, self.cursor_c)
            
        key_map = {
            Qt.Key_1: (0, 0), Qt.Key_2: (0, 1), Qt.Key_3: (0, 2),
            Qt.Key_4: (1, 0), Qt.Key_5: (1, 1), Qt.Key_6: (1, 2),
            Qt.Key_7: (2, 0), Qt.Key_8: (2, 1), Qt.Key_9: (2, 2)
        }
        
        if key in key_map:
            target_r, target_c = key_map[key]
            self.handle_interaction(target_r, target_c)

        self.update_ui()

    def return_to_menu(self):
        if not self.logic.game_over:
            reply = QMessageBox.question(self, "Abandon?", "Disconnect from active system?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No: return

        self.is_returning_to_menu = True
        from mini_project.ui.menu import MainMenu 
        self.menu_window = MainMenu()
        self.menu_window.show()
        self.close()

    def closeEvent(self, event):
        # Cleanup ROS2 on close
        if self.ros_node is not None:
            self.ros_node.destroy_node()
            rclpy.shutdown()

        if self.is_returning_to_menu:
            event.accept()
            return
        reply = QMessageBox.question(self, "Exit", "Power down completely?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes: event.accept()
        else: event.ignore()
