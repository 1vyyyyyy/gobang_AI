from graphics import *
from math import *
import threading
import sched
import time
from multiprocessing import Manager
from config import *
from gobang_algs import *

ai_list = []  # AI
human_list = []  # human
ai_and_human_list = []  # all

list_all = []  # 整个棋盘的点
next_point = [0, 0]  # AI下一步最应该下的位置

# 添加锅棋的选项：添加回棋机制
history = []  # 用于记录每一步下棋的历史
lock = threading.Lock()  # 用于人机平行操作时的严格锁定
scheduler = sched.scheduler(time.time, time.sleep)  # 用于操作调度

# 用于存储提示元素
hint_items = []

def ai():
    global cut_count   # 统计剪枝次数
    cut_count = 0
    global search_count   # 统计搜索次数
    search_count = 0
    with lock:
        negamax(True, DEPTH, -99999999, 99999999)
        history.append((next_point[0], next_point[1], "AI"))  # 记录AI下棋

    print("本次共剪枝次数：" + str(cut_count))
    print("本次共搜索次数：" + str(search_count))
    return next_point[0], next_point[1]

# 负值极大算法搜索 alpha + beta剪枝
def negamax(is_ai, depth, alpha, beta):
    # 游戏是否结束 | | 探索的递归深度是否到边界
    if game_win(ai_list) or game_win(human_list) or depth == 0:
        return evaluation(is_ai, ai_list, human_list)

    blank_list = list(set(list_all).difference(set(ai_and_human_list)))
    order(blank_list, ai_and_human_list)   # 搜索顺序排序  提高剪枝效率
    # 遍历每一个候选步
    for next_step in blank_list:

        global search_count
        search_count += 1

        # 如果要评估的位置没有相邻的子， 则不去评估  减少计算
        if not has_neighbor(next_step, ai_and_human_list):
            continue

        if is_ai:
            ai_list.append(next_step)
        else:
            human_list.append(next_step)
        ai_and_human_list.append(next_step)

        value = -negamax(not is_ai, depth - 1, -beta, -alpha)
        if is_ai:
            ai_list.remove(next_step)
        else:
            human_list.remove(next_step)
        ai_and_human_list.remove(next_step)

        if value > alpha:

            # print(str(value) + "alpha:" + str(alpha) + "beta:" + str(beta))
            # print(ai_and_human_list)
            if depth == DEPTH:
                next_point[0] = next_step[0]
                next_point[1] = next_step[1]
            # alpha + beta剪枝点
            if value >= beta:
                global cut_count
                cut_count += 1
                return beta
            alpha = value

    return alpha

def game():
    win = GraphWin("This is a gobang game", GRID_WIDTH * COLUMN, GRID_WIDTH * ROW)
    win.setBackground("yellow")

    i1 = 0

    while i1 <= GRID_WIDTH * COLUMN:
        l = Line(Point(i1, 0), Point(i1, GRID_WIDTH * COLUMN))
        l.draw(win)
        i1 = i1 + GRID_WIDTH
    i2 = 0

    while i2 <= GRID_WIDTH * ROW:
        l = Line(Point(0, i2), Point(GRID_WIDTH * ROW, i2))
        l.draw(win)
        i2 = i2 + GRID_WIDTH
    return win

def game_entry():
    win = game()

    for i in range(COLUMN + 1):
        for j in range(ROW + 1):
            list_all.append((i, j))

    change = 0
    g = 0

    # 人机对战模式
    def human_turn():
        p2 = win.getMouse()
        a2 = round((p2.getX()) / GRID_WIDTH)
        b2 = round((p2.getY()) / GRID_WIDTH)
        if (a2, b2) not in ai_and_human_list:
            with lock:
                human_list.append((a2, b2))
                ai_and_human_list.append((a2, b2))
                history.append((a2, b2, "Human"))
                piece = Circle(Point(GRID_WIDTH * a2, GRID_WIDTH * b2), 16)
                piece.setFill('black')
                piece.draw(win)

                if game_win(human_list):
                    message = Text(Point(100, 100), "Black wins.")
                    message.draw(win)
                    return True
        return False

    def ai_turn():
        pos = ai()
        with lock:
            ai_list.append(pos)
            ai_and_human_list.append(pos)
            piece = Circle(Point(GRID_WIDTH * pos[0], GRID_WIDTH * pos[1]), 16)
            piece.setFill('white')
            piece.draw(win)

            if game_win(ai_list):
                message = Text(Point(100, 100), "White wins.")
                message.draw(win)
                return True
        return False

    # 让两人对战
    def two_player_turn():
        p2 = win.getMouse()
        a2 = round((p2.getX()) / GRID_WIDTH)
        b2 = round((p2.getY()) / GRID_WIDTH)
        if (a2, b2) not in ai_and_human_list:
            with lock:
                if change % 2 == 0:  # Player 1's turn
                    human_list.append((a2, b2))
                    history.append((a2, b2, "Player 1"))
                    piece = Circle(Point(GRID_WIDTH * a2, GRID_WIDTH * b2), 16)
                    piece.setFill('black')
                    piece.draw(win)
                else:  # Player 2's turn
                    ai_list.append((a2, b2))
                    history.append((a2, b2, "Player 2"))
                    piece = Circle(Point(GRID_WIDTH * a2, GRID_WIDTH * b2), 16)
                    piece.setFill('white')
                    piece.draw(win)

                ai_and_human_list.append((a2, b2))

                if game_win(human_list):
                    message = Text(Point(100, 100), "Player 1 wins.")
                    message.draw(win)
                    return True
                if game_win(ai_list):
                    message = Text(Point(100, 100), "Player 2 wins.")
                    message.draw(win)
                    return True
        return False

    # 添加回棋功能
    def undo():
        # 在回棋前清除提示
        clear_previous_hint()

        print(history)
        print("Undo success")
        if history:  # 确保有历史记录
            with lock:
                last_move = history.pop()  # 取出最后一步
                x, y, player = last_move

                # 从对应列表中移除该步
                if player == "Human" or player == "Player 1":
                    if (x, y) in human_list:
                        human_list.remove((x, y))
                else:
                    if (x, y) in ai_list:
                        ai_list.remove((x, y))

                if(x, y) in ai_and_human_list:
                    ai_and_human_list.remove((x, y))

                # 找到最后一步棋子并删除
                for item in win.items[:]:  # 遍历所有绘制的图形
                    if isinstance(item, Circle):  # 如果是棋子
                        if (
                                item.getCenter().getX() == GRID_WIDTH * x
                                and item.getCenter().getY() == GRID_WIDTH * y
                        ):
                            item.undraw()  # 移除棋子
                            break

                win.redraw()  # 强制窗口重绘
                # 调整玩家顺序
                nonlocal change
                change -= 1  # 回退一次玩家轮换

    win.createButton(text="回棋", command=undo, x=10, y=10)

    # 创建提示按钮
    def create_hint_button():
        button_hint = win.createButton(
            text="提示",
            command=lambda: show_hint(),
            x=200,
            y=10
        )

    def clear_previous_hint():
        # 遍历并移除之前显示的提示
        for item in hint_items:
            item.undraw()  # 移除提示元素
        hint_items.clear()  # 清空提示元素列表
        win.update()  # 强制更新图形界面

    def show_hint():
        clear_previous_hint()  # 清除之前的提示

        # 获取AI的最佳落子位置
        best_move = ai()  # ai() 返回的是最佳落子位置 (x, y)

        # 在图形界面上标记此位置
        hint_circle = Circle(Point(GRID_WIDTH * best_move[0], GRID_WIDTH * best_move[1]), 16)
        hint_circle.setWidth(3)
        hint_circle.setOutline("red")  # 设置红色边框
        hint_circle.draw(win)
        hint_items.append(hint_circle)  # 添加提示圆圈到列表中

        # 显示文本提示
        hint_text = Text(Point(GRID_WIDTH * best_move[0], GRID_WIDTH * best_move[1] - 20), "Best Move")
        hint_text.setSize(10)
        hint_text.setTextColor("red")
        hint_text.draw(win)
        hint_items.append(hint_text)  # 添加提示文本到列表中

        win.after(3000, lambda: clear_previous_hint())  # 延时3秒后清除提示

    create_hint_button()

    def set_game_mode(mode):
        nonlocal game_mode
        game_mode = mode

    # 创建“人机对战”和“人人对战”按钮
    def create_game_mode_buttons():
        # 创建"人机对战"按钮
        button_ai = win.createButton(
            text="人机对战",
            command=lambda: set_game_mode("AI"),
            x=60,
            y=10
        )
        # 创建"人人对战"按钮
        button_two_players = win.createButton(
            text="人人对战",
            command=lambda: set_game_mode("Two Players"),
            x=130,
            y=10
        )

    create_game_mode_buttons()

    game_mode = "AI"  # 默认模式为人机对战

    while g == 0:
        if game_mode == "AI":
            if change % 2 == 0:  # Human turn
                scheduler.enter(0, 1, human_turn)
                scheduler.run()
            else:  # AI turn
                if ai_turn():
                    g = 1
        elif game_mode == "Two Players":
            if two_player_turn():
                g = 1
        change += 1

    message = Text(Point(100, 120), "Click anywhere to quit.")
    message.draw(win)
    win.getMouse()
    win.close()

if __name__ == "__main__":
    game_entry()
