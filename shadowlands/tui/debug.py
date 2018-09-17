import curses

# un-insane-ify the screen so we can debug
debugging=False

def debug():
    global debugging

    if not debugging:
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        debugging = True

'''
def debug(stdscr):
    global debugging

    if not debugging:
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()
        debugging = True
'''

