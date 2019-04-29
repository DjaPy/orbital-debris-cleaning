import asyncio
import curses
import time
import pathlib
import random


TIC_TIMEOUT = 0.1
BASE_DIR = str(pathlib.Path(__file__).resolve().parent)

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


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
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def get_frame_size(text):
    """Calculate size of multiline text fragment. Returns pair (rows number, colums number)"""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def settings(canvas, sleep):
    curses.curs_set(False)
    canvas.border()
    canvas.refresh()
    time.sleep(sleep)


def draw(canvas):
    """Starts an event loop to render the screen

    :param canvas:
    :return:
    """
    max_row, max_column = canvas.getmaxyx()
    count_stars = 75

    coroutines = get_coroutine_list(count_stars, max_row, max_column, canvas)
    fire_corutines = fire(canvas, start_row=max_row/2, start_column=max_column/2)
    text = create_text_frame()
    row_text, column_text = get_frame_size(text[0])
    coroutines_spacecruft = animate_spaceship(
        canvas, text, max_row, max_column, row_text, column_text
    )
    coroutines_with_space_ship = [fire_corutines, coroutines_spacecruft] + coroutines
    while True:
        try:
            for coroutine in coroutines_with_space_ship:
                coroutine.send(None)
                canvas.refresh()
            settings(canvas, sleep=TIC_TIMEOUT)
        except StopIteration:
            coroutines_with_space_ship.remove(coroutine)
        except (SystemExit, KeyboardInterrupt):
            exit(0)


def get_coroutine_list(count, max_row, max_column, canvas):
    number = 0
    offset_row = 2
    offset_column = 2
    start_row = 2
    start_column = 2
    start_list = ['*', '+', '.', ':']
    coroutines = []
    while number != count:
        row = random.randint(start_row, max_row - offset_row)
        column = random.randint(start_column, max_column - offset_column)
        symbol = random.choice(start_list)
        coroutine = blink(canvas, row, column, symbol)
        coroutines.append(coroutine)
        number += 1
    return coroutines


async def blink(canvas, row, column, symbol='*'):
    """Sets the synchronous flashing of stars on the terminal screen.

    :param canvas:
    :param row:
    :param column:
    :param symbol:
    :return:
    """
    while True:
        async_blink = random.randint(1, 5)
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
        canvas, start_row, start_column
        , rows_speed=-0.5, columns_speed=0
):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

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


def get_frame(name_frame):

    with open(name_frame, 'r') as file:
        frame = file.read()

    return frame


def create_text_frame():
    list_path_file_frame = (
        BASE_DIR + '/frame/rocket_frame_1',
        BASE_DIR + '/frame/rocket_frame_2',
    )
    path_frame_1, path_frame_2 = list_path_file_frame

    frame_1 = get_frame(path_frame_1)
    frame_2 = get_frame(path_frame_2)
    return frame_1, frame_2


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw text fragment on canvas.

    Erase text instead of drawing if negative=True is specified.
    """
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
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
        canvas, text, max_row, max_column, row_text, column_text
):
    """Asynchronous animation of the spacecraft"""

    frame_1, frame_2 = text
    start_row = max_row // 2
    start_column = max_column // 2
    min_legal_row = 1 + row_text
    max_legal_row = max_row - 1
    min_legal_column = 2
    max_legal_column = max_column - (column_text + 1)
    legal_row_list = range(min_legal_row, max_legal_row)
    legal_column_list = range(min_legal_column, max_legal_column)

    while True:
        row_direction, column_direction, _ = read_controls(canvas)

        if start_row in legal_row_list:
            start_row += row_direction
            if start_row < min_legal_row:
                start_row += 1
            if start_row > max_legal_row:
                start_row -= 1

        if start_column in legal_column_list:
            start_column += column_direction

            if start_column < min_legal_column:
                start_column += 1
            if start_column > max_legal_column:
                start_column -= 1

        draw_frame(canvas, start_row, start_column, frame_1)
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, frame_1, negative=True)

        draw_frame(canvas, start_row, start_column, frame_2)
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, frame_2, negative=True)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
