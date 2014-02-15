import unittest
from opaflib.lexer import PDFLexer
import ply.lex as lex

class ParserTest(unittest.TestCase):
    def setUp(self):
        self.my_lexer = PDFLexer()
        self.my_lexer.build(debug=False,errorlog=lex.NullLogger())

    def tearDown(self):
        self.my_lexer = None
        
    def lex(self, data):
        return str(self.my_lexer.lexify(data))

    def testLexer(self):
        tst = [
        (r"[LexToken(LEFT_SQUARE_BRACKET,'[',1,0)]", "["),
        (r"[LexToken(RIGHT_SQUARE_BRACKET,']',1,0)]", "]"),
        (r"[LexToken(DOUBLE_GREATER_THAN_SIGN,'>>',1,0)]", ">>"),
        (r"[LexToken(DOUBLE_LESS_THAN_SIGN,'<<',1,0)]", "<<"),
        (r"[LexToken(HEXSTRING,'',1,0)]","<>"),
        (r"[LexToken(HEXSTRING,'\x01\x02\x03\x04',1,0)]","<01020304>"),
        (r"[LexToken(STRING,'!',1,2)]","(!)"),
        (r"[LexToken(NUMBER,'123.2',1,0)]", '123.2'),
        (r"[LexToken(NAME,'name0',1,0)]", '/name0')]
        for token, string  in tst:
            self.assertEqual(token, self.lex(string))

if __name__ == '__main__':
    unittest.main()

        


