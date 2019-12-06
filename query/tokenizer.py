from enum import Enum
from file import DBError, NULLVAL

import string

class TokenType(Enum):
    EOF, COMMA, LP, RP, TEXT, INT, FLOAT, IDENT, OPER, STAR = range(10)

tt = TokenType

_identpart = string.ascii_letters + string.digits + '_' + '$'
class Tokenizer(object):
    def __init__(self, text):
        self.__text = text
        self.__pos = 0
        self.__val = None
        self.error = 'Syntax error'

    @property
    def lval(self):
        return self.__val

    def expect(self, *ttypes):
        real = self.next_token()
        if real not in ttypes:
            names = ', '.join(x.name for x in ttypes)
            raise DBError(f'Expected: {names}; but got {real.name} instead.')
        return real

    def expect_cur_ident(self, *idents):
        names = ', '.join(f'`{x}`' for x in idents)
        idents2 = [s.lower() for s in idents]
        if self.__val.lower() not in idents2:
            raise DBError(f'Expected: ident(s) {names}; but got `{self.__val}`.')
        return idents2.index(self.__val.lower())

    def expect_ident(self, *idents):
        names = ', '.join(f'`{x}`' for x in idents)
        real = self.next_token()
        if tt.IDENT != real:
            raise DBError(f'Expected: ident(s) {names}; but got {real.name}.')

        idents2 = [s.lower() for s in idents]
        if self.__val.lower() not in idents2:
            raise DBError(f'Expected: ident(s) {names}; but got `{self.__val}`.')
        return idents2.index(self.__val.lower())

    def expect_value(self):
        if self.expect(tt.IDENT, tt.FLOAT, tt.INT, tt.TEXT) == tt.IDENT:
            if self.__val.lower() != 'null':
                raise DBError(f'Expected: int, float, text value, or null; but got `{self.__val}`.')
            self.__val = NULLVAL

    def next_token(self):
        while self.__pos < len(self.__text):
            c = self.__text[self.__pos]
            if c in string.whitespace:
                self.__pos += 1
                continue
            elif c in string.ascii_letters + '_' + '$':
                self.__val = self._parse_greedy(_identpart)
                return tt.IDENT
            elif c == '*':
                self.__pos += 1
                return tt.STAR
            elif c == ',':
                self.__pos += 1
                return tt.COMMA
            elif c == '(':
                self.__pos += 1
                return tt.LP
            elif c == ')':
                self.__pos += 1
                return tt.RP
            elif c in '"\'':
                self.__val = self._parse_string()
                return tt.TEXT
            elif c in string.digits or c == '-':
                if c == '-':
                    num = '-'
                    self.__pos += 1
                else:
                    num = ''
                num += self._parse_greedy(string.digits)
                if num == '-':
                    raise DBError(f'Expected digit after `-`')
                
                x = self.__pos
                if x < len(self.__text) and self.__text[x] == '.':
                    self.__pos += 1
                    if x + 1 >= len(self.__text):
                        raise DBError(f'Expected digit but got EOF')
                    c = self.__text[x + 1]
                    if c not in string.digits:
                        raise DBError(f'Expected digit but got `{c}`')
                    num += '.' + self._parse_greedy(string.digits)
                    self.__val = float(num)
                    return tt.FLOAT
                else:
                    self.__val = int(num)
                    return tt.INT
            elif c in '<>!':
                self.__pos += 1
                c1 = None
                if self.__pos < len(self.__text):
                    c1 = self.__text[self.__pos]
                if c1 == '=':
                    self.__pos += 1
                    self.__val = c + c1
                elif c == '<' and c1 == '>':
                    self.__pos += 1
                    self.__val = '!='
                else:
                    self.__val = c
                return tt.OPER
            elif c == '=':
                self.__pos += 1
                self.__val = c
                return tt.OPER
            else:
                raise DBError(f'Unexpected character `{c}`')

        return tt.EOF

    def rest(self):
        return self.__text[self.__pos:]

    def assert_end(self):
        if self.next_token() != tt.EOF:
            raise DBError(f'Expected EOF, but did not get that')

    def _parse_string(self):
        quote = self.__text[self.__pos]
        strval = ''
        prev_quote = False
        self.__pos += 1
        while True:
            if self.__pos >= len(self.__text):
                if prev_quote:
                    break
                raise DBError(f'Expected `{quote}` but got EOF')
            c = self.__text[self.__pos] 
            if c == quote:
                if prev_quote:
                    strval += quote
                prev_quote = not prev_quote
            elif prev_quote:
                break
            else:
                strval += c
            self.__pos += 1
        return strval

    def _parse_greedy(self, syms):
        ret = ''
        while self.__pos < len(self.__text):
            c = self.__text[self.__pos]
            if c not in syms:
                break
            ret += c
            self.__pos += 1

        return ret




