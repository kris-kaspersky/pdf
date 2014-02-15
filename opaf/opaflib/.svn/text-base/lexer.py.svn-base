###################s#################################################
## felipe.andres.manzano@gmail.com  http://feliam.wordpress.com/  ##
## twitter.com/feliam        http://www.linkedin.com/in/fmanzano  ##
####################################################################
# PDF scanner/tokenizer
import sys
import ply.lex as lex
#logging facility
import logging
logger = logging.getLogger('LEXER')

TOKEN = lex.TOKEN
class PDFLexer():
    #Unique Lexer exception to comunicate error conditions to upper dimensions..
    class Exception(Exception):
        def __init__(self,t,txt):
            super(PDFLexer.Exception,self).__init__()
            self.pos=t.lexer.lexpos
            self.data=t.lexer.lexdata[t.lexer.lexpos:10]
            self.txt = txt

        def __str__(self):
            return '%s at %d[%s]'%(self.txt,self.pos,self.data.encode('hex'))                


    # Tokens
    tokens = ('HEXSTRING','STRING', 'NUMBER', 'NAME', 'LEFT_SQUARE_BRACKET', 'RIGHT_SQUARE_BRACKET', 
              'NULL', 'TRUE', 'FALSE', 'R', 'DOUBLE_LESS_THAN_SIGN', 'DOUBLE_GREATER_THAN_SIGN',
              'STREAM_DATA', 'OBJ', 'ENDOBJ', 'HEADER', 'TRAILER', 'EOF', 'STARTXREF' , 
              'XREF' )

    #different lexers used..
    states = ( ('string', 'exclusive'),
               ('name', 'exclusive'),
               ('xref', 'exclusive'),
             )

    #7.2.2 Character Set
    #The PDF character set is divided into three classes, called regular,
    #delimiter, and white-space characters. This classification determines
    #the grouping of characters into tokens. The rules defined in this 
    #sub-clause apply to all characters in the file except within strings, 

    #streams, and comments.
    white_spaces_r = r'\x20\r\n\t\x0c\x00'
    white_spaces = '\x20\r\n\t\x0c\x00'

    #The delimiter characters (, ), <, >, [, ], {, }, /, and %
    delimiters = r'()<>[]/%' #This is odd: {} ?
    delimiters_r = r'()<>\[\]/%' #This is odd: {} ?

    #The CARRIAGE RETURN (0Dh) and LINE FEED (0Ah) characters, also called 
    #newline characters, shall be treated as end-of-line (EOL) markers. The 
    #combination of a CARRIAGE RETURN followed immediately by a LINE FEED 
    #shall be treated as one EOL marker.
    eol = r'(\r|\n|\r\n)'

    #########################################################################
    #INITIAL lexer

    #7.3.2 Boolean Objects
    #Boolean objects represent the logical values of true and false. They appear 
    #in PDF files using the keywords true and false.
    t_TRUE = 'true'
    t_FALSE = 'false'

    #################################################################################
    #string lexer
    #7.3.4.2    Literal Strings

    #A literal string shall be written as an arbitrary number of characters
    #enclosed in parentheses. Any characters may appear in a string except
    #unbalanced parentheses and the backslash, which shall be treated
    #specially as described in this sub-clause. Balanced pairs of
    #parentheses within a string require no special treatment.

    #EXAMPLE 1        The following are valid literal strings:
    #                 ( This is a string )
    #                 ( Strings may contain newlines
    #                 and such . )
    #                 ( Strings may contain balanced parentheses ( ) and
    #                 special characters ( * ! & } ^ % and so on ) . )
    #                 ( The following is an empty string . )
    #                 ()
    #                 ( It has zero ( 0 ) length . )


    #An end-of-line marker appearing within a literal string without a 
    #preceding REVERSE SOLIDUS shall be treated as a byte value of (0Ah),
    #irrespective of whether the end-of-line marker was a CARRIAGE RETURN 
    #(0Dh), a LINE FEED (0Ah), or both.
    @TOKEN(eol)
    def t_string_LITERAL_STRING_EOL(self, t):
        t.lexer.string += '\x0A'

    #Nothing is ignored when lexing a string
    t_string_ignore = ''

        
    @TOKEN(r'\\([nrtbf()\\]|[0-7]{1,3}|'+eol+')')    
    def t_string_ESCAPED_SEQUENCE(self, t):
        val = t.value[1:]
        if val[0] in '0123':
            value = chr(int(val,8)) 
        elif val[0] in '4567':
            value = chr(int(val[:2],8)) + val[3:]
        else:   
            value = { '\n': '', '\r': '', 'n': '\n', 'r': '\r', 't': '\t', 'b': '\b', 'f': '\f', '(': '(', ')': ')', '\\': '\\' }[val[0]]
        t.lexer.string += value

    #PDF string insanity..
    def t_string_LEFT_PARENTHESIS(self, t):
        r'\('
        t.lexer.push_state('string')
        t.lexer.string += '('
        
    def t_string_RIGHT_PARENTHESIS(self, t):
        r'\)'
        t.lexer.pop_state()
        if t.lexer.current_state() == 'string':
            t.lexer.string += ')'
        else:
            t.type  = 'STRING'
            t.value = t.lexer.string
            return t
            
    def t_string_LITERAL_STRING_CHAR(self, t):
        r'.'
        t.lexer.string += t.value

    #TODO: Log, increment a warning counter, or even dismiss the file   
    def t_string_error(self, t):
        logger.error('Error scanning a literal string at %d\n'%t.lexer.lexpos)
        raise PDFLexer.Exception(self, t,'Scanning string')
        t.type  = 'STRING'
        t.value = t.lexer.string
        t.lexer.skip(1)
        return t
        
    def t_STRING(self, t):
        r'\('
        t.lexer.push_state('string')
        t.lexer.string = ''
        
    #7.3.4.3    Hexadecimal Strings
    #Strings may also be written in hexadecimal form, which is useful for 
    #including arbitrary binary data in a PDF file.A hexadecimal string shall
    #be written as a sequence of hexadecimal digits (0-9 and either A-F or a-f)
    #encoded as ASCII characters and enclosed within angle brackets < and >.
    #EXAMPLE 1          < 4E6F762073686D6F7A206B6120706F702E >
    #Each pair of hexadecimal digits defines one byte of the string. White-space 
    #characters shall be ignored. If the final digit of a hexadecimal string is 
    #missing -that is, if there is an odd number of digits- the final digit shall be 
    #assumed to be 0.

    @TOKEN(r'<[a-fA-F0-9'+white_spaces_r+']*>')
    def t_HEXSTRING(self, t):
        t.value =  ''.join([c for c in t.value if c not in self.white_spaces+'<>'])
        t.value =  (t.value+('0'*(len(t.value)%2))).decode('hex')
        return t

       
    #7.3.5      Name Objects
    #Beginning with PDF 1.2 a name object is an atomic symbol uniquely
    #defined by a sequence of any characters (8-bit values) except null
    #(character code 0).
    #
    #When writing a name in a PDF file, a SOLIDUS (2Fh) (/) shall be used to
    #introduce a name. The SOLIDUS is not part of the name but is a prefix
    #indicating that what follows is a sequence of characters representing
    #the name in the PDF file and shall follow these rules:
    #a)  A NUMBER SIGN (23h) (#) in a name shall be written by using its
    #    2-digit hexadecimal code (23), preceded     by the NUMBER SIGN.
    #b)  Any character in a name that is a regular character (other than
    #    NUMBER SIGN) shall be written as itself or by using its 2-digit
    #    hexadecimal code, preceded by the NUMBER SIGN.
    #c)  Any character that is not a regular character shall be written using
    #    its 2-digit hexadecimal code, preceded     by the NUMBER SIGN only.

    def t_NAME(self, t):
        r'/'
        t.lexer.push_state('name')    
        t.lexer.name = ''
        t.lexer.start = t.lexpos

    def t_name_HEXCHAR(self, t):
        r'\#[0-9a-fA-F]{2}'
        #Beginning with PDF 1.2 a name object is an atomic symbol uniquely 
        #defined by a sequence of any characters (8-bit values) except null (character code 0).
        assert t.value != '#00'
        t.lexer.name += t.value[1:].decode('hex')

    @TOKEN(r'[^'+white_spaces_r+delimiters_r+']')
    def t_name_NAMECHAR(self, t):
        t.lexer.name += t.value
        
    @TOKEN(r'['+white_spaces_r+delimiters_r+']')
    def t_name_WHITESPACE(self, t):
    #    global stream_len
        t.lexer.pop_state()
        t.lexer.lexpos -= 1
        t.lexpos = t.lexer.start
        t.type  = 'NAME'
        t.value = t.lexer.name
        t.lexer.name=''
        t.endlexpos = t.lexer.lexmatch.span(0)[1]
        return t

    def t_name_error(self, t):
        logger.error('Name error at pos: %d [%s]'%(t.lexer.lexpos, t.lexer.name))
        raise PDFLexer.Exception(self, t,'Scanning a name')

    #Nothing is ignored when lexing a name
    t_name_ignore = ''

    #7.3.6 Array Objects
    #An array shall be written as a sequence of objects enclosed in [ and ].
    #EXAMPLE         [ 549 3.14 false ( Ralph ) /SomeName ]
    t_LEFT_SQUARE_BRACKET = r'\['
    t_RIGHT_SQUARE_BRACKET = r'\]'

    #7.3.7 Dictionary Objects
    #A dictionary shall be written as a sequence of key-value pairs 
    #enclosed in double angle brackets (<< ... >>)
    t_DOUBLE_LESS_THAN_SIGN = r'<<'
    t_DOUBLE_GREATER_THAN_SIGN = r'>>'

    ############################################################################
    #7.3.8 Stream Objects
    #A stream object, like a string object, is a sequence of bytes. A stream 
    #shall consist of a dictionary followed by zero or more bytes bracketed between 
    #the keywords stream(followed by newline) and endstream

    #The keyword stream that follows the stream dictionary shall be followed by an 
    #end-of-line marker consisting of either a CARRIAGE RETURN and a LINE FEED or 
    #just a LINE FEED, and not by a CARRIAGE RETURN alone.
    def t_STREAM_DATA(self, t):
        r'stream(\r\n|\n)'
        found = t.lexer.lexdata.find('endstream',t.lexer.lexpos)
        if found != -1:
            t.value = t.lexer.lexdata[t.lexer.lexpos: found]
            t.lexer.lexpos = found + 9
            t.type  = 'STREAM_DATA'
        else:
            raise Exception('Error:Parsing:Lexer: Could not found endstream string.')
        return t

    #7.3.9 Null Object
    #The null object has a type and value that are unequal to those of any 
    #other object. There shall be only one object of type null, denoted by 
    #the keyword null. 
    t_NULL = r'null'

    #7.3.10 Indirect Objects
    #Any object in a PDF file may be labelled as an indirect object.The 
    #definition of an indirect object in a PDF file shall consist of its 
    #object number and generation number(separated by white space), 
    #followed by the value of the object bracketed between the keywords 
    #obj and endobj.
    def t_OBJ(self, t):
        r'\d+\x20\d+\x20obj' #[0-9]{1,10} [0-9]+ obj'
        t.value = tuple([int(x) for x in t.value.split('\x20')[:2]])
        return t
    t_ENDOBJ = r'endobj'

    #The object may be referred to from elsewhere in the file by an indirect
    #reference. Such indirect references shall consist of the object number, 
    #the generation number, and the keyword R (with white space separating each
    #part):
    #EXAMPLE 12 0 R
    def t_R(self, t):
        r'\d+\x20\d+\x20R'
        t.value = tuple([int(x,10) for x in t.value.split('\x20')[:2] ])
        t.endlexpos=t.lexer.lexmatch.span(0)[1]
        return t
        
    #7.3.3 Numeric Objects
    #PDF provides two types of numeric objects: integer and real. Integer objects
    #represent mathematical integers. Real objects represent mathematical real numbers. 
    def t_NUMBER(self, t):
        r'[+-]{0,1}(\d*\.\d+|\d+\.\d*|\d+)' #34.5 -3.62 +123.6 4. -.002 0.0 123 43445 +17 -98 0
        return t

    #7.5.2 File Header
    #The first line of a PDF file shall be a header consisting of the 5 characters %PDF- 
    #followed by a version number of the form 1.N, where N is a digit between 0 and 7.
    def t_HEADER(self, t):
        r'%PDF-1\.[0-7]'
        t.endlexpos = t.lexer.lexmatch.span(0)[1]
        t.value = t.value[-3:]
        return t
        
    #7.5.4     Cross-Reference Table
    #Each cross-reference section shall begin with a line containing the keyword
    #xref. Following this line shall be one or more cross-reference subsections,
    #which may appear in any order.
    @TOKEN(r'xref[' + white_spaces_r +']*'+eol)
    def t_XREF(self, t):
        t.lexer.push_state('xref')    
        t.lexer.xref = []
        t.lexer.xref_start = t.lexpos
        
    def t_xref_XREFENTRY(self, t):
        r'\d{10}[ ]\d{5}[ ][nf](\x20\x0D|\x20\x0A|\x0D\x0A)'
        n = t.value.strip().split(' ')
        t.lexer.xref[len(t.lexer.xref)-1][1].append((int(n[0],10), int(n[1],10), n[2]))

    #EXAMPLE 1 The following line introduces a subsection containing five objects
    #numbered consecutively from 28 to 32.
    #          28 5
    @TOKEN(r'[0-9]+[ ][0-9]+[' + white_spaces_r +']*'+eol)
    def t_xref_SUBXREF(self, t):
        n = t.value.split(' ')
        t.lexer.xref.append(((int(n[0],10),int(n[1],10)),[]))
        
    def t_xref_out(self, t):
        r'.'
        t.lexer.pop_state()  
        t.type = 'XREF'
        t.value = t.lexer.xref
        t.lexer.lexpos -= 1
        t.lexpos=t.lexer.xref_start
        return t

    #TODO: Log, increment a warning counter, or even dismiss the file   
    def t_xref_error(self, t):
        logger.error('Lexing XREF')
        raise PDFLexer.Exception(t,'Scanning a normal XREF')

    #Nothing is ignored when lexing an xref
    t_xref_ignore = ''


    #7.5.5 File Trailer
    #The trailer of a PDF file enables a conforming reader to quickly find the
    #cross-reference table and certain special objects. Conforming readers 
    #should read a PDF file from its end. The last line of the file shall contain
    #only the end-of-file marker, %%EOF. The two preceding lines shall contain, 
    #one per line and in order, the keyword startxref and the byte offset in the 
    #decoded stream from the beginning of the file to the beginning of the xref 
    #keyword in the last cross-reference section. The startxref line shall be 
    #preceded by the trailer dictionary, consisting of the keyword trailer followed
    #by a series of key-value pairs enclosed in double anglebrackets (<< ... >>).
    #Thus, the trailer has the following overall structure:
    #       trailer
    #           << key1 value1
    #                key2 value2
    #                ...
    #                keyn valuen
    #           >>
    #       startxref
    #       Byte_offset_of_last_cross-reference_section
    #       %%EOF
    t_TRAILER = r'trailer'

    @TOKEN(r'startxref'+ '['+ white_spaces_r+']+[0-9]+')
    def t_STARTXREF(self, t):
        t.value = int(t.value[10:],10)
        return t
        
    #FYI: Probably trying to fix some ill transmitted pdfs some 
    #readers look for this marker in the las 1k bytes of the file
    t_EOF = r'%%EOF'

    #ignore the comments
    def t_ignore_COMMENT(self, t):
        r'%[^\n\r]*[\n\r]'
        if t.value.startswith('%%EOF'):
            t.type = 'EOF'
            return t
        logger.debug("Ignoring comment <%s> at pos %d!!"%(t.value.encode('string_escape'), t.lexer.lexpos))

    #Damn! A lexing error!!
    #TODO: Log, increment a warning counter, or even dismiss the file   
    def t_error(self, t):
        c = t.lexer.lexdata[t.lexer.lexpos]
        logger.error('Error at pos %d. Skipping byte %02x[%s]'%(t.lexer.lexpos, ord(c), c.isalpha() and c or '?'))
        raise PDFLexer.Exception(t,'Scanning limbo')

    #ignore white spaces
    t_ignore = white_spaces

    def build(self, **kwargs):
        self.lexer = lex.lex(object=self,**kwargs)
        return self.lexer

    def __init__(self):
        self.lexer = None

    def lexify(self,data):
        ''' This translate a plain string into a sequence of tokens '''
        # Give the lexer some input
        self.lexer.input(data+" ")
        toks = []
        while True:
             tok = self.lexer.token()
             if not tok: break
             toks.append(tok)
        return toks

if __name__ == '__main__':
    pdf_lexer = PDFLexer()
    pdf_lexer.build()
    for filename in sys.argv[1:]:
        try:
            print filename, pdf_lexer.lexify(file(filename,'r').read())
        except Exception,e:
            print 'Exception!',e, filename


