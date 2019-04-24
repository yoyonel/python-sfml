"""
https://en.wikipedia.org/wiki/Tetromino
"""
from copy import deepcopy
from dataclasses import dataclass
from random import randint, seed

from sfml import sf


def main():
    seed(-1)

    board_nb_rows = 20
    board_nb_cols = 10

    board = [[0 for _ in range(board_nb_cols)] for _ in range(board_nb_rows)]

    @dataclass
    class Point:
        x: int = 0
        y: int = 0

    tetrominos = [
        [1, 3, 5, 7],  # I
        [2, 4, 5, 7],  # Z
        [3, 5, 4, 6],  # S
        [3, 5, 4, 7],  # T
        [2, 3, 5, 7],  # L
        [3, 5, 7, 6],  # J
        [2, 3, 4, 5],  # O
    ]

    def get_tetromino(i_shape):
        return [
            Point(i % 2, i // 2)
            for i in tetrominos[i_shape]
        ]

    def new_tetromino():
        t_s = randint(0, len(tetrominos) - 1)
        return t_s, get_tetromino(t_s)

    tetromino_shape, tetromino = new_tetromino()

    # create the main window
    window = sf.RenderWindow(sf.VideoMode(320, 480), "Tetris")
    window.vertical_synchronization = True

    # create the message background
    try:
        tex_tiles = sf.Texture.from_file("data/tiles.png")
        tex_background = sf.Texture.from_file("data/background.png")
    except IOError as error:
        raise RuntimeError("An error occured: {0}".format(error))

    sprite_quads = sf.Sprite(tex_tiles)
    sprite_quads.texture_rectangle = (0, 0, 18, 18)

    sprite_background = sf.Sprite(tex_background)

    dx = 0
    rotate = False
    instant_scroll_down = False
    color_num = 1
    timer = 0
    delay = 0.3

    clock = sf.Clock()

    def check() -> bool:
        for quad in tetromino:
            if quad.x < 0 or quad.x >= board_nb_cols or quad.y >= board_nb_rows:
                return False
            elif board[quad.y][quad.x] != 0:
                return False
        return True

    # start the game loop
    while window.is_open:
        time = clock.elapsed_time.seconds
        clock.restart()
        timer += time

        # process events
        for event in window.events:

            # close window: exit
            if event == sf.Event.CLOSED:
                window.close()

            if event == sf.Event.KEY_PRESSED:
                # escapte key: exit
                if event['code'] == sf.Keyboard.ESCAPE:
                    window.close()

                elif event['code'] == sf.Keyboard.LEFT:
                    dx = -1
                elif event['code'] == sf.Keyboard.RIGHT:
                    dx = 1

                if event['code'] == sf.Keyboard.UP:
                    rotate = True

                if event['code'] == sf.Keyboard.DOWN:
                    delay = 0.05

                if event['code'] == sf.Keyboard.SPACE:
                    instant_scroll_down = True

        # before moving/rotating, save the current state/position
        tetromino_last_state = deepcopy(tetromino)

        # Instant scroll down
        if instant_scroll_down:
            while check():
                # scroll down current tetromino
                for q in tetromino:
                    q.y += 1

            for q in tetromino:
                q.y -= 1

            # update field
            for q in tetromino:
                board[q.y][q.x] = int(color_num)

            # Choose a new tetromino
            tetromino_shape, tetromino = new_tetromino()

            # Choose a new color
            color_num = randint(1, 7)
        else:
            # Rotate
            if rotate and tetromino_shape != 6:
                q_cor = tetromino[1]  # center of rotation
                for q in tetromino:
                    q.x, q.y = q_cor.x - (q.y - q_cor.y), q_cor.y + (q.x - q_cor.x)
                if not check():
                    tetromino = deepcopy(tetromino_last_state)

            # Move Left Right
            for q in tetromino:
                q.x += dx
            if not check():
                tetromino = deepcopy(tetromino_last_state)

            # Tick
            if timer > delay:
                tetromino_last_state = deepcopy(tetromino)

                # scroll down current tetromino
                for q in tetromino:
                    q.y += 1

                if not check():
                    # update field
                    for q in tetromino_last_state:
                        board[q.y][q.x] = int(color_num)

                    # Choose a new tetromino
                    tetromino_shape, tetromino = new_tetromino()

                    # Choose a new color
                    color_num = randint(1, 7)

                timer = 0

        # check lines
        k = board_nb_rows - 1
        for i in range(board_nb_rows-1, 0, -1):
            count = 0
            for j in range(board_nb_cols):
                if board[i][j]:
                    count += 1
                board[k][j] = board[i][j]
            if count < board_nb_cols:
                k -= 1

        # reset
        dx = 0
        rotate = False
        delay = 0.3
        instant_scroll_down = False

        # draw
        # clear the window
        window.clear(sf.Color(0, 0, 0))

        window.draw(sprite_background)

        # renderer field
        for i, row_field in enumerate(board):
            for j, color_in_field in enumerate(row_field):
                if color_in_field != 0:
                    sprite_quads.texture_rectangle = (color_in_field * 18, 0, 18, 18)
                    sprite_quads.position = j * 18, i * 18
                    sprite_quads.move((28, 31))  # offset
                    window.draw(sprite_quads)

        # renderer current tetromino
        for quad in tetromino:
            sprite_quads.texture_rectangle = (color_num * 18, 0, 18, 18)
            sprite_quads.position = quad.x * 18, quad.y * 18
            sprite_quads.move((28, 31))  # offset
            window.draw(sprite_quads)

        # window.draw(sprite_frame)

        # finally, display the rendered frame on screen
        window.display()


if __name__ == "__main__":
    main()
