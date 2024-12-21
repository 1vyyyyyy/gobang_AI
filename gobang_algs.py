from config import *

#  离最后落子的邻居位置最有可能是最优点
def order(blank_list, ai_and_human_list):
    last_pt = ai_and_human_list[-1]
    for item in blank_list:
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if (last_pt[0] + i, last_pt[1] + j) in blank_list:
                    blank_list.remove((last_pt[0] + i, last_pt[1] + j))
                    blank_list.insert(0, (last_pt[0] + i, last_pt[1] + j))


def has_neighbor(pt, ai_and_human_list):
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if (pt[0] + i, pt[1]+j) in ai_and_human_list:
                return True
    return False


# 评估函数
def evaluation(is_ai, ai_list, human_list):
    total_score = 0

    if is_ai:
        my_list = ai_list
        enemy_list = human_list
    else:
        my_list = human_list
        enemy_list = ai_list

    # 算自己的得分
    score_all_arr = []  # 得分形状的位置 用于计算如果有相交 得分翻倍
    my_score = 0
    for pt in my_list:
        m = pt[0]
        n = pt[1]
        my_score += cal_score(m, n, 0, 1, enemy_list, my_list, score_all_arr)
        my_score += cal_score(m, n, 1, 0, enemy_list, my_list, score_all_arr)
        my_score += cal_score(m, n, 1, 1, enemy_list, my_list, score_all_arr)
        my_score += cal_score(m, n, -1, 1, enemy_list, my_list, score_all_arr)

    #  算敌人的得分， 并减去
    score_all_arr_enemy = []
    enemy_score = 0
    for pt in enemy_list:
        m = pt[0]
        n = pt[1]
        enemy_score += cal_score(m, n, 0, 1, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, 1, 0, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, 1, 1, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, -1, 1, my_list, enemy_list, score_all_arr_enemy)

    total_score = my_score - enemy_score*ratio*0.1

    return total_score

# 每个方向上的分值计算
def cal_score(m, n, x_decrict, y_derice, enemy_list, my_list, score_all_arr):
    add_score = 0  # 加分项
    # 在一个方向上， 只取最大的得分项
    max_score_shape = (0, None)

    # 如果此方向上，该点已经有得分形状，不重复计算
    for item in score_all_arr:
        for pt in item[1]:
            if m == pt[0] and n == pt[1] and x_decrict == item[2][0] and y_derice == item[2][1]:
                return 0

    # 在落子点 左右方向上循环查找得分形状
    for offset in range(-5, 1):
        # offset = -2
        pos = []
        for i in range(0, 6):
            if (m + (i + offset) * x_decrict, n + (i + offset) * y_derice) in enemy_list:
                pos.append(2)
            elif (m + (i + offset) * x_decrict, n + (i + offset) * y_derice) in my_list:
                pos.append(1)
            else:
                pos.append(0)
        tmp_shap5 = (pos[0], pos[1], pos[2], pos[3], pos[4])
        tmp_shap6 = (pos[0], pos[1], pos[2], pos[3], pos[4], pos[5])

        for (score, shape) in shape_score:
            if tmp_shap5 == shape or tmp_shap6 == shape:
                if tmp_shap5 == (1,1,1,1,1):
                    print('wwwwwwwwwwwwwwwwwwwwwwwwwww')
                if score > max_score_shape[0]:
                    max_score_shape = (score, ((m + (0+offset) * x_decrict, n + (0+offset) * y_derice),
                                               (m + (1+offset) * x_decrict, n + (1+offset) * y_derice),
                                               (m + (2+offset) * x_decrict, n + (2+offset) * y_derice),
                                               (m + (3+offset) * x_decrict, n + (3+offset) * y_derice),
                                               (m + (4+offset) * x_decrict, n + (4+offset) * y_derice)), (x_decrict, y_derice))

    # 计算两个形状相交， 如两个3活 相交， 得分增加 一个子的除外
    if max_score_shape[1] is not None:
        for item in score_all_arr:
            for pt1 in item[1]:
                for pt2 in max_score_shape[1]:
                    if pt1 == pt2 and max_score_shape[0] > 10 and item[0] > 10:
                        add_score += item[0] + max_score_shape[0]

        score_all_arr.append(max_score_shape)

    return add_score + max_score_shape[0]

def game_win(list):
    """
    判断某一方是否获胜，只检查最后下的棋子周围区域
    :param list: 当前玩家的棋子列表（ai 或 human）
    :return: 如果存在五子连珠则返回 True，否则返回 False
    """
    # 检查每个棋子的坐标
    for (m, n) in list:
        # 检查水平、垂直、对角线四个方向
        # 1. 水平检查
        if check_direction(m, n, 1, 0, list):  # 水平：沿 x 轴
            return True
        # 2. 垂直检查
        if check_direction(m, n, 0, 1, list):  # 垂直：沿 y 轴
            return True
        # 3. 主对角线检查（左上到右下）
        if check_direction(m, n, 1, 1, list):  # 主对角线：沿 x 和 y 轴都增加
            return True
        # 4. 副对角线检查（右上到左下）
        if check_direction(m, n, 1, -1, list):  # 副对角线：x 增加，y 减少
            return True
    return False

def check_direction(x, y, dx, dy, list):
    """
    检查给定方向上是否有五子连珠
    :param x: 当前棋子的位置x坐标
    :param y: 当前棋子的位置y坐标
    :param dx: x方向的增量（1表示右，-1表示左）
    :param dy: y方向的增量（1表示下，-1表示上）
    :param list: 当前玩家的棋子位置列表
    :return: 如果该方向上有五子连珠则返回 True，否则返回 False
    """
    count = 1  # 当前棋子算作一个
    # 向前检查（沿着方向(dx, dy)）
    for i in range(1, 5):
        nx, ny = x + i * dx, y + i * dy
        if (nx, ny) in list:
            count += 1
        else:
            break
    # 向后检查（沿着相反方向(-dx, -dy)）
    for i in range(1, 5):
        nx, ny = x - i * dx, y - i * dy
        if (nx, ny) in list:
            count += 1
        else:
            break
    # 如果连成五个，则返回True
    return count >= 5
