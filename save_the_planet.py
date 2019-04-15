import asyncio
import curses
import time

import random


TIC_TIMEOUT = 0.1


def settings(canvas, sleep):
    curses.curs_set(False)
    canvas.border()
    canvas.refresh()
    time.sleep(sleep)


def draw(canvas):
    max_row, max_column = canvas.getmaxyx()
    count_stars = 75
    sleep_start = random.randint(1, 10)
    coroutines = get_coroutine_list(count_stars, max_row, max_column, canvas)
    while True:
        try:
            for coroutine in coroutines:
                # time.sleep(sleep_start*TIC_TIMEOUT)
                coroutine.send(None)
                canvas.refresh()
            settings(canvas, sleep=TIC_TIMEOUT)
        except StopIteration:
            coroutines.remove(coroutine)
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
    while True:
        async_blink = random.randint(20, 40)
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


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
