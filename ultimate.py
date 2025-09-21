import pygame
import sys
import random
import copy

black = (0, 0, 0)
white = (255, 255, 255)
blue = (255, 0, 0)
red = (0, 0, 255)

screen_size = 600

class MiniBoard:

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size    # size of mini board
        self.cell_size = size // 3
        self.grid = [[0 for _ in range(3)] for _ in range(3)]
        self.winner = 0
        self.full = False
        self.win_line = None

    def draw(self, screen):
        for i in range(1, 3):
            pygame.draw.line(screen, black, (self.x, self.y + i * self.cell_size),
                             (self.x + self.size, self.y + i * self.cell_size))
            pygame.draw.line(screen, black, (self.x + i * self.cell_size, self.y),
                             (self.x + i * self.cell_size, self.y + self.size))
        for row in range(3):
            for col in range(3):
                value = self.grid[row][col]
                cx = self.x + col * self.cell_size + self.cell_size // 2
                cy = self.y + row * self.cell_size + self.cell_size // 2
                if value == 1:
                    offset = self.cell_size * 0.2
                    pygame.draw.line(screen, blue, (cx - offset, cy - offset), (cx + offset, cy + offset))
                    pygame.draw.line(screen, blue, (cx - offset, cy + offset), (cx + offset, cy - offset))
                elif value == 2:
                    pygame.draw.circle(screen, red, (cx, cy), int(self.cell_size * 0.25))

        if self.winner > 0 and self.win_line:
            colour = blue if self.winner == 1 else red
            lw = 3
            t, idx = self.win_line
            if t == "row":
                y = self.y + idx * self.cell_size + self.cell_size // 2
                pygame.draw.line(screen, colour, (self.x, y), (self.x + self.size, y), lw)
            elif t == "col":
                x = self.x + idx * self.cell_size + self.cell_size // 2
                pygame.draw.line(screen, colour, (x, self.y), (x, self.y + self.size), lw)
            elif t == "diag":
                if idx == 0:
                    pygame.draw.line(screen, colour, (self.x, self.y), (self.x + self.size, self.y + self.size), lw)
                else:
                    pygame.draw.line(screen, colour, (self.x + self.size, self.y), (self.x, self.y + self.size), lw)


    def mark(self, row, col, player):
        if self.grid[row][col] == 0 and self.winner == 0:
            self.grid[row][col] = player
            self.check_winner()
            return True
        return False

    def check_winner(self):
        for i in range(3):
            if self.grid[i][0] and all(self.grid[i][j] == self.grid[i][0] for j in range(3)):
                self.winner, self.win_line = self.grid[i][0], ("row", i)
            if self.grid[0][i] and all(self.grid[j][i] == self.grid[0][i] for j in range(3)):
                self.winner, self.win_line = self.grid[0][i], ("col", i)
        if self.grid[0][0] and all(self.grid[i][i] == self.grid[0][0] for i in range(3)):
            self.winner, self.win_line = self.grid[0][0], ("diag", 0)
        if self.grid[0][2] and all (self.grid[i][2-i] == self.grid[0][2] for i in range(3)):
            self.winner, self.win_line = self.grid[0][2], ("diag", 1)

        self.full = all(self.grid[r][c] != 0 for r in range(3) for c in range(3))
        if self.full and self.winner == 0:
            self.winner = -1


class UltimateBoard:

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.cell_size = size // 3

        self.boards = [[MiniBoard(x + col * self.cell_size, y + row * self.cell_size, self.cell_size)
                        for col in range(3)] for row in range(3)]
        self.winner = 0   # 1 = player, 2 = computer, -1 = tie
        self.next_board = None  # (row, col) of next allowed board, None = any
        self.full = False
        self.global_win_line = None

    def draw(self, screen):
        for row in self.boards:
            for board in row:
                board.draw(screen)
        self.highlight_move(screen)

        pygame.draw.line(screen, black, (self.x + self.cell_size, self.y),
                         (self.x + self.cell_size, self.y + self.size), 6)
        pygame.draw.line(screen, black, (self.x + 2 * self.cell_size, self.y),
                         (self.x + 2 * self.cell_size, self.y + self.size), 6)
        pygame.draw.line(screen, black, (self.x, self.y + self.cell_size),
                         (self.x + self.size, self.y + self.cell_size), 6)
        pygame.draw.line(screen, black, (self.x, self.y + 2 * self.cell_size),
                         (self.x + self.size, self.y + 2 * self.cell_size), 6)  # 6 on end for thickness

        if self.winner > 0 and self.global_win_line:
            colour = blue if self.winner == 1 else red
            lw = 10
            t, idx = self.global_win_line
            if t == "row":
                y = self.y + idx * self.cell_size + self.cell_size // 2
                pygame.draw.line(screen, colour, (self.x, y), (self.x + self.size, y), lw)
            elif t == "col":
                x = self.x + idx * self.cell_size + self.cell_size // 2
                pygame.draw.line(screen, colour, (x, self.y), (x, self.y + self.size), lw)
            elif t == "diag":
                if idx == 0:
                    pygame.draw.line(screen, colour, (self.x, self.y), (self.x + self.size, self.y + self.size), lw)
                else:
                    pygame.draw.line(screen, colour, (self.x + self.size, self.y), (self.x, self.y + self.size), lw)


    def is_valid_move(self, big_r, big_c, small_r, small_c):
        if self.winner != 0:
            return False

        if self.next_board and (big_r, big_c) != self.next_board:
            return False

        return self.boards[big_r][big_c].grid[small_r][small_c] == 0

    def make_move(self, big_r, big_c, small_r, small_c, player):
        if not self.is_valid_move(big_r, big_c, small_r, small_c):
            return False
        success = self.boards[big_r][big_c].mark(small_r, small_c, player)
        if not success:
            return False

        self.update_global_winner()

        next_board = self.boards[small_r][small_c]
        if next_board.full or next_board.winner != 0:
            self.next_board = None
        else:
            self.next_board = (small_r, small_c)
        return True

    def highlight_move(self, screen):
        if self.next_board is None or self.winner:
            return
        br, bc = self.next_board
        rect = pygame.Rect(self.x + bc * self.cell_size, self.y + br * self.cell_size, self.cell_size, self.cell_size)
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        surface.fill((255, 255, 0, 100))
        screen.blit(surface, rect.topleft)

    def evaluate(self):
        # +10 for player win, -10 for computer win.
        if self.winner == 1:
            return 10
        elif self.winner == 2:
            return -10
        else:
            return 0

    def copy(self):
        return copy.deepcopy(self)

    def update_global_winner(self):
        state = [[self.boards[r][c].winner for c in range(3)] for r in range(3)]
        print(state)

        for i in range(3):
            if state[i][0] > 0 and all(state[i][j] == state[i][0] for j in range(3)):
                self.winner = state[i][0]
                self.global_win_line = ("row", i)
            if state[0][i] > 0 and all(state[j][i] == state[0][i] for j in range(3)):
                self.winner = state[0][i]
                self.global_win_line = ("col", i)
        if state [0][0] > 0 and all(state[i][i] == state[0][0] for i in range(3)):
            self.winner = state[0][0]
            self.global_win_line = ("diag", 0)
        if state[0][2] > 0 and all(state[i][2-i] == state[0][2] for i in range(3)):
            self.winner = state[0][2]
            self.global_win_line = ("diag", 1)

        self.full = all(b.full or b.winner for row in self.boards for b in row)
        if self.full and self.winner == 0:
            self.winner = -1


class Game:

    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((screen_size, screen_size))
        pygame.display.set_caption("Ultimate Tic Tac Toe")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.board = UltimateBoard(0, 0, screen_size)
        self.running = True
        self.game_over = False
        self.current_player = 1
        self.message = ""

    def run(self):
        while self.running:
            self.handle_events()

            if not self.game_over and self.current_player == 2:
                pygame.time.wait(300)
                self.make_ai_move()

            self.screen.fill(white)
            self.board.draw(self.screen)

            if self.game_over:
                self.draw_message()

            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and self.current_player == 1:
                x, y = pygame.mouse.get_pos()
                big_r = y // (screen_size // 3)
                big_c = x // (screen_size // 3)
                small_r = (y % (screen_size // 3)) // (screen_size // 9)
                small_c = (x % (screen_size // 3)) // (screen_size // 9)

                if self.board.make_move(big_r, big_c, small_r, small_c, 1):
                    self.check_game_over()
                    if not self.game_over:
                        self.current_player = 2

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__init__()

    def make_ai_move(self):
        legal_moves = []
        for big_r in range(3):
            for big_c in range(3):
                mini = self.board.boards[big_r][big_c]
                if mini.full or mini.winner:
                    continue

                for small_r in range(3):
                    for small_c in range(3):
                        if mini.grid[small_r][small_c] == 0:
                            if self.board.is_valid_move(big_r, big_c, small_r, small_c):
                                legal_moves.append((big_r, big_c, small_r, small_c))

        if legal_moves:
            move = random.choice(legal_moves)
            _, best_move = minimax(self.board, depth=5, maximizing_player=False)    # change depth, lower for quicker but easier
            if best_move:
                self.board.make_move(*best_move, 2)
                self.check_game_over()
                if not self.game_over:
                    self.current_player = 1

    def check_game_over(self):
        if self.board.winner == 1:
            self.message = "You win"
            self.game_over = True
        elif self.board.winner == 2:
            self.message = "Computer wins"
            self.game_over = True
        elif self.board.winner == -1:
            self.message = "Tie"
            self.game_over = True

    def draw_message(self):
        text_surf = self.font.render(self.message, True, black)
        text_rect = text_surf.get_rect(center = (screen_size // 2, screen_size // 2))
        self.screen.blit(text_surf, text_rect)


def minimax(board, depth, maximizing_player):
    if board.winner or depth == 0:
        return board.evaluate(), None

    legal_moves = []
    for br in range(3):
        for bc in range(3):
            mini = board.boards[br][bc]
            if mini.full or mini.winner:
                continue
            for sr in range(3):
                for sc in range(3):
                    if mini.grid[sr][sc] == 0:
                        if board.is_valid_move(br, bc, sr, sc):
                            legal_moves.append((br, bc, sr, sc))
    if not legal_moves:
        return 0, None

    if maximizing_player:
        best_value = -float("inf")
        best_move = None
        for move in legal_moves:
            clone = board.copy()
            clone.make_move(*move, 1)
            val, _ = minimax(clone, depth - 1, False)
            if val > best_value:
                best_value = val
                best_move = move
        return best_value, best_move
    else:
        best_value = float("inf")
        best_move = None
        for move in legal_moves:
            clone = board.copy()
            clone.make_move(*move, 2)
            val, _ = minimax(clone, depth - 1, True)
            if val < best_value:
                best_value = val
                best_move = move
        return best_value, best_move


if __name__ == "__main__":
    print("Test")
    game = Game()
    game.run()
    pygame.quit()

    sys.exit()
