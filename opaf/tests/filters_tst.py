import unittest
from opaflib import filters
class FiltersTest(unittest.TestCase):
    random_strings = [ "AAAAAAAAA", "$#@%!#TYU$&#%^!@%THJDTKE%I$U^", "X"*65537 ]

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def _basicTest(self, flt, decode_tbl=[], encode_tbl=[], random_strings=[], decode_exception=[], encode_exception=[]):
        #test specific decoding pairs
        for coded, clear in decode_tbl:
            self.assertEqual(clear, flt.decode(coded))

        #test specific encoding pairs
        for clear, coded in encode_tbl:
            self.assertEqual(flt.decode(clear), coded)

        #test x = dec(enc(x))
        for clear in random_strings:
            self.assertEqual(clear, flt.decode(flt.encode(clear)))

        #Test strings that should not decode
        for coded in decode_exception:
            self.assertRaises(Exception, flt.decode, coded)

        #Test strings that should not encode
        for clear in encode_exception:
            self.assertRaises(Exception, flt.encode, clear)


    def testASCIIHexDecode(self):
        decode_tbl = [
          ('61 62 2e6364   65',  'ab.cde'),
          ('61 62 2e6364   657', 'ab.cdep'),
          ('7', 'p')
          ]
        decode_exception = ['61 62 2e6364 R  657', '$1' , '<><><><><><><' ]
        flt = filters.ASCIIHexDecode()
        self._basicTest(flt,decode_tbl,decode_exception=decode_exception,random_strings=self.random_strings)

    def testASCII85Decode(self):
        decode_tbl = [
          ('9jqo^BlbD-BleB1DJ+*+F(f,q', 'Man is distinguished'), 
          ('E,9)oF*2M7/c~>',            'pleasure.')
          ]

        flt = filters.ASCII85Decode()
        self._basicTest(flt,decode_tbl,random_strings=self.random_strings)

    def testFlatedecode(self):
        decode_tbl = [
          ('Man is distinguished'.encode('zlib'), 'Man is distinguished')
          ]

        flt = filters.FlateDecode()
        self._basicTest(flt,decode_tbl,random_strings=self.random_strings)

    def testRunLengthDecode(self):
        decode_tbl = [
          ('\x05123456\xfa7\x04abcde\x80junk', '1234567777777abcde')
          ]

        flt = filters.RunLengthDecode()
        self._basicTest(flt,decode_tbl,random_strings=self.random_strings)


        


