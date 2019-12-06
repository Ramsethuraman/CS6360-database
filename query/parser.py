import cmd
from termcolor import colored
from file import DBError
from .tokenizer import Tokenizer, TokenType as tt
from .handler import *
from . import davisbase_constants as dc


class DatabaseREPL(cmd.Cmd):    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = dc.PROMPT_NAME
        self.__fullline = ''
        self.__prev_nonempty = False

    def print_error(self, msg):
        print(colored(msg, 'red'))
        self.cmdqueue.clear()

    def default(self, line):
        cmds = [x[3:].upper() for x in dir(self) if x.startswith('do_')]
        self.print_error(f'Expected: [{"|".join(cmds)}] ...')
        self.print_error('Type in help <cmd> for further usage info')

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
        line, _, _ = line.partition('--')
        line = line.strip()

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

    def onecmd(self, line):
        try:
            return super().onecmd(line)
        except DBError as exc:
            msg = ' '.join(map(str, exc.args))
            self.print_error(msg)
        except:
            import traceback
            self.print_error(traceback.format_exc())
            self.cmdqueue.clear()

    #DDL commands
    def do_show(self, args):
        '''
SHOW TABLES

    Show the list of all tables (including metatables)
        '''
        # TODO: can you NOT lowercase pls
        command = args.lower().strip().strip(';')
        if command != dc.TABLES_KEYWORD.lower():
            self.print_error('Syntax error: SHOW TABLES')
            return
        show_tables_query_handler()

    def do_create(self, args):
        '''
CREATE INDEX table_name (column_name)

    Creates an index on table_name and column_name.

CREATE TABLE table_name (col_name <TYPE> [NOT NULL] [UNIQUE] [, ...])

    Creates a new table with a set of columns and its types.
        '''
        tkn = Tokenizer(args.strip())
        
        if tkn.expect_ident(dc.INDEX_KEYWORD, dc.TABLE_KEYWORD) == 0:
            tkn.expect(tt.IDENT)
            tbl_name = tkn.lval

            tkn.expect(tt.LP)
            tkn.expect(tt.IDENT)
            col_name = tkn.lval
            tkn.expect(tt.RP)
            tkn.assert_end()

            create_index_handler(tbl_name, col_name)
        else:
            tkn.expect(tt.IDENT)
            tbl_name = tkn.lval

            cur_col = []
            column_list = []
            tkn.expect(tt.LP)
            while True:
                ttype = tkn.expect(tt.RP, tt.IDENT, tt.COMMA)
                if ttype == tt.IDENT:
                    cur_col.append(tkn.lval)
                elif ttype == tt.RP:
                    if not cur_col:
                        self.print_error('Empty column specifier')
                        return
                    column_list.append(cur_col)
                    break
                elif ttype == tt.COMMA:
                    if not cur_col:
                        self.print_error('Empty column specifier')
                        return
                    column_list.append(cur_col)
                    cur_col = []

            tkn.assert_end()
            create_table_query_handler(tbl_name, column_list)

    def do_drop(self, args):
        '''
DROP table_name

    Removes a table file, its meta-data, and any associated indexes it may have. 
        '''
        command = args.strip().strip(';')
        if not command.startswith(dc.TABLE_KEYWORD.lower() + ' '):
            self.print_error("Syntax error: DROP TABLE <TABLE_NAME>")
            return
        command_split = command.split(' ')
        if len(command_split) > 2:
            self.print_error("More than one tables entered")
            return
        table_name = command_split[1].strip()
        if table_name == '':
            self.print_error('No table name specified')
            return
        drop_tables_query_handler(table_name)

    def do_exit(self, args):
        '''
Exit the program
        '''
        return True

    def do_eof(self, args):
        '''
Exit the program
        '''
        return True
    
    #DML commands
    def do_insert(self, args):
        '''
INSERT INTO table_name (col1[, ...]) VALUES (val1[, ...])

    Insert a row entry into the specified table. Any columns not supplied will
    be NULL'd out.
        '''
        tkn = Tokenizer(args)
        tkn.expect_ident(dc.INTO_KEYWORD)

        tkn.expect(tt.IDENT)
        table_name = tkn.lval

        column_list = []
        tkn.expect(tt.LP)
        while True:
            tkn.expect(tt.IDENT) 
            column_list.append(tkn.lval)
            ttype = tkn.expect(tt.RP, tt.COMMA)
            if ttype == tt.RP:
                break

        tkn.expect_ident(dc.VALUES_KEYWORD)
        values = []
        tkn.expect(tt.LP)
        while True:
            tkn.expect_value()
            values.append(tkn.lval)
            ttype = tkn.expect(tt.RP, tt.COMMA)
            if ttype == tt.RP:
                break

        tkn.assert_end()

        if len(values) != len(column_list):
            self.print_error('Mismatch length of values and columns')
            return

        insert_query_handler(table_name, column_list, values)

    def do_delete(self, args):
        '''
DELETE FROM table_name WHERE <column> <cond> <value>

    Delete all rows with the following column value specified. 

    <cond> can be of the following: <, <=, =, !=, >=, >
        '''


        tkn = Tokenizer(args)
        tkn.expect_ident(dc.FROM_KEYWORD)
        tkn.expect_ident(dc.TABLE_KEYWORD)

        tkn.expect(tt.IDENT)
        table_name = tkn.lval
        if tkn.expect(tt.IDENT, tt.EOF) == tt.IDENT:
            tkn.expect_cur_ident(dc.WHERE_KEYWORD)
            where_clause = tkn.rest()
        else:
            where_clause = ''

        delete_query_handler(table_name, where_clause)

    def do_update(self, args):
        '''
UPDATE table_name SET <mod_column> = <new_value> WHERE <cond_column> <cond> <cond_value>

    Update all rows that match the specified condition, on the mod_column and
    set that to new_value

    <cond> can be of the following: <, <=, =, !=, >=, >
        '''
        tkn = Tokenizer(args)
        tkn.expect(tt.IDENT)
        table_name = tkn.lval
        tkn.expect_ident(dc.SET_KEYWORD)

        tkn.expect(tt.IDENT)
        column_name = tkn.lval

        tkn.expect(tt.OPER)
        if tkn.lval != '=':
            raise DBError(f'Expected: `=` but got `{tkn.lval}`.')

        tkn.expect_value()
        column_value = tkn.lval

        tkn.expect_ident(dc.WHERE_KEYWORD)
        where_clause = tkn.rest()

        update_query_handler(table_name, column_name, column_value, where_clause)

    def do_debug(self, args):
        tkn = Tokenizer(args.strip())
        tkn.expect_value()
        print(tkn.lval)

    #DQL commands
    def do_select(self, args):
        '''
SELECT <column_set>|* FROM table_name [WHERE <column> <cond> <value>]

    Select a set of row entries that meet the condition if specified, or all of
    entries in the table if ignored. If * is specified in place of <column_set>,
    all columns are displayed, else only those columns in <column_set> will be
    shown.

    <cond> can be of the following: <, <=, =, !=, >=, >
        '''
        tkn = Tokenizer(args.strip())
        column_list = []

        if tkn.expect(tt.IDENT, tt.STAR) == tt.STAR:
            tkn.expect_ident(dc.FROM_KEYWORD)
            column_list.append('*')
        else:
            column_list.append(tkn.lval)
            while tkn.expect(tt.COMMA, tt.IDENT) == tt.COMMA:
                column_list.append(tkn.expect(tt.IDENT))
            tkn.expect_cur_ident(dc.FROM_KEYWORD.lower())

        tkn.expect(tt.IDENT)
        tbl_name = tkn.lval

        if tkn.expect(tt.IDENT, tt.EOF) == tt.IDENT:
            tkn.expect_cur_ident(dc.WHERE_KEYWORD.lower())
            where_clause = tkn.rest()
        else:
            where_clause = ''

        select_query_handler(column_list, tbl_name, where_clause)

    def cmdloop_with_keyboard_interrupt(self):
        try:
            self.cmdloop('Starting database...')
            print('\nBye')
        except KeyboardInterrupt:
            pass

