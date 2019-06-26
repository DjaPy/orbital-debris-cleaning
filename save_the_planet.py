import asyncio
import curses
import time
import pathlib
import random


TIC_TIMEOUT = 0.1
BASE_DIR = str(pathlib.Path(__file__).resolve().parent)
FRAME_DIR = BASE_DIR + '/frame/'


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258

COROUTINES = []


def read_controls(canvas):
    """Read keys pressed and returns tuple with controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        canvas.nodelay(True)
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -2

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 2

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 2

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -2

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def get_frame_size(text):
    """Calculate size of multiline text fragment.

     Returns pair (rows number, columns number)
     """

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def draw(canvas):
    """Starts an event loop to render the screen

    :param canvas:
    :return:
    """

    canvas.border()
    max_row, max_column = canvas.getmaxyx()
    count_stars = 85
    count_garbage = 100

    get_coroutine_stars(count_stars, max_row, max_column, canvas)
    fire_corutines = fire(
        canvas, row=max_row/2, column=max_column/2
    )
    COROUTINES.append(fire_corutines)

    relative_pathes_frame = {
        'space_garbage': [
            'duck.txt', 'hubble.txt',
            'lamp.txt', 'trash_l.txt',
            'trash_s.txt', 'trash_xl.txt',
        ],
        'spaceship_frame': [
            'rocket_frame_1', 'rocket_frame_2',
        ],
    }

    file_pathes_to_frames_spaceships = [
        FRAME_DIR + path_file_frame for path_file_frame in relative_pathes_frame['spaceship_frame']
    ]

    frames_animation_spaceship = [
        read_file(path) for path in file_pathes_to_frames_spaceships
    ]

    pathes_to_garbage_frame = [
        FRAME_DIR + path_file_frame for path_file_frame in relative_pathes_frame['space_garbage']
    ]
    count_rows, count_columns = get_frame_size(frames_animation_spaceship[0])
    coroutines_spacecraft = animate_spaceship(
        canvas, frames_animation_spaceship, max_row, max_column, count_rows, count_columns
    )

    COROUTINES.append(coroutines_spacecraft)
    coroutines_of_space_garbage = fill_orbit_with_garbage(
        canvas, pathes_to_garbage_frame, max_column
    )

    COROUTINES.append(coroutines_of_space_garbage)
    while True:
        canvas.refresh()
        try:
            for coroutine in COROUTINES:
                coroutine.send(None)
            time.sleep(TIC_TIMEOUT)

        except StopIteration:
            COROUTINES.remove(coroutine)
        except (SystemExit, KeyboardInterrupt):
            exit(0)


def get_coroutine_stars(count, max_row, max_column, canvas):
    number = 0
    offset_row = 2
    offset_column = 2
    start_row = 2
    start_column = 2
    stars_list = ['*', '+', '.', ':']
    for _ in range(number, count):
        row = random.randint(start_row, max_row - offset_row)
        column = random.randint(start_column, max_column - offset_column)
        symbol = random.choice(stars_list)
        offset_tics = random.randint(1, 5)
        coroutine = blink(canvas, row, column, offset_tics, symbol)
        COROUTINES.append(coroutine)


async def fill_orbit_with_garbage(canvas, paths, max_column):
    start_column = 2
    offset_column = 2
    while True:
        path_to_frame = random.choice(paths)
        column_for_garbage = random.randint(
            start_column, max_column - offset_column
        )
        garbage_frame = read_file(path_to_frame)
        await fly_garbage(canvas, column_for_garbage, garbage_frame)
        await asyncio.sleep(0)


async def blink(canvas, row, column, offset_tics, symbol):
    """Sets the synchronous flashing of stars on the terminal screen.

    :param canvas:
    :param row:
    :param column:
    :param symbol:
    :param offset_tics:
    :return:
    """
    while True:
        async_blink = offset_tics
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(async_blink):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD | curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


async def fire(
        canvas, row, column
        , rows_speed=-0.5, columns_speed=0
):
    """Display animation of gun shot. Direction and speed can be specified."""

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def read_file(frame_name):

    with open(frame_name, 'r') as file:
        frame = file.read()

    return frame


def draw_frame(canvas, rows, columns, text, negative=False):
    """Draw text fragment on canvas.

    Erase text instead of drawing if negative=True is specified.
    """
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(rows)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(columns)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def animate_spaceship(
        canvas, frames_animation, max_row, max_column, count_row, count_column
):
    """Asynchronous animation of the spacecraft"""

    frame_1, frame_2 = frames_animation
    position_row = max_row // 2
    position_column = max_column // 2
    min_legal_row = 1 + count_row
    max_legal_row = max_row - 1
    min_legal_column = 1
    max_legal_column = max_column - (count_column + 1)

    while True:
        row_direction, column_direction, _ = read_controls(canvas)

        if min_legal_row <= position_row < max_legal_row:
            position_row += row_direction

            if position_row < min_legal_row:
                position_row = max(min_legal_column, position_row)
            if position_row > max_legal_row:
                position_row = min(max_legal_row, position_row)

        if min_legal_column <= position_column < max_legal_column:
            position_column += column_direction

            if position_column < min_legal_column:
                position_column = max(min_legal_column, position_column)
            if position_column > max_legal_column:
                position_column = min(max_legal_column, position_row)

        draw_frame(canvas, position_row, position_column, frame_1)
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        draw_frame(canvas, position_row, position_column, frame_1, negative=True)

        draw_frame(canvas, position_row, position_column, frame_2)
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        draw_frame(canvas, position_row, position_column, frame_2, negative=True)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom.

    Сolumn position will stay same, as specified on start.

    """
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
    curses.curs_set(False)
