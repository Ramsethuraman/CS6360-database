from query.parser import DatabaseREPL
from query import davisbase_constants
import readline, pathlib

hist_file = str(pathlib.Path.home()) + '/.davisdb_history'
open(hist_file, 'a+').close()

readline.read_history_file(hist_file)

if __name__ == '__main__':
    prompt = DatabaseREPL()
    prompt.cmdloop_with_keyboard_interrupt()
    readline.write_history_file(hist_file)
