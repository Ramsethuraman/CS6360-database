import cmd
from termcolor import colored
from file import DBError
from .handler import *
from . import davisbase_constants as dc

def print_error(msg):
    print(colored(msg, 'red'))

def wrap_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except DBError as exc:
        msg = ' '.join(map(str, exc.args))
        print_error(msg)
    except:
        import traceback
        print_error(traceback.format_exc())

def shutdown():
    return True


class DatabaseREPL(cmd.Cmd):    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = dc.PROMPT_NAME
        self.__fullline = ''
        self.__prev_nonempty = False

    def default(self, line):
        print_error('Unknown syntax: ' + str(line))

    def emptyline(self):
        # Does nothing, maintain state
        pass

    def parseline(self, line):
        # Make the command part lowercase
        cmd, arg, line = super().parseline(line)
        if cmd == None:
            return cmd, arg, line
        else:
            return cmd.lower(), arg, line

    def precmd(self, line):
        # Some conditions to pass through
        if self.cmdqueue:
            # Queue meaning that we are executing multiple statements
            self.__prev_nonempty = True
            return line
        if self.__prev_nonempty:
            # When queue is length 0 but we are still reading from queue
            self.__prev_nonempty = False
            return line
        if line == 'EOF' or line == 'eof':
            return line
        if not self.__fullline and not line:
            return ''

        full = (self.__fullline + ' ' + line).strip()

        # Find first semicolon not in quotation
        lines = []
        start_ind = 0
        quoted = None
        for i, c in enumerate(full):
            if quoted == c:
                quoted = None
                continue
            elif quoted != None:
                continue

            if c in '"\'':
                quoted = c
            elif c == ';':
                lines.append(full[start_ind:i])
                start_ind = i + 1

        if start_ind < len(full):
            self.__fullline = full[start_ind:]
            self.prompt = dc.PROMPT_MORE
        else:
            self.__fullline = ''
            self.prompt = dc.PROMPT_NAME
        
        if len(lines) > 1:
            self.cmdqueue += lines[1:]
        elif len(lines) == 0:
            return ''

        return lines[0]


    def do_eof(self, args):
        return True

    #DDL commands
    def do_show(self, args):
        # TODO: can you NOT lowercase pls
        command = args.lower().strip().strip(';')
        if command != dc.TABLES_KEYWORD.lower():
            print_error('Syntax error: SHOW TABLES')
            return
        wrap_error(show_tables_query_handler)

    def do_create(self, args):
        command = args.lower().strip().strip(';')
        if (command.startswith(dc.INDEX_KEYWORD.lower())):
            #TODO - Unclear on syntax for CREATE INDEX
            print_error('TODO: CREATE INDEX')
            pass
        else:
            split_command = command.split(dc.TABLE_KEYWORD.lower() + ' ')
            if len(split_command) < 2:
                print_error('Syntax error: CREATE TABLE <TABLE_NAME> (<COLUMN_NAME> <DATA_TYPE> <NOT_NULL> <UNIQUE>,...)')
                return

            #Check if parentheses are balanced
            first_paren = split_command[1].find('(')
            second_paren = split_command[1].find(')')

            if (first_paren == -1 or second_paren == -1 or first_paren >= second_paren):
                print_error('Parentheses aren\'t balanced')
                return
            
            table_name = split_command[1][:first_paren].strip()
            
            column_list = split_command[1][first_paren + 1:second_paren].strip().split(',')
            column_list = [x.strip() for x in column_list]

            wrap_error(create_table_query_handler, table_name, column_list)

    def do_drop(self, args):
        command = args.lower().strip().strip(';')
        if not command.startswith(dc.TABLE_KEYWORD.lower() + ' '):
            print_error("Syntax error: DROP TABLE <TABLE_NAME>")
            return
        command_split = command.split(' ')
        if len(command_split) > 2:
            print_error("More than one tables entered")
            return
        table_name = command_split[1].strip()
        if table_name == '':
            print_error('No table name specified')
            return
        wrap_error(drop_tables_query_handler, table_name)

    def do_exit(self, args):
        shutdown()

    def do_EOF(self, args):
        shutdown()
    
    #DML commands
    def do_insert(self, args):
        command = args.lower().strip().strip(';')
        split_command = command.split(dc.INTO_KEYWORD.lower() + ' ')
        if len(split_command) < 2:
            print_error('Syntax error: INSERT INTO <TABLE_NAME> (<COLUMN_LIST>) VALUES (<VALUE_LIST>)')
            return
        
        first_pair_open_paren = split_command[1].find('(')
        first_pair_close_paren = split_command[1].find(')')
        second_pair_open_paren = split_command[1].find('(', first_pair_open_paren + 1)
        second_pair_close_paren = split_command[1].find(')', first_pair_close_paren + 1)

        if (first_pair_open_paren >= first_pair_close_paren or second_pair_open_paren >= second_pair_close_paren):
            print_error('Parentheses aren\'t balanced')
            return
        
        table_name = split_command[1][:first_pair_open_paren].strip()

        column_list = split_command[1][first_pair_open_paren + 1:first_pair_close_paren].strip().split(',')
        column_list = [x.strip() for x in column_list]

        value_list = split_command[1][second_pair_open_paren + 1:second_pair_close_paren].strip().split(',')
        value_list = [x.strip() for x in value_list]

        #TODO - Handle validation if column list and value list arent equal
        #TODO - Check for keyword 'VALUES'

        wrap_error(insert_query_handler, table_name, column_list, value_list)

    def do_delete(self, args):
        SYNTAX_ERROR_MSG = 'Syntax error: DELETE FROM table_name WHERE <CONDITION>'
        command = args.lower().strip().strip(';')
        split_command = command.split(dc.FROM_KEYWORD.lower() + ' ')
        if len(split_command) < 2:
            print_error(SYNTAX_ERROR_MSG)
            return
        
        where_keyword_index = split_command[1].find(' ' + dc.WHERE_KEYWORD.lower() + ' ')
        if where_keyword_index == -1:
            print_error(SYNTAX_ERROR_MSG)
            return

        table_name = split_command[1][:where_keyword_index].strip()

        where_clause = split_command[1][where_keyword_index + 1 + len(dc.WHERE_KEYWORD):].strip()
        if not where_clause:
            print_error('Missing where clause')

        wrap_error(delete_query_handler, table_name, where_clause)

    def do_update(self, args):
        SYNTAX_ERROR_MSG = 'Syntax error: UPDATE <TABLE_NAME> SET <COLUMN_NAME> = <VALUE> WHERE <CONDITION>'
        command = args.lower().strip().strip(';')

        split_command = command.split(' ' + dc.SET_KEYWORD.lower() + ' ')
        if len(split_command) < 2:
            print_error(SYNTAX_ERROR_MSG)
            return

        table_name = split_command[0].strip()

        where_keyword_index = split_command[1].find(' ' + dc.WHERE_KEYWORD.lower() + ' ')
        if where_keyword_index == -1:
            print_error(SYNTAX_ERROR_MSG)
            return

        column_str = split_command[1][:where_keyword_index].strip()

        equal_char_index = column_str.find('=')
        column_name = column_str[:equal_char_index].strip()

        column_value = column_str[equal_char_index + 1:].strip()
        
        where_clause = split_command[1][where_keyword_index + 1 + len(dc.WHERE_KEYWORD):].strip()
        if not where_clause:
            print_error('Missing where clause')

        wrap_error(update_query_handler, table_name, column_name, column_value, where_clause)

    #DQL commands
    def do_select(self, args):
        command = args.lower().strip(';')
        split_command = command.split(dc.FROM_KEYWORD.lower())
        if len(split_command) == 1:
            print_error('Expected ' + dc.FROM_KEYWORD + ' keyword')
            return
        column_list = split_command[0].strip()
        if len(column_list) == 0:
            print_error('No column names specified')
            return
        column_list = column_list.split(',')
        column_list = [x.strip() for x in column_list]

        rest_of_command = split_command[1].strip()
        rest_of_command = rest_of_command.split(dc.WHERE_KEYWORD.lower())
        where_clause = ''
        if len(rest_of_command) > 1:
            #Where clause specified
            where_clause = rest_of_command[1].strip()
            if not where_clause:
                print_error('No where clause specified')
        table_name = rest_of_command[0].strip()
        if len(table_name) == 0:
            print_error('No table name specified')
            return
        wrap_error(select_query_handler, column_list, table_name, where_clause)

    def cmdloop_with_keyboard_interrupt(self):
        try:
            self.cmdloop('Starting database...')
            print('\nBye')
        except KeyboardInterrupt:
            shutdown()

