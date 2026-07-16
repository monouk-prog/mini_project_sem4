import rclpy
from rclpy.node import Node
from tictactoe_msgs.msg import TicTacToeMove
import sys
import tty
import termios

class KeyboardPublisher(Node):
    def __init__(self):
        super().__init__('keyboard_publisher')
        self.publisher = self.create_publisher(TicTacToeMove, 'tictactoe/move', 10)
        self.get_logger().info('Keyboard publisher ready. Press 1-9 to play, q to quit.')

    def publish_move(self, cell: int):
        msg = TicTacToeMove()
        msg.board_state = ''
        msg.player_symbol = ''
        msg.selected_cell = cell
        msg.game_status = 'ongoing'
        msg.winner = ''
        self.publisher.publish(msg)
        self.get_logger().info(f'Sent cell: {cell}')

def get_keypress():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardPublisher()

    print("Press 1-9 to select cell, q to quit")
    try:
        while rclpy.ok():
            key = get_keypress()
            if key == 'q':
                break
            if key in '123456789':
                node.publish_move(int(key))
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
