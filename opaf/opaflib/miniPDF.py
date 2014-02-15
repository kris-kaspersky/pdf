##########################################################################
####   Felipe Andres Manzano     *   felipe.andres.manzano@gmail.com  ####
####   http://twitter.com/feliam *   http://wordpress.com/feliam      ####
##########################################################################
import struct

#For constructing a minimal pdf file
## PDF REference 3rd edition:: 3.2 Objects
class PDFObject:
    def __init__(self):
        self.n=None
        self.v=None
    def __str__(self):
        raise Exception("Fail")

## PDF REference 3rd edition:: 3.2.1 Booleans Objects
class PDFBool(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s
    def __str__(self):
        if self.s:
            return "true"
        return "false"

## PDF REference 3rd edition:: 3.2.2 Numeric Objects
class PDFNum(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s
    def __str__(self):
        return "%s"%self.s

## PDF REference 3rd edition:: 3.2.3 String Objects
class PDFString(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s
    def __str__(self):
        return "(%s)"%self.s

## PDF REference 3rd edition:: 3.2.3 String Objects / Hexadecimal Strings
class PDFHexString(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s
    def __str__(self):
        return "<" + "".join(["%02x"%ord(c) for c in self.s]) + ">"

## A convenient type of literal Strings
class PDFOctalString(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s="".join(["\\%03o"%ord(c) for c in s])
    def __str__(self):
        return "(%s)"%self.s

## PDF REference 3rd edition:: 3.2.4 Name Objects
class PDFName(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s
    def __str__(self):
        return "/%s"%self.s

## PDF REference 3rd edition:: 3.2.5 Array Objects
class PDFArray(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        assert type(s) == type([])
        self.s=s
    def append(self,o):
        self.s.append(o)
        return self
    def __str__(self):
        return "[%s]"%(" ".join([ o.__str__() for o in self.s]))

## PDF REference 3rd edition:: 3.2.6 Dictionary Objects
class PDFDict(PDFObject):
    def __init__(self, d={}):
        PDFObject.__init__(self)
        self.dict = {}
        for k in d:
            self.dict[k]=d[k]

    def __iter__(self):
        for k in self.dict.keys():
            yield k

    def __iterkeys__(self):
        for k in self.dict.keys():
            yield k

    def __getitem__(self, key):
        return self.dict[key]
        
    def add(self,name,obj):
        self.dict[name] = obj

    def get(self,name):
        if name in self.dict.keys():
            return self.dict[name]
        else:
            return None

    def __str__(self):
        s="<<"
        for name in self.dict:
            s+="%s %s "%(PDFName(name),self.dict[name])
        s+=">>"
        return s

## PDF REference 3rd edition:: 3.2.7 Stream Objects
class PDFStream(PDFDict):
    def __init__(self,d={},stream=""):
        PDFDict.__init__(self,d)
        self.stream=stream
        self.filtered=self.stream
        self.add('Length', len(stream))
        self.filters = []

    def appendFilter(self, filter):
        self.filters.append(filter)
        self._applyFilters() #yeah every time .. so what!

    def _applyFilters(self):
        self.filtered = self.stream
        for f in self.filters:
                self.filtered = f.encode(self.filtered)
        if len(self.filters)>0:
            self.add('Length', len(self.filtered))
            self.add('Filter', PDFArray([f.name for f in self.filters]))
        #Add Filter parameters ?
    def __str__(self):
        self._applyFilters() #yeah every time .. so what!
        s=""
        s+=PDFDict.__str__(self)
        s+="\nstream\n"
        s+=self.filtered
        s+="\nendstream"
        return s

## PDF REference 3rd edition:: 3.2.8 Null Object
class PDFNull(PDFObject):
    def __init__(self):
        PDFObject.__init__(self)

    def __str__(self):
        return "null"


## PDF REference 3rd edition:: 3.2.9 Indirect Objects
class UnResolved(PDFObject):
    def __init__(self,n,v):
        PDFObject.__init__(self)
        self.n=n
        self.v=v
    def __str__(self):
        return "UNRESOLVED(%d %d)"%(self.n,self.v)
class PDFRef(PDFObject):
    def __init__(self,obj):
        PDFObject.__init__(self)
        self.obj=[obj]
    def __str__(self):
        if len(self.obj)==0:
            return "null"
        return "%d %d R"%(self.obj[0].n,self.obj[0].v)

## PDF REference 3rd edition:: 3.3 Filters
## Example Filter...
class FlateDecode:
    name = PDFName('FlateDecode')
    def __init__(self):
        pass
    def encode(self,stream):
        return zlib.compress(stream)
    def decode(self,stream):
        return zlib.decompress(stream)

## PDF REference 3rd edition:: 3.4 File Structure
## Simplest file structure...
class PDFDoc():
    def __init__(self,obfuscate=0):
        self.objs=[]
        self.info=None
        self.root=None
    def setRoot(self,root):
        self.root=root
    def setInfo(self,info):
        self.info=info
    def _add(self,obj):
        if obj.v!=None or obj.n!=None:
            raise Exception("Already added!!!")
        obj.v=0
        obj.n=1+len(self.objs)
        self.objs.append(obj)
    def add(self,obj):
        if type(obj) != type([]):
            self._add(obj);        
        else:
            for o in obj:  
                self._add(o)
    def _header(self):
        return "%PDF-1.5\n%\xE7\xF3\xCF\xD3\n"
    def __str__(self):
        doc1 = self._header()
        xref = {}
        for obj in self.objs:
            xref[obj.n] = len(doc1)
            doc1+="%d %d obj\n"%(obj.n,obj.v)
            doc1+=obj.__str__()
            doc1+="\nendobj\n" 
        posxref=len(doc1)
        doc1+="xref\n"
        doc1+="0 %d\n"%(len(self.objs)+1)
        doc1+="0000000000 65535 f \n"
        for xr in xref.keys():
            doc1+= "%010d %05d n \n"%(xref[xr],0)
        doc1+="trailer\n"
        trailer =  PDFDict()
        trailer.add("Size",len(self.objs)+1)
        if self.root == None:
            raise Exception("Root not set!")
        trailer.add("Root",PDFRef(self.root))
        if self.info:
            trailer.add("Info",PDFRef(self.info))
        doc1+=trailer.__str__()
        doc1+="\nstartxref\n%d\n"%posxref
        doc1+="%%EOF"
        return doc1
