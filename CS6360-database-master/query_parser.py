import cmd
from termcolor import colored
from query_handler import QueryHandler
import davisbase_constants

def print_error(msg):
    print(colored(msg, 'red'))

def shutdown():
    return True

class DatabaseREPL(cmd.Cmd):    
    #DDL commands
    def do_show(self, args):
        command = args.lower().strip().strip(';')
        if command != davisbase_constants.TABLES_KEYWORD.lower():
            print_error('Syntax error: SHOW TABLES')
            return
        QueryHandler.show_tables_query_handler()

    def do_create(self, args):
        command = args.lower().strip().strip(';')
        if (command.startswith(davisbase_constants.INDEX_KEYWORD.lower())):
            #TODO - Unclear on syntax for CREATE INDEX
            pass
        else:
            split_command = command.split(davisbase_constants.TABLE_KEYWORD.lower() + ' ')
            print(split_command)

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

            QueryHandler.create_table_query_handler(table_name, column_list)

    def do_drop(self, args):
        command = args.lower().strip().strip(';')
        if not command.startswith(davisbase_constants.TABLE_KEYWORD.lower() + ' '):
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
        QueryHandler.drop_tables_query_handler(table_name)

    def do_exit(self, args):
        shutdown()

    def do_EOF(self, args):
        shutdown()
    
    #DML commands
    def do_insert(self, args):
        command = args.lower().strip().strip(';')
        split_command = command.split(davisbase_constants.INTO_KEYWORD.lower() + ' ')
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

        QueryHandler.insert_query_handler(table_name, column_list, value_list)

    def do_delete(self, args):
        SYNTAX_ERROR_MSG = 'Syntax error: DELETE FROM table_name WHERE <CONDITION>'
        command = args.lower().strip().strip(';')
        split_command = command.split(davisbase_constants.FROM_KEYWORD.lower() + ' ')
        if len(split_command) < 2:
            print_error(SYNTAX_ERROR_MSG)
            return
        
        where_keyword_index = split_command[1].find(' ' + davisbase_constants.WHERE_KEYWORD.lower() + ' ')
        if where_keyword_index == -1:
            print_error(SYNTAX_ERROR_MSG)
            return

        table_name = split_command[1][:where_keyword_index].strip()

        where_clause = split_command[1][where_keyword_index + 1 + len(davisbase_constants.WHERE_KEYWORD):].strip()

        QueryHandler.delete_query_handler(table_name, where_clause)

    def do_update(self, args):
        SYNTAX_ERROR_MSG = 'Syntax error: UPDATE <TABLE_NAME> SET <COLUMN_NAME> = <VALUE> WHERE <CONDITION>'
        command = args.lower().strip().strip(';')

        split_command = command.split(' ' + davisbase_constants.SET_KEYWORD.lower() + ' ')
        if len(split_command) < 2:
            print_error(SYNTAX_ERROR_MSG)
            return

        table_name = split_command[0].strip()

        where_keyword_index = split_command[1].find(' ' + davisbase_constants.WHERE_KEYWORD.lower() + ' ')
        if where_keyword_index == -1:
            print_error(SYNTAX_ERROR_MSG)
            return

        column_str = split_command[1][:where_keyword_index].strip()

        equal_char_index = column_str.find('=')
        column_name = column_str[:equal_char_index].strip()

        column_value = column_str[equal_char_index + 1:].strip()
        
        where_clause = split_command[1][where_keyword_index + 1 + len(davisbase_constants.WHERE_KEYWORD):].strip()

        QueryHandler.update_query_handler(table_name, column_name, column_value, where_clause)

    #DQL commands
    def do_select(self, args):
        command = args.lower().strip(';')
        split_command = command.split(davisbase_constants.FROM_KEYWORD.lower())
        if len(split_command) == 1:
            print_error('Expected ' + davisbase_constants.FROM_KEYWORD + ' keyword')
            return
        column_list = split_command[0].strip()
        if len(column_list) == 0:
            print_error('No column names specified')
            return
        column_list = column_list.split(',')
        column_list = [x.strip() for x in column_list]

        rest_of_command = split_command[1].strip()
        rest_of_command = rest_of_command.split(davisbase_constants.WHERE_KEYWORD.lower())
        where_clause = ''
        if len(rest_of_command) > 1:
            #No where clause specified
            where_clause = rest_of_command[1].strip()
        table_name = rest_of_command[0].strip()
        if len(table_name) == 0:
            print_error('No table name specified')
            return
        QueryHandler.select_query_handler(column_list, table_name, where_clause)

    def cmdloop_with_keyboard_interrupt(self):
        try:
            self.cmdloop('Starting database...')
        except KeyboardInterrupt:
            shutdown()


if __name__ == '__main__':
    prompt = DatabaseREPL()
    prompt.prompt = davisbase_constants.PROMPT_NAME + '> '
    prompt.cmdloop_with_keyboard_interrupt()