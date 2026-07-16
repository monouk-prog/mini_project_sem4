import pygame
import sys
import math
import random
from mini_project.game.logic import GameLogic
import mini_project.ai.easy as aieasy
import mini_project.ai.medium as aimedium
import mini_project.ai.hard as aihard



class TicTacToe3D:
    """
    Main game class handling rendering, input, and 3D projection.
    All game objects exist in 3D space and are projected to screen coordinates.
    """

    def __init__(self,settings):
        """Initialize Pygame, display, and game state."""
        pygame.init()

        # Display configuration
        self.display_info = pygame.display.Info()
        self.screen_width = self.display_info.current_w
        self.screen_height = self.display_info.current_h

        self.fullscreen = True
        self.width = self.screen_width
        self.height = self.screen_height
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.FULLSCREEN
        )
        pygame.display.set_caption("3D Tic Tac Toe")

        # Game settings
        self.settings = settings
        self.mode = settings["mode"]
        self.difficulty = settings.get("difficulty","easy")
        self.size = 3
        
        # Scaling and sizing
        self.scale = min(self.width, self.height) / 900
        self.cell_size = int(130 * self.scale)
        self.board_size = self.size * self.cell_size
        self.half_board = self.board_size / 2

        # Camera settings
        self.camera_distance = int(900 * self.scale)
        self.center_x = self.width // 2
        self.center_y = self.height // 2 - int(20 * self.scale)

        # Rotation angles (degrees)
        self.rot_x = 25          # Current tilt
        self.rot_y = 45          # Current rotation
        self.rot_z = 0
        self.target_rot_x = 25   # Smooth interpolation targets
        self.target_rot_y = 45

        # Colors
        self.colors = {
            'background': (11, 12, 16),
            'bg_stars': (30, 35, 45),
            'board_top': (25, 35, 55),
            'board_bottom': (15, 20, 35),
            'board_edge': (40, 60, 90),
            'cell_normal': (30, 42, 65),
            'cell_hover': (45, 60, 90),
            'grid_line': (60, 80, 120),
            'x': (0, 242, 254),
            'o': (255, 159, 67),
            'cursor': (255, 0, 127),
            'text': (197, 198, 199),
            'winner_x': (0, 242, 254),
            'winner_o': (255, 159, 67),
            'button': (31, 40, 51),
            'button_hover': (43, 53, 70),
            'button_reset': (0, 242, 254),
            'button_reset_hover': (100, 242, 254),
            'button_text': (197, 198, 199),
            'grid': (60, 80, 120),
        }

        # Game state
        self.logic = GameLogic()
        self.cursor_r = 1
        self.cursor_c = 1
        self.fading_piece = None

        # Animation
        self.cursor_pulse = 0
        self.cursor_direction = 1
        self.particles = []
        self._create_particles()

        # UI Buttons
        self.buttons = {}
        self._create_buttons()

        # Fonts
        self.font_large = pygame.font.Font(None, int(56 * self.scale))
        self.font_medium = pygame.font.Font(None, int(36 * self.scale))
        self.font_small = pygame.font.Font(None, int(24 * self.scale))
        self.font_button = pygame.font.Font(None, int(28 * self.scale))

        # Mouse interaction
        self.dragging = False
        self.last_mouse_pos = None

        # Game loop control
        self.running = True
        self.clock = pygame.time.Clock()

        self._print_controls()

    # ========================================================================
    # INITIALIZATION HELPERS
    # ========================================================================

    def _create_particles(self):
        """Create background star particles."""
        for _ in range(80):
            self.particles.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.1, 0.5)
            })

    def _create_buttons(self):
        """Create UI button definitions."""
        btn_width = int(130 * self.scale)
        btn_height = int(42 * self.scale)
        small_btn_width = int(60 * self.scale)
        tilt_btn_width = int(50 * self.scale)
        tilt_btn_height = int(40 * self.scale)

        self.buttons = {
            'reset': {
                'rect': pygame.Rect(
                    int(20 * self.scale),
                    self.height - int(60 * self.scale),
                    btn_width, btn_height
                ),
                'text': 'RESET',
                'hover': False
            },
            'rotate_left': {
                'rect': pygame.Rect(
                    self.width // 2 - int(100 * self.scale),
                    self.height - int(60 * self.scale),
                    small_btn_width, btn_height
                ),
                'text': '<',
                'hover': False
            },
            'rotate_right': {
                'rect': pygame.Rect(
                    self.width // 2 + int(40 * self.scale),
                    self.height - int(60 * self.scale),
                    small_btn_width, btn_height
                ),
                'text': '>',
                'hover': False
            },
            'rotate_180': {
                'rect': pygame.Rect(
                    self.width // 2 - int(50 * self.scale),
                    self.height - int(115 * self.scale),
                    int(100 * self.scale), int(40 * self.scale)
                ),
                'text': '180',
                'hover': False
            },
            'tilt_up': {
                'rect': pygame.Rect(
                    self.width - int(150 * self.scale),
                    self.height // 2 - int(50 * self.scale),
                    tilt_btn_width, tilt_btn_height
                ),
                'text': '^',
                'hover': False
            },
            'tilt_down': {
                'rect': pygame.Rect(
                    self.width - int(150 * self.scale),
                    self.height // 2 + int(10 * self.scale),
                    tilt_btn_width, tilt_btn_height
                ),
                'text': 'v',
                'hover': False
            }
        }

    def _print_controls(self):
        """Print control instructions to console."""
        print("\n" + "="*60)
        print("3D TIC TAC TOE - FULL SCREEN")
        print("="*60)
        print("HOW TO PLAY:")
        print("  Arrow Keys  : Move cursor")
        print("  Enter/Space : Place piece")
        print("  A/D         : Rotate board left/right")
        print("  R           : Rotate board 180 degrees")
        print("  Q/E         : Tilt up/down")
        print("  Mouse Drag  : Free rotation")
        print("  Mouse Click : Select and place")
        print("  F           : Toggle Full Screen")
        print("  ESC         : Exit")
        print("="*60)
        print("RULES:")
        print("  - First to get 3 in a row wins")
        print("  - Only 3 pieces per player on board")
        print("  - Oldest piece fades and is removed")
        print("="*60)
        print("Starting game...\n")

    # ========================================================================
    # 3D MATH FUNCTIONS
    # ========================================================================

    def _rotate_point_3d(self, x, y, z, rot_x, rot_y, rot_z):
        """
        Rotate a 3D point around the origin using Euler angles.

        Args:
            x, y, z: 3D coordinates
            rot_x, rot_y, rot_z: Rotation angles in degrees

        Returns:
            tuple: Rotated (x, y, z) coordinates
        """
        # Convert to radians
        rx = math.radians(rot_x)
        ry = math.radians(rot_y)
        rz = math.radians(rot_z)

        # Rotate around X axis
        cos_x, sin_x = math.cos(rx), math.sin(rx)
        y1 = y * cos_x - z * sin_x
        z1 = y * sin_x + z * cos_x
        y, z = y1, z1

        # Rotate around Y axis
        cos_y, sin_y = math.cos(ry), math.sin(ry)
        x1 = x * cos_y + z * sin_y
        z1 = -x * sin_y + z * cos_y
        x, z = x1, z1

        # Rotate around Z axis
        cos_z, sin_z = math.cos(rz), math.sin(rz)
        x1 = x * cos_z - y * sin_z
        y1 = x * sin_z + y * cos_z
        x, y = x1, y1

        return x, y, z

    def _project_3d_to_2d(self, x, y, z):
        """
        Project a 3D point to 2D screen coordinates using perspective projection.

        Args:
            x, y, z: 3D coordinates

        Returns:
            tuple: (screen_x, screen_y, scale_factor)
        """
        # Apply rotation
        x_rot, y_rot, z_rot = self._rotate_point_3d(
            x, y, z, self.rot_x, self.rot_y, self.rot_z
        )

        # Perspective projection
        scale = self.camera_distance / (self.camera_distance + z_rot)
        screen_x = self.center_x + x_rot * scale
        screen_y = self.center_y + y_rot * scale

        return (int(screen_x), int(screen_y), scale)

    def _get_cell_3d_position(self, row, col):
        """
        Get the 3D position of a cell center.

        Args:
            row, col: Cell indices (0-2)

        Returns:
            tuple: (x, y, z) in board space
        """
        # Center the board at origin
        offset = (self.size - 1) * self.cell_size / 2
        x = col * self.cell_size - offset
        y = row * self.cell_size - offset
        z = 0
        return x, y, z

    # ========================================================================
    # RENDERING FUNCTIONS
    # ========================================================================

    def _draw_background(self):
        """Draw the background with animated star particles."""
        self.screen.fill(self.colors['background'])

        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                self.colors['bg_stars'],
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
            particle['y'] += particle['speed']
            if particle['y'] > self.height:
                particle['y'] = 0
                particle['x'] = random.randint(0, self.width)

    def _draw_board_3d(self):
        """
        Draw the 3D board as a flat plane with depth.
        The board is rendered using 8 corner points in 3D space.
        """
        half = self.half_board + int(20 * self.scale)

        # Define board corners in 3D space
        # Bottom face (z = -10) and top face (z = 0)
        corners_3d = [
            (-half, -half, -10), (half, -half, -10),
            (half, half, -10), (-half, half, -10),
            (-half, -half, 0), (half, -half, 0),
            (half, half, 0), (-half, half, 0),
        ]

        # Project corners to 2D
        corners_2d = []
        for x, y, z in corners_3d:
            sx, sy, _ = self._project_3d_to_2d(x, y, z)
            corners_2d.append((sx, sy))

        # Draw bottom face (back of board)
        pygame.draw.polygon(
            self.screen, self.colors['board_bottom'],
            [corners_2d[0], corners_2d[1], corners_2d[2], corners_2d[3]]
        )

        # Draw top face (front of board)
        pygame.draw.polygon(
            self.screen, self.colors['board_top'],
            [corners_2d[4], corners_2d[5], corners_2d[6], corners_2d[7]]
        )

        # Draw side faces for 3D depth effect
        side_faces = [
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7]
        ]
        for face in side_faces:
            pygame.draw.polygon(
                self.screen, self.colors['board_edge'],
                [corners_2d[i] for i in face]
            )

        # Draw board outline on top face
        pygame.draw.polygon(
            self.screen, self.colors['board_edge'],
            [corners_2d[4], corners_2d[5], corners_2d[6], corners_2d[7]], 2
        )

    def _draw_cell_3d(self, row, col):
        """
        Draw a single cell with its contents in 3D space.

        Args:
            row, col: Cell indices
        """
        # Get cell position in 3D space
        x, y, z = self._get_cell_3d_position(row, col)
        half = (self.cell_size - int(8 * self.scale)) / 2

        # Define cell corners in 3D space (slightly above board surface)
        corners_3d = [
            (x - half, y - half, 2),
            (x + half, y - half, 2),
            (x + half, y + half, 2),
            (x - half, y + half, 2),
        ]

        # Project corners to 2D
        corners_2d = []
        for cx, cy, cz in corners_3d:
            sx, sy, _ = self._project_3d_to_2d(cx, cy, cz)
            corners_2d.append((sx, sy))

        # Determine cell state
        is_hover = (
            row == self.cursor_r and
            col == self.cursor_c and
            not self.logic.game_over
        )
        value = self.logic.board[row][col]
        is_fading = self.fading_piece and self.fading_piece == (row, col)

        # Cell color with hover pulse animation
        if is_hover:
            pulse = 0.5 + 0.5 * math.sin(self.cursor_pulse)
            color = (
                int(45 + 30 * pulse),
                int(60 + 30 * pulse),
                int(90 + 30 * pulse)
            )
        else:
            color = self.colors['cell_normal']

        # Draw cell face
        pygame.draw.polygon(self.screen, color, corners_2d)
        pygame.draw.polygon(self.screen, self.colors['grid_line'], corners_2d, 2)

        # Draw piece if cell is occupied
        if value != " ":
            self._draw_piece_3d(x, y, z, value, is_fading)

        # Draw cursor highlight on cell edges
        if is_hover:
            pulse = 0.5 + 0.5 * math.sin(self.cursor_pulse)
            glow_size = int(8 * pulse * self.scale)
            for i in range(4):
                start = corners_2d[i]
                end = corners_2d[(i + 1) % 4]
                pygame.draw.line(
                    self.screen, self.colors['cursor'],
                    start, end, glow_size + 1
                )

    def _draw_piece_3d(self, x, y, z, value, is_fading):
        """
        Draw a piece (X or O) in 3D space using projected points.

        Args:
            x, y, z: 3D position of the piece center
            value: 'X' or 'O'
            is_fading: Whether the piece should be drawn faded
        """
        # Project the center to get screen position and scale
        cx, cy, scale = self._project_3d_to_2d(x, y, z)

        # Size based on perspective scale
        piece_size = int(35 * scale * self.scale)

        # Determine color with optional fading
        if value == "X":
            color = self.colors['x']
            if is_fading:
                # Alpha blending for fading - draw with transparency
                color = (color[0], color[1], color[2], 64)
        else:  # "O"
            color = self.colors['o']
            if is_fading:
                color = (color[0], color[1], color[2], 64)

        if value == "X":
            # Draw X as two diagonal lines in 3D space
            # Define line endpoints in 3D space
            # Line 1: top-left to bottom-right
            p1 = self._project_3d_to_2d(x - piece_size, y - piece_size, z)
            p2 = self._project_3d_to_2d(x + piece_size, y + piece_size, z)
            # Line 2: top-right to bottom-left
            p3 = self._project_3d_to_2d(x + piece_size, y - piece_size, z)
            p4 = self._project_3d_to_2d(x - piece_size, y + piece_size, z)

            line_width = int(4 * self.scale)
            pygame.draw.line(self.screen, color, (p1[0], p1[1]), (p2[0], p2[1]), line_width)
            pygame.draw.line(self.screen, color, (p3[0], p3[1]), (p4[0], p4[1]), line_width)

        else:  # "O"
            # Draw O as a circle approximated by projected points
            # Generate points in 3D space around the center
            num_points = 48
            points_3d = []
            radius = piece_size

            for i in range(num_points):
                angle = 2 * math.pi * i / num_points
                px = x + radius * math.cos(angle)
                py = y + radius * math.sin(angle)
                points_3d.append((px, py, z))

            # Project all points to 2D
            points_2d = []
            for px, py, pz in points_3d:
                sx, sy, _ = self._project_3d_to_2d(px, py, pz)
                points_2d.append((sx, sy))

            # Draw the circle using lines
            if len(points_2d) > 2:
                line_width = int(4 * self.scale)
                pygame.draw.lines(
                    self.screen, color, True, points_2d, line_width
                )

    def _draw_grid_lines(self):
        """Draw grid lines on the board surface."""
        # Horizontal grid lines
        for r in range(1, self.size):
            x1, y1, z1 = self._get_cell_3d_position(r - 0.5, 0)
            x2, y2, z2 = self._get_cell_3d_position(r - 0.5, self.size - 1)

            p1 = self._project_3d_to_2d(x1, y1, z1)
            p2 = self._project_3d_to_2d(x2, y2, z2)

            pygame.draw.line(
                self.screen, self.colors['grid_line'],
                (p1[0], p1[1]), (p2[0], p2[1]), 2
            )

        # Vertical grid lines
        for c in range(1, self.size):
            x1, y1, z1 = self._get_cell_3d_position(0, c - 0.5)
            x2, y2, z2 = self._get_cell_3d_position(self.size - 1, c - 0.5)

            p1 = self._project_3d_to_2d(x1, y1, z1)
            p2 = self._project_3d_to_2d(x2, y2, z2)

            pygame.draw.line(
                self.screen, self.colors['grid_line'],
                (p1[0], p1[1]), (p2[0], p2[1]), 2
            )

    def _draw_info(self):
        """Draw game status information."""
        if self.logic.game_over and self.logic.winner:
            text = f"PLAYER {self.logic.winner} WINS!"
            color = (
                self.colors['winner_x']
                if self.logic.winner == "X"
                else self.colors['winner_o']
            )
        elif self.logic.game_over:
            text = "DRAW!"
            color = self.colors['text']
        else:
            text = f"Player {self.logic.current_player}'s Turn"
            color = self.colors['text']

        status = self.font_large.render(text, True, color)
        status_rect = status.get_rect(center=(self.width // 2, int(40 * self.scale)))
        self.screen.blit(status, status_rect)

        # Controls hint
        controls = (
            "Arrow Keys: Move | Enter/Space: Place | "
            "A/D: Rotate | R: 180 | F: Fullscreen"
        )
        controls_surface = self.font_small.render(controls, True, self.colors['text'])
        controls_rect = controls_surface.get_rect(
            center=(self.width // 2, int(85 * self.scale))
        )
        self.screen.blit(controls_surface, controls_rect)

        # Rotation info
        rot_text = (
            f"Rotation: {int(self.rot_y) % 360} | Tilt: {int(self.rot_x)}"
        )
        rot_surface = self.font_small.render(rot_text, True, self.colors['text'])
        rot_rect = rot_surface.get_rect(
            center=(self.width // 2, self.height - int(80 * self.scale))
        )
        self.screen.blit(rot_surface, rot_rect)

    def _draw_buttons(self):
        """Draw all UI buttons."""
        for key, btn in self.buttons.items():
            if key == 'reset':
                color = (
                    self.colors['button_reset_hover']
                    if btn['hover']
                    else self.colors['button_reset']
                )
                pygame.draw.rect(self.screen, color, btn['rect'], border_radius=5)
                text = self.font_button.render(btn['text'], True, (0, 0, 0))
                text_rect = text.get_rect(center=btn['rect'].center)
                self.screen.blit(text, text_rect)

            else:
                color = (
                    self.colors['button_hover']
                    if btn['hover']
                    else self.colors['button']
                )
                pygame.draw.rect(self.screen, color, btn['rect'], border_radius=5)
                pygame.draw.rect(self.screen, self.colors['grid'], btn['rect'], 1, border_radius=5)
                text = self.font_medium.render(btn['text'], True, self.colors['text'])
                text_rect = text.get_rect(center=btn['rect'].center)
                self.screen.blit(text, text_rect)

    # ========================================================================
    # INTERACTION FUNCTIONS
    # ========================================================================

    def _get_cell_from_mouse(self, mouse_x, mouse_y):
        """
        Find which cell the mouse is pointing at using distance checking
        on projected cell centers.

        Args:
            mouse_x, mouse_y: Mouse screen coordinates

        Returns:
            tuple: (row, col) or None if no cell selected
        """
        min_dist = float('inf')
        selected = None

        for r in range(self.size):
            for c in range(self.size):
                x, y, z = self._get_cell_3d_position(r, c)
                sx, sy, scale = self._project_3d_to_2d(x, y, z)

                dist = ((mouse_x - sx) ** 2 + (mouse_y - sy) ** 2) ** 0.5
                cell_hit_radius = self.cell_size * scale / 2

                if dist < cell_hit_radius and dist < min_dist:
                    min_dist = dist
                    selected = (r, c)

        return selected

    def _toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.FULLSCREEN
            )
            self.width = self.screen_width
            self.height = self.screen_height
        else:
            self.width = int(self.screen_width * 0.8)
            self.height = int(self.screen_height * 0.8)
            self.screen = pygame.display.set_mode(
                (self.width, self.height),
                pygame.RESIZABLE
            )

        self.center_x = self.width // 2
        self.center_y = self.height // 2 - int(20 * self.scale)
        self._create_buttons()

    # ========================================================================
    # EVENT HANDLING
    # ========================================================================

    def _handle_events(self):
        """Process all input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                self.width = event.w
                self.height = event.h
                self.screen = pygame.display.set_mode(
                    (self.width, self.height),
                    pygame.RESIZABLE
                )
                self.center_x = self.width // 2
                self.center_y = self.height // 2 - int(20 * self.scale)
                self.scale = min(self.width, self.height) / 900
                self.cell_size = int(130 * self.scale)
                self.board_size = self.size * self.cell_size
                self.camera_distance = int(900 * self.scale)
                self._create_buttons()

            elif event.type == pygame.MOUSEMOTION:
                # Update button hover states
                for key in self.buttons:
                    self.buttons[key]['hover'] = (
                        self.buttons[key]['rect'].collidepoint(event.pos)
                    )

                # Handle mouse drag for rotation
                if self.dragging and self.last_mouse_pos:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    # Clamp rotation to prevent going behind the board
                    self.target_rot_y += dx * 0.3
                    self.target_rot_y = max(-80, min(80, self.target_rot_y))
                    self.target_rot_x += dy * 0.3
                    self.target_rot_x = max(-60, min(60, self.target_rot_x))
                    self.last_mouse_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check button clicks
                    for key, btn in self.buttons.items():
                        if btn['rect'].collidepoint(event.pos):
                            if key == 'reset':
                                self.logic.reset()
                                self.fading_piece = None
                                return
                            elif key == 'rotate_left':
                                # Rotate left (negative direction)
                                self.target_rot_y -= 15
                                self.target_rot_y = max(-80, min(80, self.target_rot_y))
                                return
                            elif key == 'rotate_right':
                                # Rotate right (positive direction)
                                self.target_rot_y += 15
                                self.target_rot_y = max(-80, min(80, self.target_rot_y))
                                return
                            elif key == 'rotate_180':
                                # Instead of full 180, just flip to the other side
                                if self.target_rot_y >= 0:
                                    self.target_rot_y = -30
                                else:
                                    self.target_rot_y = 30
                                return
                            elif key == 'tilt_up':
                                self.target_rot_x = max(-60, self.target_rot_x - 10)
                                return
                            elif key == 'tilt_down':
                                self.target_rot_x = min(60, self.target_rot_x + 10)
                                return

                    # Check cell selection
                    if not self.logic.game_over:
                        cell = self._get_cell_from_mouse(
                            event.pos[0], event.pos[1]
                        )
                        if cell:
                            r, c = cell
                            self.cursor_r, self.cursor_c = r, c
                            if self.logic.board[r][c] == " ":
                                self.logic.make_move(r, c)
                                if self.is_ai_turn() and not self.logic.game_over:
                                    self.trigger_ai_move()
                                self.fading_piece = self.logic.get_fading_piece()

                    # Start drag
                    self.dragging = True
                    self.last_mouse_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
                    self.last_mouse_pos = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return

                elif event.key == pygame.K_f:
                    self._toggle_fullscreen()

                elif event.key == pygame.K_UP:
                    self.cursor_r = max(0, self.cursor_r - 1)
                elif event.key == pygame.K_DOWN:
                    self.cursor_r = min(self.size - 1, self.cursor_r + 1)
                elif event.key == pygame.K_LEFT:
                    self.cursor_c = max(0, self.cursor_c - 1)
                elif event.key == pygame.K_RIGHT:
                    self.cursor_c = min(self.size - 1, self.cursor_c + 1)

                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    if not self.logic.game_over:
                        r, c = self.cursor_r, self.cursor_c
                        if self.logic.board[r][c] == " ":
                            self.logic.make_move(r, c)
                            self.fading_piece = self.logic.get_fading_piece()

                # A key - rotate left
                elif event.key == pygame.K_a:
                    self.target_rot_y -= 15
                    self.target_rot_y = max(-80, min(80, self.target_rot_y))

                # D key - rotate right
                elif event.key == pygame.K_d:
                    self.target_rot_y += 15
                    self.target_rot_y = max(-80, min(80, self.target_rot_y))

                elif event.key == pygame.K_r:
                    # Instead of full 180, just flip to the other side
                    if self.target_rot_y >= 0:
                        self.target_rot_y = -30
                    else:
                        self.target_rot_y = 30

                elif event.key == pygame.K_q:
                    self.target_rot_x = max(-60, self.target_rot_x - 10)
                elif event.key == pygame.K_e:
                    self.target_rot_x = min(60, self.target_rot_x + 10)

                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3,
                                   pygame.K_4, pygame.K_5, pygame.K_6,
                                   pygame.K_7, pygame.K_8, pygame.K_9]:
                    num = event.key - pygame.K_1
                    r = num // 3
                    c = num % 3
                    if not self.logic.game_over and self.logic.board[r][c] == " ":
                        self.logic.make_move(r, c)
                        self.fading_piece = self.logic.get_fading_piece()
                        self.cursor_r, self.cursor_c = r, c

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

    def is_ai_turn(self):
        return str(self.mode).lower() in ["single","player vs ai"] and self.logic.current_player == "O"

    # ========================================================================
    # MAIN LOOP
    # ========================================================================

    def render(self):
        """
        Render a single frame.
        Rendering order: Background -> Board -> Grid -> Pieces -> Cursor -> UI
        """
        # Update cursor pulse animation
        self.cursor_pulse += 0.05 * self.cursor_direction
        if self.cursor_pulse > 1 or self.cursor_pulse < 0:
            self.cursor_direction *= -1

        # Smooth camera interpolation with clamping
        self.rot_x += (self.target_rot_x - self.rot_x) * 0.05
        self.rot_y += (self.target_rot_y - self.rot_y) * 0.05
        
        # Clamp rotation to prevent going behind the board
        self.rot_y = max(-80, min(80, self.rot_y))
        self.rot_x = max(-60, min(60, self.rot_x))

        # Draw in correct order
        self._draw_background()
        self._draw_board_3d()

        # Draw grid lines and cells
        for r in range(self.size):
            for c in range(self.size):
                self._draw_cell_3d(r, c)

        # Draw grid lines on top
        self._draw_grid_lines()

        # Draw UI overlay
        self._draw_info()
        self._draw_buttons()

        pygame.display.flip()
        self.clock.tick(60)

    def run(self):
        """Main game loop."""
        while self.running:
            self._handle_events()
            self.render()

        pygame.quit()
        sys.exit()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    game = TicTacToe3D()
    game.run()
