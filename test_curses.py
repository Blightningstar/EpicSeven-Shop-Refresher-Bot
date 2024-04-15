import curses


def main(stdscr):
    stdscr.clear()
    # Colors Used
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    # RED_ON_BLACK = curses.color_pair(1)

    stdscr.addstr("RANDOM QUOTES", curses.A_REVERSE)
    stdscr.chgat(-1, curses.A_REVERSE)

    stdscr.addstr(curses.LINES - 1, 0, "Press 'R' to request a new quote, 'Q' to quit")

    stdscr.chgat(curses.LINES - 1, 7, 1, curses.color_pair(1) | curses.A_BOLD)
    stdscr.chgat(curses.LINES - 1, 7, 1, curses.color_pair(1) | curses.A_BOLD)

    quote_window = curses.newwin(curses.LINES - 2, curses.COLS, 1, 0)

    quote_text_window = quote_window.subwin(curses.LINES - 6, curses.COLS - 4, 3, 2)

    quote_text_window.addstr("Press 'R' to get your first quote!")

    quote_window.box()

    stdscr.refresh()
    quote_window.refresh()

    while True:
        c = quote_window.getch()
        if c == ord("r") or c == ord("R"):
            quote_text_window.clear()
            quote_text_window.addstr("Getting quote...", curses.color_pair(1))

            quote_text_window.refresh()
            quote_text_window.clear()
            quote_text_window.addstr("Hello Moto!")
        elif c == ord("q") or c == ord("Q"):
            break

        stdscr.refresh()
        quote_window.refresh()
        quote_text_window.refresh()
        curses.doupdate()

    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)

    curses.endwin()


def run():
    curses.wrapper(main)


if __name__ == "__main__":
    run()
