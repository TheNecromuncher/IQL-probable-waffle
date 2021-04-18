import numpy as np
import pygame as pg
import random

# GLOBAL ZONE
# colors:
GREY = (160, 160, 160)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# size of grid:
NUM_ROWS = 300
NUM_COLS = 300
top_x, top_y = 0, 0
container_size = 1048
# goal and start:
GOAL_STATE = (0, NUM_COLS - 1)
START_STATE = (NUM_ROWS - 1, 0)
# pygame setup:
pg.display.set_caption("IQL Algorithm")
pg.init()
pg.font.init()
sys_fonts = pg.font.get_fonts()
font1 = pg.font.SysFont(name=sys_fonts[0], size=22, bold=True, italic=False)
font2 = pg.font.SysFont(name=sys_fonts[0], size=12, bold=False, italic=False)
font3 = pg.font.SysFont(name=sys_fonts[0], size=12, bold=False, italic=True)
font4 = pg.font.SysFont(name=sys_fonts[0], size=30, bold=False, italic=False)
random.seed()
pg_user_keys = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
WIN = pg.display.set_mode(size=(int(1600), int(1050)))
WIN.fill(WHITE)
CELL_SIZE = 3
size = 100
# current/previous states for methods to interact with (only stores co_ords):
CURRENT_STATE = [START_STATE[0], START_STATE[1]]
PREVIOUS_STATE = CURRENT_STATE
# viable actions list:
ACTIONS = ["right", "up", "left", "down"]


def random_action():
    return ACTIONS[random.randint(0, 3)]


# action = None indicates unvisited
class State:
    def __init__(self, Q, Action=None, Obstacle=False, Lock=False):
        self.Q = Q
        self.Action = Action
        self.Lock = Lock
        self.Obstacle = Obstacle


# discount factor! will be changeable by user later
DISCOUNT_FACTOR = 0.95

# sets up q-table
q_table = [[None] * NUM_COLS for _ in range(NUM_ROWS)]
for row in range(len(q_table)):
    for entry in range(len(q_table)):
        q_table[row][entry] = State(0)

# changes goal state to be high reward and locked
q_table[GOAL_STATE[0]][GOAL_STATE[1]] = State(100, Lock=True)

# adds in obstacles
obstacle_states = [(5, 5), (2, 3), (2, 1), (2, 2), (5, 4)]
for obstacle in obstacle_states:
    q_table[obstacle[0]][obstacle[1]].Obstacle = True


# Ready to roll! time to call main...


def manhattan_distance(A, B):
    return abs(A[0] - B[0]) + abs(A[1] - B[1])


# both takes the action and verifies it is both within grid bounds and does not enter into an obstacle
def test_action(co_ords, action):
    y = co_ords[0]
    x = co_ords[1]
    if action == "down":
        y += 1
    elif action == "left":
        x -= 1
    elif action == "up":
        y -= 1
    elif action == "right":
        x += 1
    else:
        raise Exception("that is not an action what's going on")
    # verifies action is allowed, i.e. not off of grid or into an obstacle
    if x < 0 or x > NUM_COLS:
        return None
    elif y < 0 or y > NUM_ROWS:
        return None
    elif q_table[y][x].Obstacle is True:
        return None
    else:
        # returns y, x coordinates
        return y, x


# chooses action that results in minimal manhattan distance from goal, preferring actions that involve no turns
# as described in paper. returns ["action", (y, x), distance]
def perform_action():
    options = []
    for action in ACTIONS:
        co_ords = test_action(CURRENT_STATE, action)
        if co_ords is not None:
            options.append([action, co_ords])
    for option in options:
        y = option[1][0]
        x = option[1][1]
        options[options.index(option)].append(manhattan_distance((y, x), GOAL_STATE))
        if q_table[CURRENT_STATE[0]][CURRENT_STATE[1]].Lock:
            return None
        if q_table[y][x].Lock:
            return None
    # sorts by 3rd thing in the array, which is the manhattan distance
    options.sort(key=lambda z: z[2])
    # if theres nowhere to go, raise exception
    if len(options) == 0:
        raise Exception("Nowhere to go!!")
    # if theres only one option, or if the first ones the best, pick it
    elif len(options) == 1 or options[0][2] != options[1][2]:
        current_state = options[0][1]
        return options[0]
    # otherwise, pick one that doesn't turn
    elif options[0][1][0] == PREVIOUS_STATE[0] or options[0][1][1] == PREVIOUS_STATE[1]:
        return options[0]
    else:
        return options[1]


def write_words(string, location, font, alias_bool=True, color=(0, 0, 0)):
    text = font.render(string, alias_bool, color)
    text_rect = text.get_rect()
    text_rect.center = ((top_x + container_size + location[0]),
                        (top_y + container_size + location[1]))
    WIN.blit(text, text_rect)


def print_UI(size, grid):
    size -= 1
    # draw grid outline
    pg.draw.line(
        WIN, BLACK, (top_x, top_y),
        (container_size + top_x, top_y), 1)
    pg.draw.line(
        WIN, BLACK, (top_x, top_y + container_size),
        (top_x + container_size, top_y + container_size), 1)
    pg.draw.line(
        WIN, BLACK, (top_x, top_y),
        (top_x, top_y + container_size), 1)
    pg.draw.line(
        WIN, BLACK, (top_x + container_size, top_y),
        (top_x + container_size, top_y + container_size), 1)
    # figure out cell size; "size" is arg
    CELL_SIZE = container_size / size

    if grid:
        # vertical divisions of grid
        for x in range(size):
            pg.draw.line(
                WIN, BLACK, (top_x + (CELL_SIZE * x), top_y),
                (top_x + (CELL_SIZE * x), (container_size + top_y)), 1)
            # horizontal divisions of grid
            pg.draw.line(
                WIN, BLACK, (top_x, top_y + (CELL_SIZE * x)),
                (top_x + container_size, top_y + (CELL_SIZE * x)), 1)


def place_cell(x, y, color=BLACK):
    x = top_x + CELL_SIZE * x
    y = top_y + CELL_SIZE * y
    cell_x = cell_y = (container_size/size)
    pg.draw.rect(WIN, color, x, y, x2, y2)


def main():
    size = 100
    pg.display.update()
    program = True
    grid = True
    obstacle_density = 1
    print_UI(size, grid)
    frame_rate = 60
    frame_rate_store = []

    while program:
        clock = pg.time.Clock()

        # BEGIN MAIN GAME LOOP, PROMPT FOR INPUT
        run = True
        while run:
            clock.tick(frame_rate)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    program = False
                    run = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_a:
                        size = 100
                    if event.key == pg.K_b:
                        size = 200
                    if event.key == pg.K_c:
                        size = 300
                    if event.key == pg.K_q:
                        obstacle_density = 1
                    if event.key == pg.K_w:
                        obstacle_density = 2
                    if event.key == pg.K_e:
                        obstacle_density = 3
                    if event.key == pg.K_g:
                        if not grid:
                            grid = True
                        else:
                            grid = False
                    if event.key == pg.K_f:
                        pass
                    if event.key == pg.K_SPACE:
                        WIN.fill((255, 255, 255))
                        print_UI(size, grid)
                        run = False
        if not program:
            break


if __name__ == "__main__":
    main()
