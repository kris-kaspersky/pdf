import StringIO
from opaflib import *
####
#### XrefStm
####
#Logging facility
import logging
#logging.basicConfig(filename='opaf.log',level=logging.DEBUG)
logger = logging.getLogger("OPAFXref")


def decodeAnyXref(xml_pdf,xref):
    '''
        #TODO! Hidden objects not referenced!
        Decode the passed xref xml. It may be normal xref or a XrefStm steream
        This return a tuple like this :
            (referenced, compressed, deleted, prev )
        where:
            referenced  =  { REF  ->  pos }      
                a reference to byte position     
            compressed  =  { REF  -> ( REFC, I) }  
                so called compressed objects are at index I 
                inside the ObjStm with named REFC 
            deleted     =  [ REF, REF ..] 
                list of deleted object references    
            prev        =  byte pos of the prev xref if any
    '''
    if xref.tag == "indirect_object_stream":
        return decodeXrefStm(xml_pdf,xref)
    else:
        assert xref.tag == "xref", "Type must by xref"
        return decodeXref(xml_pdf,xref)
         
def decodeXrefStm(xml_pdf,xrefstm):
    '''
        This will decode a XrefStm stream.
    '''
    def unpack(s,nbytes,default=1):
        #Fields requiring more than one byte are stored with the high-order byte first.
        assert len(s) == nbytes
        if nbytes == 0:
            return default
        co = 0
        for i in range(0,nbytes):
            co=ord(s[i])+(co<<8)
        return co

    assert xrefstm.tag == "indirect_object_stream", "Type must by indirect_object_stream (And it is %s)"%xrefstm.tag
    assert payload(getTypeOfStream(xrefstm)) == "XRef", "Must be a XrefStream but it is a %s"%payload(getTypeOfStream(xref))
    assert expand(xrefstm), "Something went wrong when decompressing the Main XrefStream"
    #Get trailer dictionary and data
    xrefstm_dict = xmlToPy(xrefstm[0])
    xrefstm_data = payload(xrefstm[1])

    #safety checks
    assert all([ x in xrefstm_dict for x in [ 'Type', 'Size', 'W' ]]), 'Type Size and W are required in Xref Streams'
    assert type(xrefstm_dict['W']) == type([]) and len(xrefstm_dict['W']) >= 3 , "W array must be at least of length 3"
    assert len(xrefstm_data) % sum(xrefstm_dict['W']) == 0 , "XRef stream data should vi a number of %s bytes"%xrefstm['W']

    #unpack the numbers from the stream
    nums = []
    xrefstm_io = StringIO.StringIO(xrefstm_data)
    for i in range(0, len(xrefstm_data), sum(xrefstm_dict['W'])):
        nums.append(tuple([unpack(xrefstm_io.read(x),x) for x in xrefstm_dict['W']]))
    #Check if we got any erased object
    if any([t[0] == 0 for t in nums]):
        logger.info("There are erased objects")

    #Get Index array or its default
    index = xrefstm_dict.get("Index",[0,xrefstm_dict['Size']])
    assert len(index)%2 == 0, "Index should be an array of pairs"     
    assert  all([(index[i]+index[i+1])<index[i+2] for i in range(0,len(index)-2,2)]), "The array shall be sorted in ascending order by object number. Subsections cannot overlap; an object number may have at most one entry in a section.Index: %s"%index
    
    #Calculate xref subsections
    subsections = [(index[i],index[i+1]) for i in range(0,len(index),2)]
    assert sum([size for n,size in subsections]) == len(nums), "Different number of subsections and values in stream"


    #assign object numbers to entries...
    entries = {}
    for n, size in subsections:
        for i in range(n, n+size):
            entries[i] = nums.pop(0)
    logger.info("Got %d entries in %d subsections of the XrefStm %s"%(len(entries),len(subsections),payload(xrefstm)))  

    #Check free linked list
    deleted = []
    t,n,g = entries[n]
    while n != 0 and t == 0:
        assert entries[n][2] != n, "Loop in free list!"
        t,n,g = entries[n]
        if n!=0:
            deleted.append(repr(n,g-1))
    assert len(deleted) == sum([t==0  and n!=0 and 1 or 0 for t,n,g in entries.values()]), "Something wrong in the free list"
    logger.info("Got %d free entries XrefStm %s"%(len(deleted),payload(xrefstm)))  
    
    
    #Check compresed object references
    compressed = {}
    referenced = {}
    for n in entries.keys():
        ty,a,b = entries[n]
        if ty == 2:
            cobj,i = a, b
            ##-The type of this entry, which shall be 2. Type 2 entries define
            #  compressed objects.
            ##-The object number of the object stream in which this object is
            #  stored. (The generation number of the object stream shall be
            #  implicitly 0.)
            ##-The index of this object within the object stream.
            ref = repr((n,0))
            compressed[ref] = ( (cobj,0), i)
        elif ty == 1:
            pos, g = a, b
            ##-The type of this entry, which shall be 1. Type 1 entries define
            #  objects that are in use but are not compressed (corresponding
            #  to n entries in a cross-reference table).
            ##-The byte offset of the object, starting from the beginning of the
            #  file.
            ##-The generation number of the object. Default value: 0.
            referenced[repr((n,g))] = pos
    logger.info("Got %d compressed entries XrefStm %s"%(len(compressed),payload(xrefstm)))  
    logger.info("Got %d referenced entries XrefStm %s"%(len(referenced),payload(xrefstm)))  
             
    if 'Prev' in xrefstm_dict.keys():
        logger.info("There are chained cross references")
    return referenced, compressed, deleted, xrefstm_dict.get('Prev',None)

def decodeXref(xml_pdf,xref):    
    '''
        This will decode a NORMAL Xref.
        #TODO: this is done by the lexer... move it here?
    '''
    assert xref.tag == "xref", "Type must by xref (And it is %s)"%xref.tag
    
    #get the trailer dictionary
    xref_dict = xmlToPy(xref[0])
    
    referenced, compressed, deleted = {}, {}, []
    subsections = eval(payload(xref)) #safe lazyness because we parse it in the lexer
    for subsection in subsections:
        (start,size), entries = subsection
        assert size == len(entries), "Subsection length should be %d and it is %d"%(size,len(subsection))
        #TODO Check reference order, overlap and freelist
        for i in range(0,len(entries)):
            pos, gen, ty = entries[i]
            ref = repr((start+i,gen))
            if ty == 'f':
                deleted.append(ref)
            elif ty == 'n':
                referenced[ref] = pos
        return referenced, compressed, deleted, xref_dict.get('Prev',None)


def checkXrefTree(xml_pdf):
    '''
        Starting from the main (normal or XrefStm) xref it dive into the
        /Prev and /XrefStm links decoding all cross reference information
        and checking for inconsistensies.
        On return 
                referenced, compressed, deleted 
        TODO: document algorithm, decode hidden, define good checks
    '''
    #check xref net
    #TODO: add hidden objects...
    main_xref = getMainXref(xml_pdf)
    #TODO: Check loops in /Prev link
    xref_table = []
    referenced, compressed, deleted, prev = decodeAnyXref(xml_pdf,main_xref) 
    xref_table.append((referenced, compressed, deleted))
    while prev:
        prev_xref = xml_pdf.xpath('//*[(local-name() = "xref" or local-name()= "indirect_object_stream") and @lexstart="%s"]'%prev)
        assert len(prev_xref)>0, "\Prev xref chain pointing to non existing object"
        referenced, compressed, deleted, prev = decodeAnyXref(xml_pdf,prev_xref[0]) 
        xref_table.append((referenced, compressed, deleted))
    #TODO check referenced, compressed, deleted are consisten to eachother
    referenced, compressed, deleted = {}, {}, []
    for r,c,d in xref_table:
        assert len(set(r.keys()).intersection(set(referenced.keys())) )==0, "Some objects are Xreferenced more than once "
        referenced.update(r)
        compressed.update(c)
        deleted+=d
                
    positions = [x.get('lexstart') for x in  xml_pdf.xpath('/*[starts-with(local-name(),"indirect_object")]')]
    #Check that every crossreferenced object is there
    assert len(set(referenced.values())-set(positions))==0 , "Some objects are not referenced from XREF %s"%repr(set(referenced.values())-set(positions))


