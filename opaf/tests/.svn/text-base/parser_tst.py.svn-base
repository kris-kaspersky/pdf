import unittest
from opaflib import parser
from ply.lex import LexError

class ParserTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def testNormalParser(self):
        object_tags_tbl = [
          ('array', '[ 1 (string) <414141> null ]'),
          ('number', '1'),
          ('number', '1.0'),
          ('number', '-1.0'),
          ('string', '(string)'),
          ('string', '(st(ri)ng)'),
          ('string', '(st(ri)n\\023g)'),
          ('string', '<41414141>'),
          ('dictionary', '<< /entry1 1 /entry2 (string) /entry3 <414141> /entry4 null >>'),
          ('dictionary', '<< /entry1 1 /entry2#01 (string) /en#45try3 <414141> /entry4 null >>'),
          ]

        object_raises = [
          '1 0',
          '(asd',
          '1.0.1',
          'asda>',
          '<asd>',
          '((asda)',
          'obj'
          'qfdgfsda',
          '<< /aa >>'
          ]

        indirect_object_tags_tbl = [
          ('indirect_object', '1 0 obj\n(string)\nendobj  \n'),
          ('indirect_object', '1 0 obj\n<41414141>\nendobj\n'),
          ('indirect_object', '1 0 obj\n[1 (string) <414141> null]\nendobj'),
          ]

        indirect_object_raises = [
          '1 0 obj\n<</key 1>>\nendobj\n2 0 obj\n<</key 2\nendobj',
          '1 0 \nobj\n<</key 1>>\nendobj\n',
          
          ]

        #test invalid objects
        for obj_str in object_raises:
            self.assertRaises(Exception, parser.parse, ('object',obj_str ))

        #test tags for an indirect object parser
        for tag, obj_str in indirect_object_tags_tbl:
            self.assertEqual(tag, parser.parse('indirect', obj_str+"\n").tag)

        #test invalid indirect_objects      
        for obj_str in object_raises:
            self.assertRaises(Exception, parser.parse, ('indirect',obj_str))

        #test tags for a simple object parser
        for tag, obj_str in object_tags_tbl:
            self.assertEqual(tag, parser.parse('object', obj_str).tag)


        

if __name__ == '__main__':
    unittest.main()

        


