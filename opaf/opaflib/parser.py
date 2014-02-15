####################################################################
## felipe.andres.manzano@gmail.com  http://feliam.wordpress.com/  ##
## twitter.com/feliam        http://www.linkedin.com/in/fmanzano  ##
####################################################################
import sys,re
import traceback

import ply.yacc as yacc
from opaflib.lexer import PDFLexer 
from opaflib.xmlast import create_leaf, create_tree


#logging facility
import logging
logger = logging.getLogger("PARSER")

# This is required by PLY
tokens = PDFLexer.tokens

tokens = PDFLexer.tokens
#In PDF 1.5 and later, cross-reference streams may be used in 
#linearized files in place of traditional cross-reference tables.
#The logic described in this section, along with the appropriate 
#syntactic changes for cross-reference streams shall still apply.
def p_pdf(p):
    ''' pdf : HEADER pdf_update_list'''
    header = create_leaf('header', p[1], span=p.lexspan(1))
    p[0] = create_tree('pdf', [header] + p[2], span=p.lexspan(0), version="OPAF!" )

#7.3.6    Array Objects
#An array object is a one-dimensional collection of objects arranged
#sequentially. Unlike arrays in many other computer languages, PDF 
#arrays may be heterogeneous; that is, an array's elements may be 
#any combination of numbers, strings, dictionaries, or any other 
#objects, including other arrays. An array may have zero elements.

def p_array(p):
    ''' array : LEFT_SQUARE_BRACKET object_list RIGHT_SQUARE_BRACKET '''
    p[0] = create_tree('array', p[2], span=p.lexspan(0))

def p_object_list(p):
    ''' object_list : object object_list '''
    p[0] = [p[1]] + p[2]

def p_object_list_empty(p):
    ''' object_list : '''
    p[0] = []

#Objects
def p_object_name(p):
    ''' object : NAME '''
    p[0] = create_leaf('name', p[1], span=p.lexspan(1))

def p_object_string(p):
    ''' object : STRING '''                    
    p[0] = create_leaf('string', p[1], span=p.lexspan(1))
    
def p_object_hexstring(p):
    ''' object : HEXSTRING '''                    
    p[0] = create_leaf('string', p[1], span=p.lexspan(1))
    
def p_object_number(p):
    ''' object : NUMBER '''
    x = p[1]
    x = float(int(float(x))) == float(x) and int(float(x)) or float(x)
    p[0] = create_leaf('number', x, span=p.lexspan(1))
    
def p_object_true(p):
    ''' object : TRUE '''                    
    p[0] = create_leaf('bool', True, span=p.lexspan(1))

def p_object_false(p):
    ''' object : FALSE '''                    
    p[0] = create_leaf('bool', False, span=p.lexspan(1))

def p_object_null(p):
    ''' object : NULL '''                    
    p[0] = create_leaf('null', None, span=p.lexspan(1))
    
def p_object_ref(p):
    ''' object : R '''
    p[0] = create_leaf('R', p[1], span=p.lexspan(1))

#complex objexts
def p_object_dictionary(p):
    ''' object : dictionary '''
    p[0] = p[1]

def p_object_array(p):
    ''' object : array '''
    p[0] = p[1]
    
#7.3.7      Dictionary Objects
#A dictionary object is an associative table containing pairs of objects, 
#known as the dictionary's entries. The first element of each entry is the
#key and the second element is the value. The key shall be a name. The 
#value may be any kind of object, including another dictionary. A dictionary
#may have zero entries.
def p_dictionary(p):
    ''' dictionary : DOUBLE_LESS_THAN_SIGN dictionary_entry_list DOUBLE_GREATER_THAN_SIGN '''
    p[0] = create_tree('dictionary', p[2], span=(p.lexspan(1)[0], p.lexspan(3)[1]))
    
def p_dictionary_entry_list(p):
    ''' dictionary_entry_list : dictionary_entry_list NAME object
                              |  '''
    if len(p) == 1:
        p[0]=[]
    else:
        key_node = create_leaf('name', p[2], span=p.lexspan(2))
        dictionary_span = (p.lexspan(2)[0],p.lexspan(3)[1])
        dictionary_node = create_tree('entry', [key_node,p[3]], span=dictionary_span)
        p[0] = p[1] + [dictionary_node]


#7.3.10 Indirect Objects
#The definition of an indirect object in a PDF file shall consist of its 
#object number and generation number (separated by white space), followed
#by the value of the object bracketed between the keywords obj and endobj.
#EXAMPLE 1       Indirect object definition
#                12 0 obj
#                    ( Brillig )
#                endobj
def p_indirect(p):
    ''' indirect : indirect_object_stream
                 | indirect_object '''
    p[0] = p[1]


def p_indirect_object(p):
    ''' indirect_object : OBJ object ENDOBJ '''
    ref = "%d %d"%p[1]
    p[0] = create_tree('indirect_object', [p[2]], span=p.lexspan(0), id=ref)
    
def p_indirect_object_stream(p):
    ''' indirect_object_stream : OBJ dictionary STREAM_DATA ENDOBJ '''
    stream_data = create_leaf('data',p[3],span=(p.lexspan(2)[0],p.lexspan(4)[1]))
    stream = create_tree('stream',[p[2], stream_data],span=p.lexspan(0))
    p[0] =  create_tree('indirect_object', [stream],span=p.lexspan(0), id="%d %d"%p[1])

#pdf
#7.5    File Structure
#A basic conforming PDF file shall be constructed of following four elements:
# [-] A one-line header identifying the version of the PDF specification 
#     to which the file conforms
# [-] A body containing the objects that make up the document contained 
#     in the file
# [-] A cross-reference table containing information about the indirect 
#     objects in the file
# [-] A trailer giving the location of the cross-reference table and of 
#     certain special objects within the body of the file
def p_xref_common(p):
    ''' xref : XREF TRAILER dictionary '''
    data = create_leaf('data', str(p[1]), span=p.lexspan(0))
    p[0] = create_tree('xref',[p[3], data], span=p.lexspan(0))

# 7.5.8.1:: Therefore, with the exception of the startxref address %%EOF
# segment and comments, a file may be entirely a sequence of objects.
def p_xref_stream(p):
    ''' xref : indirect_object_stream '''
    p[0] =  p[1]

#PDF_UPDATE_LIST
def p_pdf_update(p):
    ''' pdf_update : body xref pdf_end '''
    p[0] = create_tree('pdf_update', p[1]+[p[2],p[3]],span=(0xffffffff,-1))
    [p[0].span_expand(e.span) for e in p[1]+[p[2],p[3]]]

#PDF_UPDATE_LIST
def p_pdf_end(p):
    ''' pdf_end : STARTXREF EOF'''
    p[0] = create_leaf('startxref', p[1], span=p.lexspan(0))

def p_pdf_update_list(p):    
    ''' pdf_update_list : pdf_update_list pdf_update '''
    p[0] = p[1] + [p[2]]

def p_pdf_update_list_one(p):    
    ''' pdf_update_list : pdf_update '''
    p[0] = [p[1]]
    
def p_body_object(p):
    ''' body : body indirect_object 
             | body indirect_object_stream '''
    p[0] = p[1]+[p[2]]
    
def p_body_void(p):
    ''' body : '''
    p[0] = []

def p_error(p):
    if not p:
        logger.error("EOF reached!")
    else:
        logger.error("Syntax error at [%d] %s %s"%(p.lexpos, p.value,p.type))

#Used in BRUTE parsing
def p_pdf_brute_end(p):
    ''' pdf_brute_end : XREF TRAILER  dictionary STARTXREF EOF'''
    xref = create_tree('xref', [p[3]],span=(0,p.lexspan(4)[0]-1), xref=p[1])
    pdf_end = create_leaf('startxref', p[4], span=(p.lexspan(4)[0],p.lexspan(0)[1]))
    p[0] = [xref, pdf_end] 


# Build the parsers
parsers = {}              
starts = ['pdf','object', 'indirect', 'pdf_brute_end' ]

def generate_parsers():
    ''' 
        Generate the PLY parsers.
        This should be called from the setup
    '''
    for tag in starts:
        logger.info("Building parsing table for tag %s"%tag)
        start = tag
        yacc.yacc(start=tag, tabmodule='parsetab_%s'%tag, outputdir='opaflib')

#Load the parsers
for tag in starts:
    logger.info("Building parsing table for tag %s"%tag)
    start = tag
    parsers[tag] = yacc.yacc(start=tag, tabmodule='opaflib.parsetab_%s'%tag, write_tables=0)


def parse(tag,stream):
    '''
       Entry function to parse a whole pdf or portion of it..
    '''
    logger.debug("Parsing an object of type <%s>"%tag)
    lexer = PDFLexer().build(debug=False,errorlog=logger)
    return parsers[tag].parse(stream,tracking=True,lexer=lexer)

def normalParser(pdf):
    '''
        This will try to apply the grammar described here 
        http://feliam.wordpress.com/2010/08/22/pdf-sequential-parsing/

        Assuming endstreams are no appearing inside streams 
        we can apply an eager parser and do not Need the xref
    '''
    return parse('pdf',pdf)

def bruteParser(pdf):
    '''
        This will try to parse any object in the file based on obj/endobj and few other kewords.
        This is an ad-hoc parsing wich will try to read the file in any posile way. 
        It may produce phantom overlaped XML objects. Yo may check this issues afterwards.
        Also it is slow.
    '''
    try:
        #Search for the PDF header
        headers = list(re.finditer(r'%PDF-1\.[0-7]',pdf))
        xml_headers = []
        for header in headers:
            start = header.start()
            end = header.end()
            version = header.group(0)[-3:]
            xml_headers.append(create_leaf('header', version,span=(start,end)))
        logger.info('Found %d headers'%len(xml_headers))
        
        #Search the startxref. And xrefs.
        startxrefs = list(re.finditer(r'startxref[\x20\r\n\t\x0c\x00]+[0-9]+[\x20\r\n\t\x0c\x00]+%%EOF',pdf))
        xrefs = list(re.finditer(r'xref',pdf))    
        xml_xrefs = []
        xml_pdf_ends = []
        for xref in xrefs:
            start = xref.start()
            for end in [x.end() for x in startxrefs if x.start()>xref.end()]:
                logger.info("Searching for a xref, trailer and %%%%EOF at [%s:%s]"%(start,end))
                potential_xref = pdf[start:end]
                try:
                    xml_xref, xml_pdf_end = parse('pdf_brute_end', potential_xref)
                    #fix lexspan and append
                    xml_xref.span_move(start)
                    xml_xrefs.append(xml_xref)
                    #fix lexspan and append
                    xml_pdf_end.span_move(start)
                    xml_pdf_ends.append(xml_pdf_end)
                except Exception, e:
                    print e
                    logger.info("Couldn't parse a xref, trailer and %%%%EOF at [%s:%s] (%s)"%(start,end,e))

        #use the force
        #This algorithm will try to match any obj with any endobj and will keep it 
        #if a sane object is found inside. Overlapping is possible here, you may analize it
        #cut it off from the xml later, using the lexspan markers.
        delimiter = r"[()<>\[\]/%\x20\r\n\t\x0c\x00]"
        objs = list(re.finditer(r'\d+\x20\d+\x20obj'+delimiter, pdf))
        endobjs = list(re.finditer(delimiter+r'endobj', pdf))
        streams = list(re.finditer(delimiter+'stream'+delimiter, pdf))
        endstreams = list(re.finditer('endstream'+delimiter+'endobj', pdf))
        xml_iobjects = []
        logger.info("Found %d Object starting points"%len(objs))
        logger.info("Found %d Object ending points"%len(endobjs))
        for m in objs:
            start = m.start()
            for end in [x.end() for x in endobjs if x.start()>m.end()]:
                try:
                    logger.debug("Parsing potential object at %s~%s"%(start,end))
                    potential_obj = pdf[start:end]
                    
                    '''
                    DISABLED
                    # If for some reason there are "endstreams" keywords inside the 
                    # stream let's momentaneaously escape them, so it can be parsed  
                    # with the strict parser
                    escape_endstreams = [e.start()+start for e in endstreams if e.start()>start and e.end()<end ]
                    for e in escape_endstreams[:-1]:
                        potential_obj = potential_obj[:e] +"X"*9 + potential_obj[e+9:]
                    '''
                    
                    #Try to strictly parse an indirect object
                    xml_iobject = parse('indirect',potential_obj)

                    #fix lexspan
                    xml_iobject.span_move(start)

                    '''
                    DISABLED
                    #FIX: fix escape
                    #WRONG offset!!!!!!!!!!!!
                    pl = payload(xml_iobject)
                    #Un-escape the "endstream" keywords
                    for e in escape_endstreams[:-1]:
                        pl = pl[:e] +"endstream" + pl[e+9:]
                    setpayload(xml_iobject, pl)
                    '''

                    #append to the list
                    xml_iobjects.append(xml_iobject)

                    #Just parse the first object we can of this try.
                    #Comment out the following line to search for phantoms 
                    #(i.e. objects inside objects or overlaped objects)
                    break
                except Exception,e:
                    logger.debug("Received exception %s when parsing potential object at [%s:%s]."%(e, start,end))
        logger.info("Succesfully parsed %d/%d Objects ending points"%(len(xml_iobjects),len(endobjs)*len(objs)))

        #sum all the objects
        allobjects = xml_headers + xml_xrefs + xml_pdf_ends + xml_iobjects

        if len(xml_pdf_ends) == 0:
            logger.info("%%%%EOF tag was not found! Creating a dummy.")
            dummy_startxref = create_leaf('startxref', -1, span=(len(pdf),len(pdf)))
            print dummy_startxref.value
            allobjects.append(dummy_startxref)

        if len(xml_headers) == 0:
            logger.info("%%%%PDF-N-M tag was not found! Creating a dummy.")
            allobjects.append(create_leaf('header', "NOVERSION", span=(0,0)))

        #Sort it as they appear in the file
        allobjects = sorted(allobjects,lambda x,y: cmp(x.span[0], y.span[0]))

        #recreate XML structure 'best' we can...
        assert allobjects[0].tag == 'header'
        root_element = create_tree('pdf', [allobjects.pop(0)], span=(0,len(pdf)), version="OPAF!(raw)")
        
        update = create_tree('pdf_update', [],span=(0xfffffff,-1))
        while len(allobjects)>0:
            thing = allobjects.pop(0)
            update.append(thing)
            update.span_expand(thing.span)
            if thing.tag == 'startxref':
                root_element.append(update)
                update = create_tree('pdf_update',[],span=(0xfffffff,-1))

        if len(update)>0:
            logger.info("Missing ending %%EOF")
            root_element.append(update)

        return root_element
    except Exception,e:
        print e,e,e
        raise e

def xrefParser(pdf):
    '''
        This will try to parse the pdf based on the tree of cross references.
        Hard, uninmplemented and insane.
    '''
    assert False, "Uninmplemented!"
    if False:                
        try:
            xrefpos = int(pdf[startxrefpos+9:])     
        except:
            logger.info("Damn! Startxref is broken! Lower chances of parsing this..")
            #Idea: look for lowest xref/Root an try there
            #If not try obj/endobj
            assert False, "Unimplemented"
        if pdf[xrefpos].isnum() :
            logger("Main cross reference is a XrefStream")
            assert False, "Unimplemented"
        elif pdf[xrefpos:xrefpos+5] == "xref" :
            logger("Main cross reference is a NoRMAL xref")
            assert False, "uninmplemented"                                    
        else:
            logger("XREF not found. Is this a pdf? Where did you get this?")
            assert False, "uninmplemented"                    
    #cri cri...

def multiParser(pdf):
    ''' 
        Try the different parsing strategies in some preference order...
    '''
    #fallback chain of different type of parsing algorithms
    try:
        return normalParser(pdf)
    except Exception, e:
        logger.info("PDF is NOT a sequence of objects as it SHALL be, for discussion see http://bit.ly/coRMtc ("+str(e)+")")
    try:
        return bruteParser(pdf)
    except Exception, e:
        logger.error("Can not parse it with a relaxed parser either ("+str(e)+")")
    try:
        return xrefParser(pdf)
    except Exception, e:
        logger.info("Couldn't parse it. Damn! ("+str(e) +")")
    return None


#Example main    
if __name__ == '__main__':
    bytes = 0
    files = 0
    for filename in sys.argv[1:] :
        print filename
        try:
            s = file(filename,"r").read()
            files += 1
            bytes += len(s)
            result = multiParser(s)
            print(etree.tostring(result, pretty_print=True))
        except Exception,e:
            print "Pucha!", e

