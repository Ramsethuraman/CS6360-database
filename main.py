from query.parser import DatabaseREPL
from query import davisbase_constants as dc
import readline, pathlib, sys

hist_file = str(pathlib.Path.home()) + '/.davisdb_history'
open(hist_file, 'a+').close()

readline.read_history_file(hist_file)

if __name__ == '__main__':
    if not sys.stdin.isatty():
        dc.PROMPT_NAME = ''
        dc.PROMPT_MORE = ''

    prompt = DatabaseREPL()
    prompt.cmdloop_with_keyboard_interrupt()
    readline.write_history_file(hist_file)
