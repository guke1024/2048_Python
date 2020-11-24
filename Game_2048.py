# coding: utf-8

import curses
# curses show interface
from random import randrange, choice
# 产生随机数
from collections import defaultdict
import easygui


press_dict = {'W': 'Up', 'A': 'Left', 'S': 'Down', 'D': 'Right', 'R': 'Restart', 'Q': 'Quit', 'N': 'Withdraw',
              'w': 'Up', 'a': 'Left', 's': 'Down', 'd': 'Right', 'r': 'Restart', 'q': 'Quit', 'n': 'Withdraw'}
# 用户输入：程序操作
old_board = []
w_num = 0


class Game(object):
    def __init__(self, height=4, width=4, win=2048):
        self.height = height
        # 高
        self.width = width
        # 宽
        self.win_value = win
        # 通关分数
        self.score = 0
        # 当前分数
        self.highscore = 0
        # 历史最高分
        self.reset()
        # 重新开始游戏

    def get_user_press(self, keyboard):
        # 处理用户输入
        press = ''
        while press not in press_dict:
            press = keyboard.getkey()
        return press_dict[press]
        # 返回输入对应的行为

    def reset(self):
        # 重置棋盘
        if self.score > self.highscore:
            self.highscore = self.score
        # 更新历史最高分
        self.score = 0
        self.board = [[0 for i in range(self.width)] for j in range(self.height)]
        self.spawn()
        self.spawn()
        # 初始化游戏界面

    def spawn(self):
        # 随机生成 2, 4
        new_cube = 4 if randrange(100) > 89 else 2
        (i, j) = choice([(i, j) for i in range(self.width)for j in range(self.height) if self.board[i][j] == 0])
        # 产生一个随机的元组坐标
        self.board[i][j] = new_cube

    def transpose(self, board):
        return [list(row) for row in zip(*board)]
        # 转置矩阵

    def invert(self, board):
        return [row[::-1] for row in board]
        # 逆序行

    def move(self, key_press):
        def move_left(row):
            def left_zero(row):
                # 消除左边的 0
                new_row = [i for i in row if i != 0]
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row

            def same_cube(row):
                # 合并相同数字
                flag = False
                new_row = []
                for i in range(len(row)):
                    if flag:
                        new_row.append(2 * row[i])
                        self.score += 2 * row[i]
                        if self.score > self.highscore:
                            self.highscore = self.score
                        # 更新分数
                        flag = False
                    else:
                        if i + 1 < len(row) and row[i] == row[i+1]:
                            flag = True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                return new_row
            return left_zero(same_cube(left_zero(row)))

        moves = {}
        global old_board
        global w_num
        if w_num == 0:
            old_board.append(self.board)
        if key_press == 'Withdraw':
            if len(old_board) == 1:
                easygui.msgbox("开局不允许悔棋！")
            else:
                if w_num == 0:
                    self.board = old_board[-2]
                    w_num = 1
                    return True
                else:
                    easygui.msgbox("只能悔棋一次！")
        else:
            w_num = 0
        moves['Left'] = lambda board: [move_left(row) for row in board]
        moves['Right'] = lambda board: self.invert(moves['Left'](self.invert(board)))
        moves['Up'] = lambda board: self.transpose(moves['Left'](self.transpose(board)))
        moves['Down'] = lambda board: self.transpose(moves['Right'](self.transpose(board)))
        if key_press in moves:
            if self.move_possible(key_press):
                self.board = moves[key_press](self.board)
                self.spawn()
                return True
            else:
                return False

    def move_possible(self, key_press):
        def row_left_move(row):
            # 判断能否左移或合并
            def possible(i):
                if row[i] == 0 and row[i+1] != 0:
                    # 当左边有 0， 右边有数字时，可以左移
                    return True
                if row[i] != 0 and row[i+1] == row[i]:
                    # 当左边有一个数和右边的数相等时，可以左合并
                    return True
                return False
            return any(possible(i) for i in range(len(row) - 1))

        check = {}
        check['Left'] = lambda board: any(row_left_move(row) for row in board)
        check['Right'] = lambda board: check['Left'](self.invert(board))
        check['Up'] = lambda board: check['Left'](self.transpose(board))
        check['Down'] = lambda board: check['Right'](self.transpose(board))
        if key_press in check:
            return check[key_press](self.board)
        else:
            return False

    def is_win(self):
        # 任何位置的数大于设定的 win 时， 游戏胜利
        return any(any(i >= self.win_value for i in row) for row in self.board)

    def is_gameover(self):
        # 无法移动和合并时， 游戏失败
        return not any(self.move_possible(move) for move in press_dict.values())

    def draw(self, show):
        prompt_str1 = '(W)上 移 (S)下 移 (A)左 移 (D)右 移'
        prompt_str2 = '(N)悔 棋  (R)重 新 开 始  (Q)退 出'
        gameover_str = '           游 戏 结 束'
        win_string = '          你 赢 了 ！'

        def cast(s):
            show.addstr(s + '\n')
            
        def draw_row():
            # 绘制行
            line = '+' + ('+---------' * self.width + '+')[1:]
            row = defaultdict(lambda: line)
            if not hasattr(draw_row, "counter"):
                draw_row.counter = 0
            cast(row[draw_row.counter])
            draw_row.counter += 1

        def draw_column(column):
            # 绘制列

            cast(''.join('|         ' for num in column) + '|')
            cast(''.join('| {: ^7} '.format(num) if num > 0 else '|         ' for num in column) + '|')
            cast(''.join('|         ' for num in column) + '|')

        show.clear()
        cast('分 数 : ' + str(self.score))
        cast('最 高 分 : ' + str(self.highscore))
        for column in self.board:
            # 绘制行、列、边框
            draw_row()
            draw_column(column)
        draw_row()
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_str)
            else:
                cast(prompt_str1)
        cast(prompt_str2)


def main_program(stdscr):
    def start():
        # 重置游戏
        game_limit.reset()
        return 'allGame'

    def rq_game(state):
        game_limit.draw(stdscr)
        # 画出游戏界面
        action = game_limit.get_user_press(stdscr)
        # 判断重启还是结束
        keep_now = defaultdict(lambda: state)
        keep_now['Restart'], keep_now['Quit'] = 'Limit', 'Quit'
        return keep_now[action]

    def end_game():
        game_limit.draw(stdscr)
        action = game_limit.get_user_press(stdscr)
        if action == 'Restart':
            return 'Limit'
        if action == 'Quit':
            return 'Quit'
        if game_limit.move(action):
            if game_limit.is_win():
                return 'Win'
            if game_limit.is_gameover():
                return 'Gameover'
        return 'allGame'

    state_actions = {
        'Limit': start,
        'Win': lambda: rq_game('Win'),
        'Gameover': lambda: rq_game('Gameover'),
        'allGame': end_game
        }

    curses.use_default_colors()

    game_limit = Game(win = 2048)
    state = 'Limit'
    while state != 'Quit':
        state = state_actions[state]()


curses.wrapper(main_program)
