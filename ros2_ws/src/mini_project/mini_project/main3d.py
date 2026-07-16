#!/usr/bin/env python3
"""
=============================================================================
                    3D TIC TAC TOE - MAIN ENTRY POINT
=============================================================================
This is the main entry point for the 3D Tic Tac Toe game.
It initializes and runs the game.
=============================================================================
"""

import sys
import pygame
from ui.game3d import TicTacToe3D


def main():
    """
    Main function to start the game.
    Handles any potential initialization errors.
    """
    try:
        # Initialize and run the game
        game = TicTacToe3D()
        game.run()
        
    except pygame.error as e:
        print(f"Pygame initialization error: {e}")
        print("Please make sure pygame is properly installed.")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
        sys.exit(0)
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
