from lxml import etree
from opaflib.filters import defilterData
#Logging facility
import logging,code 
logger = logging.getLogger("OPAFXML")

class PDFXML(etree.ElementBase):
    ''' Base pdf-xml class. Every pdf token xml representation will
        have a span wich indicates where the original token layed in the file
    '''
    def _getspan(self):
        return tuple([int(i) for i in self.get('span').split('~')])
    def _setspan(self, value):
        self.set('span',"%d~%d"%value)
    def span_move(self,offset, recursive=True):
        begin,end = self.span 
        self.span = (begin+offset,end+offset)
        if recursive:
            for child in self.getchildren():
                child.span_move(offset)
    def span_expand(self,span):
        begin,end = self.span 
        self.span = (min(begin,span[0]),max(end,span[1]))        

    def clear_span(self, recursive=True):
        del self.attrib['span']
        for child in self.getchildren():
            child.clear_span()
    span = property(_getspan,_setspan)

    def _to_xml(self):
        return etree.tostring(self)
    xml = property(_to_xml)

    def _from_python(self, value):
        self.from_python(value)
    def _to_python(self):
        return self.to_python()
    value = property(_to_python,_from_python)
    
    def __getattr__(self, name):
        tags = set([e.tag for e in self])
        if name in tags:
            return self.xpath('./%s'%name)
        return getattr(super(PDFXML,self),name)
        
    
    def get_numgen(self):
        ''' Search the object and generation number of any pdf element '''
        if self.tag.startswith('indirect'):
            return self.id
        else:
            return self.getparent().get_numgen()


#leaf
class PDFString(PDFXML):
    def from_python(self, value):
        self.text = value.encode('string_escape')
    def to_python(self):
        return self.text.decode('string_escape')
    
class PDFName(PDFString):
    pass
    
class PDFData(PDFString):
    pass

class PDFBool(PDFString):
    def from_python(self, value):
        assert type(value) == bool, 'Value must be a boolean'
        self.text = ['false','true'][int(value)]
    def to_python(self):
        return {'false': False, 'true': True}[self.text]

class PDFNull(PDFString):
    def from_python(self, value):
        assert value is None, 'Value must be None'
        self.text = 'null'
    def to_python(self):
        assert self.text == 'null', 'PDFNull xml not initialized'
        return None
    
class PDFR(PDFString):
    def from_python(self, (n,g)):
        assert type(n) == int and type(g) == int, 'R must be two numbers, n and g'
        assert n >= 0 and n < 65535 , 'Invalid object number (%d)'%n
        assert g >= 0 and g < 65535 , 'Invalid generation number (%d)'%g
        self.text = "%d %d"%(n,g)
    def to_python(self):
        return tuple([int(i) for i in self.text.split(' ')])

    def solve(self):
        ''' search the referenced indirect object in the containing pdf '''
        pdf = self.xpath('/*')[0]
        return pdf.getIndirectObject(self.value)
        
class PDFNumber(PDFXML):
    def from_python(self, value):
        assert type(value) in [int, float], 'Wrong type for a number'
        self.text = str(value)
    def to_python(self):
        x = self.text
        return float(int(float(x))) == float(x) and int(float(x)) or float(x)

class PDFStartxref(PDFString):
    def from_python(self, value):
        assert type(value) == int ,  'Wrong type for startxref'
        self.text = str(value).encode('string_escape')
    def to_python(self):
        return int(self.text.decode('string_escape'))

class PDFHeader(PDFString):
    pass
#tree


class PDFEntry(PDFXML):
    def to_python(self):
        return tuple([e.value for e in self.getchildren()])

    def _getkey(self):
        return self[0]
    def _setkey(self, key):
        assert key.tag == 'name'
        self[0] = key
    key = property(_getkey,_setkey,None)

    def _getval(self):
        return self[1]
    def _setval(self, val):
        self[1] = val
    val = property(_getval,_setval,None)

    
class PDFDictionary(PDFXML):
    def to_python(self):
        return dict([e.value for e in self.getchildren()])

    def has_key(self,key):
        return len(self.xpath('./entry/name[position()=1 and text()="%s"]'%key))>0
    def __getitem__(self, i):
        if str == type(i):
            return self.xpath('./entry/name[position()=1 and text()="%s"]/../*[position()=2]'%i)[0]
        return super(PDFDictionary,self).__getitem__(i)
    def __delitem__(self, i):
        if str == type(i):
            return self.remove(self.xpath('./entry/name[position()=1 and text()="%s"]/..'%i)[0])
        return super(PDFDictionary,self).__delitem__(i)
    def __setitem__(self, key, val):
        if str == type(key):
            self.xpath('./entry/name[position()=1 and text()="%s"]/..'%key)[0].val=val
        else:
            super(PDFDictionary,self).__setitem__(key,val)
    

class PDFStream(PDFXML):
    def to_python(self):
        return {'dictionary':self[0].value, 'data':self[1].value}

    def _getdictionary(self):
        return self[0]
    def _setdictionary(self, d):
        assert key.tag == 'dictionary'
        self[0] = d
    dictionary = property(_getdictionary,_setdictionary,None)

    def _getdata(self):
        return self[1]
    def _setdata(self, data):
        assert data.tag == 'data'
        self[1] = data
    data = property(_getdata,_setdata,None)


    def isFiltered(self):
        ''' Check if stream is filtered '''
        return self.dictionary.has_key('Filter')

    def getFilters(self):
        val = self.dictionary.value
        filters = val.get('Filter',None)
        params = val.get('DecodeParams',None)

        assert any([type(filters) == list and (type(params) == list or params==None ),
            type(filters) != list and (type(params) == dict or params==None ) ]), 'Filter/DecodeParms wrong type'

        if type(filters) != list:
            filters=[filters]
            params=params and [params] or [{}]

        if params == None:
            params = [{}]*len(filters)
            
        assert all([type(x)==str for x in filters]), 'Filter shall be a names'
        assert all([type(x)==dict for x in params]), 'Params should be a dictionary.. or null?'
        assert len(filters) == len(params),'Number of Decodeparams should match Filters'
        return zip(filters,params)

    def popFilter(self):
        dictionary = self.dictionary
        assert dictionary.has_key('Filter'), 'Stream not Filtered!'

        selected_filter = None
        selected_params = None
        
        deletion_list = []
        
        
        if dictionary['Length'].value != len(self.data.value):
            logger.info("Length field of object %s does not match the actual data size (%d != %d)"%(str(self.get_numgen()),dictionary['Length'].value,len(self.data.value)))
        
        if type(dictionary['Filter']) == PDFArray:
            selected_filter = dictionary['Filter'][0]
            del dictionary['Filter'][0]
            if dictionary.has_key('DecodeParms'):
                assert dictionary['DecodeParms'] == PDFArray, 'Array of filters need array of decoding params'
                selected_params = dictionary['DecodeParms'][0]
                deletion_list.append((dictionary['DecodeParms'],0))
                #del dictionary['DecodeParms'][0]
        else:
            selected_filter = dictionary['Filter']
            del dictionary['Filter']
            if dictionary.has_key('DecodeParms'):
                selected_params = dictionary['DecodeParms']
                deletion_list.append((dictionary, 'DecodeParms'))
                #del dictionary['DecodeParms']
            
        if dictionary.has_key('Filter') and \
           type(dictionary['Filter']) == PDFArray and \
           len(dictionary['Filter']) == 0:
                deletion_list.append((dictionary, 'Filter'))
                #del dictionary['Filter']
        if dictionary.has_key('DecodeParms') and \
               type(dictionary['DecodeParms']) == PDFArray and \
               len(dictionary['DecodeParms']) == 0:
                deletion_list.append((dictionary, 'DecodeParms'))
                #del dictionary['DecodeParms']
        #FIX recode defilterData .. make it register/unregister able. 
        #(think /Crypt 7.4.10 Crypt Filter )
        self.data.value = defilterData(selected_filter.value,self.data.value, selected_params and selected_params.value or selected_params)
        for v,i in deletion_list:
            del v[i]
        dictionary['Length'].value = len(self.data.value)
            
    def defilter(self):
        try:
            while self.isFiltered():
                self.popFilter()
        except Exception,e:
            logger.debug("Couldn't defilter <%s> stream (exception %s)."%(self.value,str(e)))
            logger.info("Couldn't defilter <%s> stream."%str(self.get_numgen()))

    def isObjStm(self):
        ''' Return true if this is an object stream (ObjStml) '''
        return self.dictionary.has_key('Type') and self.dictionary['Type'].value == 'ObjStm'

    def expandObjStm(self):
        '''
            This parses the ObjStm structure and replace it with all the new 
            indirect objects.
        '''
        from opaflib.parser import parse
        assert not self.isFiltered(), "ObjStm should not be compressed at this point"
        assert self.dictionary.has_key('N'), "N is mandatory in ObjStm dictionary"
        assert self.dictionary.has_key('First'), "First is mandatory in ObjStm dictionary"


        dictionary = self.dictionary
        data = self.data.value
        first = dictionary["First"].value
        pointers =  [int(x) for x in data[:first].split()]
        assert len(pointers)%2 == 0 , "Wrong number of integer in the ObjStm begining"
        pointers = dict([(pointers[i+1]+first,pointers[i]) for i in range(0,len(pointers),2) ])
        positions = sorted(pointers.keys() + [len(data)])
        
        parsed_objects = []
        for p in range(0,len(positions)-1):
            logger.info("Adding new object %s from objectstream"%repr((pointers[positions[p]],0)))
            io = PDF.indirect_object(parse('object', data[positions[p]:positions[p+1]]+" "))
            io.id = (pointers[positions[p]],0)
            parsed_objects.append(io)
        return parsed_objects



class PDFArray(PDFXML):
    def to_python(self):
        return [e.value for e in self]

class PDFIndirect(PDFXML):
    def to_python(self):
        assert len(self.getchildren())==1, "Wrong number of children in indirect object"
        return (self.id, self.object.value)

    def _getobject(self):
        return self[0]
    def _setobject(self, o):
        self[0] = o
    object = property(_getobject,_setobject,None)

    def _getid(self):
        return tuple([int(i) for i in self.get('id').split(' ')])
    def _setid(self, o):
        self.set('id', "%d %d"%o)
    id = property(_getid,_setid,None)
    
    def isStream(self):
        return len(self.xpath('./stream'))==1


class PDFPdf(PDFXML):
    def to_python(self):
        return [e.value for e in self]
    def getStartxref(self):
        ''' Get the last startxref pointer (should be at least one) '''
        return self.pdf_update[-1].startxref[-1]

    #FIX move all this to pdf_update and do the wrapper here
    def getObjectAt(self, pos):
        ''' Get the object found at certain byte position '''
        return self.xpath('//*[starts-with(@span,"%d~")]'%pos)[0]

    def getTrailer(self, startxref=None):
        ''' Get the Trailer dictionary (should be at least one) '''
        if startxref == None:
            startxref = self.getStartxref().value
        xref = self.getObjectAt(startxref)
        assert xref.tag in ['xref', 'stream'] and xref[0].tag == 'dictionary'
        return xref[0]

    def getID(self, startxref=None):
        ''' Get the pdf ID from the trailer dictionary '''
        trailer = self.getTrailer(startxref).value
        if trailer.has_key('ID'):
            return trailer['ID']
        else:
            return ['','']
     
    def getIndirectObject(self, ref):
        ''' Search for an indirect object '''
        for u in self.pdf_update:
            if u.has_key(ref):
                return u[ref]
        
    def getRoot(self):
        ''' Get the pdf Root node. '''
        return self.getIndirectObject(self.getTrailer()['Root'].value).object

    def isEncrypted(self):
        ''' Return true if pdf is encrypted '''
        return self.getTrailer().has_key('Encrypt')

    def countObjStm(self):
        ''' Count number of 'compressed' object streams '''
        return len(self.xpath('//stream/dictionary/entry/name[position()=1 and text()="Type"]/../name[position()=2 and text()="ObjStm"]/../../..'))
    def countIObj(self):
        ''' Count number of 'compressed' object streams '''
        return len(self.xpath('//indirect_object'))
   
    def graph(xml_pdf,dot='default.dot'):
        ''' Generate a .dot graph of the pdf '''
        dotdata = "digraph  {\n"
        
        nodes_added = set()
        for io in self.pdf_update.indirect_object:            
            references = io.xpath(".//R")
            orig = "%d %d"%io.id
            if len(references) == 0:
                dotdata += '\t"%s";\n'%x
                nodes_added.add(orig)
            else:
                for r in references:
                    dest = "%d %d"%r.value
                    dotdata += '\t"%s" -> "%s";\n'%(orig, dest)
                    nodes_added.add(orig)
                    nodes_added.add(dest)


        try:
            root = "%d %d"%self.getRoot()
            dotdata += '\t"trailer" -> "%s";\n'%root
        except Exception,e :
            pass
        dotdata += '}\n'
        logger.info("Writing graph to %s(a dot file). Download graphviz or try this http://rise4fun.com/Agl for render it."%dot)
        file(dot,"w").write(dotdata)
   
    def expandAllObjStm(self):
        ''' Find all object streams and expand them. Each ObjStm will be replaced
            by its childs '''
        for u in self.pdf_update:
            for ref in u.findAllObjStm():
                u.expandObjStm(ref)

    def defilterAll(self):
        ''' Find all object streams and expand them. Each ObjStm will be replaced
            by its childs '''
        for u in self.pdf_update:
            for io in u[:]:
                if type(io) == PDFIndirect and io.isStream() and io.object.isFiltered():
                    io.object.defilter()

    def decrypt(self):
        ''' This will try to decrypt V:4 null password encryption '''
        import hashlib, struct
        from Crypto.Cipher import AES 
        from Crypto.Util import randpool 
        import base64 

        def rc4crypt(data, key):
            x = 0
            box = range(256)
            for i in range(256):
                x = (x + box[i] + ord(key[i % len(key)])) % 256
                box[i], box[x] = box[x], box[i]
            x = 0
            y = 0
            out = []
            for char in data:
                x = (x + 1) % 256
                y = (y + box[x]) % 256
                box[x], box[y] = box[y], box[x]
                out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))
            
            return ''.join(out)

        block_size = 16 
        key_size = 32 

        def encrypt(plain_text,key_bytes):
            assert len(key_bytes) == key_size
            mode = AES.MODE_CBC 

            pad = block_size - len(plain_text) % block_size 
            data = plain_text + pad * chr(pad) 
            iv_bytes = randpool.RandomPool(512).get_bytes(block_size) 
            encrypted_bytes = iv_bytes + AES.new(key_bytes, mode, iv_bytes).encrypt(data) 
            return encrypted_bytes

        def decrypt(encrypted_bytes,key_bytes):
            #assert len(key_bytes) == key_size
            mode = AES.MODE_CBC 
            iv_bytes = encrypted_bytes[:block_size] 
            plain_text = AES.new(key_bytes, mode, iv_bytes).decrypt(encrypted_bytes[block_size:]) 
            pad = ord(plain_text[-1]) 
            return plain_text[:-pad] 
        
        
        assert self.isEncrypted()
        
        #Get and print the encryption dictionary
        encrypt = self.getTrailer()['Encrypt'].solve().object

        print "It's ENCRYPTED!"
        encrypt_py = encrypt.value
        print encrypt_py

        #Ok try to decrypt it ...
        assert encrypt_py['V'] == 4, "Sorry only Version 4 supported"
        assert encrypt_py['R'] == 4, "Sorry only Version 4 supported"

        #password length
        n = encrypt_py['Length']/8
        print "N:",n

        #a) Pad or truncate the password string to exactly 32 bytes. 
        user_password = ""
        pad = "28BF4E5E4E758A4164004E56FFFA01082E2E00B6D0683E802F0CA9FE6453697A".decode('hex')

        print "PASSWORD: ", user_password.encode('hex')
        print "PAD: ", pad.encode('hex')

        #b) Initialize the MD5 hash function and pass the result of step (a) as input to this function.
        m = hashlib.md5()
        m.update((user_password+pad)[:32])
        print "MD5 update 1", ((user_password+pad)[:32]).encode('hex')

        #c) Pass the value of the encryption dictionary's O entry to the MD5 hash function.
        m.update (encrypt_py['O'][:32])
        print "MD5 update 2", (encrypt_py['O'][:32]).encode('hex')

        #d) Convert the integer value of the P entry to a 32-bit unsigned binary number and pass these bytes to the
        #  MD5 hash function, low-order byte first.  WTF!!??
        print "MD5 update 3", struct.pack("<L", 0xffffffff&encrypt_py['P']).encode('hex')
        m.update (struct.pack("<L",  0xffffffff&encrypt_py['P']   ))

        #e) append ID ?
        #TODO, get the ID from the trailer..
        ID = ''
        m.update (ID)
        print "MD5 update 4", ID.encode('hex')

        #f) If document metadata is not being encrypted, pass 4 bytes with the value 0xFFFFFFFF to the MD5 hash function.
        if encrypt_py.has_key('EncryptMetadata') and encrypt_py['EncryptMetadata'] == false:
            m.update('\xff'*4)
            print "MD5 update 5", ('\xff'*4).encode('hex')

        print "1rst DIGEST:", m.digest().encode('hex')
        h = m.digest()[:n]

        for i in range(0,50):
            h = hashlib.md5(h[:n]).digest()
            print "Encryption KEY(%d)"%i, h.encode('hex')
            
        key = h[:n]
        print "Encryption KEY", key.encode('hex')

        print "Try to authenticate"

        _buf = hashlib.md5(pad + ID).digest()
        print "MD5(padding+ID):",_buf.encode('hex')

        for i in range(0,20):
            _key = ''.join([chr(ord(k)^i) for k in list(key)])
            _buf1 = rc4crypt(_buf,_key)
            print "RC4 iter(%d) Encrypt data <%s> with key <%s> and it gives data <%s>"%(i,_buf.encode('hex'),_key.encode('hex'),_buf1.encode('hex'))
            _buf = _buf1


        assert _buf == encrypt_py['U'][:16]
        print "Authenticated! (An actual pass is not needed. Using null pass '' )"
        print "U", encrypt_py['U'].encode('hex')
        print "O", encrypt_py['O'].encode('hex')

        def decrypt_xml(xml_element):
            n,g = xml_element.get_numgen()
            m = hashlib.md5()
            m.update(key)
            m.update(chr(n&0xff))
            m.update(chr((n>>8)&0xff))
            m.update(chr((n>>16)&0xff))
            m.update(chr(g&0xff))
            m.update(chr((g>>8)&0xff))
            m.update("sAlT")
            real_key = m.digest()
            pld = e.value
            if pld.endswith("\x0d\x0a"):
                pld = pld[:-2]
            pld = decrypt(pld,real_key)
            e.value=pld

        #decrypt every string and stream in place...
        for e in self.xpath('//stream/data'):
            decrypt_xml(e)
        for e in self.xpath('//string'):
            decrypt_xml(e)




class PDFUpdate(PDFXML):
    def to_python(self):
        return dict([e.value for e in self.xpath('./indirect_object')])

    def has_key(self,key):
        key = "%d %d"%key
        return len(self.xpath('./indirect_object[@id="%s"]'%key))>0
    def __getitem__(self, key):
        if tuple == type(key):
            key = "%d %d"%key
            return self.xpath('./indirect_object[@id="%s"]'%key)[0]
        return super(PDFUpdate,self).__getitem__(key)
    def __delitem__(self, key):
        if tuple == type(key):
            key = "%d %d"%key
            return self.remove(self.xpath('./indirect_object[@id="%s"]'%key)[0])
        return super(PDFUpdate,self).__delitem__(key)
    def __setitem__(self, key, val):
        if str == type(key):
            self.xpath('./indirect_object[@obj="%s"]'%key)[0][:]=[val] #mmm
        else:
            super(PDFDictionary,self).__setitem__(key,val)
    
    def getObjectAt(self, pos):
        ''' Get the object found at certain byte position (only in this update!)'''
        return self.xpath('.//*[starts-with(@span,"%d~")]'%pos)[0]

    def getTrailer(self, startxref=None):
        ''' Get the Trailer dictionary (of this update!)'''
        if startxref == None:
            startxref = self.getStartxref().value
        xref = self.getObjectAt(startxref)
        return xref.dictionary
             
    def getRoot(self):
        ''' Get the pdf Root node of this update. '''
        return self[self.getTrailer()['Root'].value].object

    def countObjStm(self):
        ''' Count number of 'compressed' object streams '''
        return len(self.xpath('.//stream/dictionary/entry/name[position()=1 and text()="Type"]/../name[position()=2 and text()="ObjStm"]/../../..'))
   
    def expandObjStm(self, ref):
        io_objstm = self[ref]
        assert io_objstm.object.dictionary['Type'].value == 'ObjStm'

        #completelly defilter the object stream
        while io_objstm.object.isFiltered():
            io_objstm.object.popFilter()

        #parse the indirect simpe objects  inside it
        expanded_iobjects = io_objstm.object.expandObjStm()

        #replace the object stream by its childs
        for new_io in expanded_iobjects:
            io_objstm.addnext(new_io)
        self.remove(io_objstm)
    
    def findAllObjStm(self):
        ''' Search  'compressed' object streams ids/refs'''
        return [io.id for io in self.xpath('.//stream/dictionary/entry/name[position()=1 and text()="Type"]/../name[position()=2 and text()="ObjStm"]/../../../..')]
        
    def expandAllObjStm(self):
        for ref in self.findAllObjStm():
            self.expandObjStm(ref)
#Factory
class PDFXMLFactory():
    def __init__(self):
        self.parser = etree.XMLParser()
        fallback = etree.ElementDefaultClassLookup(PDFXML)
        lookup = etree.ElementNamespaceClassLookup(fallback)
        namespace = lookup.get_namespace(None)
        #leafs
        namespace['name'] = PDFName
        namespace['string'] = PDFString
        namespace['number'] = PDFNumber
        namespace['null'] = PDFNull
        namespace['bool'] = PDFBool
        namespace['R'] = PDFR
        namespace['header'] = PDFHeader
        namespace['startxref'] = PDFStartxref
        namespace['data'] = PDFData
        #trees
        namespace['entry'] = PDFEntry
        namespace['dictionary'] = PDFDictionary
        namespace['stream'] = PDFStream
        namespace['pdf'] = PDFPdf
        namespace['pdf_update'] = PDFUpdate
        namespace['indirect_object'] = PDFIndirect
        namespace['array'] = PDFArray
        self.parser.set_element_class_lookup(lookup)

    #leaf
    def create_leaf(self, tag, value,**attribs):
        assert tag in ['number','string','name','R','startxref','header','data','null','bool'], "Got wrong leaf tag: %s"%tag
        xml = self.parser.makeelement(tag)
        xml.value=value
        xml.span=attribs.setdefault('span', (0xffffffff,-1))
        del attribs['span']
        for attr_key, attr_val in attribs.items():
            xml.set(attr_key, str(attr_val))
        return xml

    #Tree
    def create_tree(self, tag, *childs, **attribs):
        assert tag in ['indirect_object','dictionary', 'entry', 'array', 'stream', 'xref', 'pdf', 'pdf_update'], "Got wrong tree tag: %s"%tag
        xml = self.parser.makeelement(tag)
        xml.span=attribs.setdefault('span', (0xffffffff,-1))
        del attribs['span']
        for attr_key, attr_val in attribs.items():
            xml.set(attr_key, str(attr_val))
        for child in childs:
            xml.append(child)        
        return xml
    
    def __getattr__(self,tag, *args,**kwargs):
        if tag in ['number','string','name','R','startxref','header','data','null','bool']:
            return lambda payload, **my_kwargs: self.create_leaf(tag, payload, **my_kwargs)
        elif tag in ['indirect_object','dictionary', 'entry', 'array', 'stream', 'xref', 'pdf', 'pdf_update']:
            return lambda payload, **my_kwargs: self.create_tree(tag, *payload, **my_kwargs)
        return super(PDFXMLFactory,self).__getattr__(tag,*args,**kwargs)
            
PDF = PDFXMLFactory()
def create_leaf(tag, value, **kwargs):
    return PDF.create_leaf(tag, value,**kwargs)
def create_tree(tag, childs, **kwargs):
    return PDF.create_tree(tag, *childs, **kwargs)

if __name__=="__main__":
    name = create_leaf('name', "Name")
    string = create_leaf('string', "Felipe")
    entry = create_tree('entry',[name,string])
    dictionary = create_tree('dictionary',[entry])
    stream_data = create_leaf('data',"A"*100)
    stream = create_tree('stream',[dictionary,stream_data])
    indirect = create_tree('indirect_object', [stream], obj=(1,0))
    array = create_tree('array', [create_leaf('number', i) for i in range(0,10)])
    xml=indirect
    print etree.tostring(xml), xml.value
    
    import code
    code.interact(local=locals())

