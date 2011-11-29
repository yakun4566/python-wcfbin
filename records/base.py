import struct
import logging

from datatypes import *

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Record(object):
    records = dict()

    @classmethod
    def add_records(cls, records):
        for r in records:
            Record.records[r.type] = r

    def __init__(self, type=None):
        if type:
            self.type = type

    def to_bytes(self):
        """
        >>> Record(0xff).to_bytes()
        '\\xff'
        """
        return struct.pack('<B', self.type)


    @classmethod
    def parse(cls, fp):
        if cls != Record:
            return cls()
        root = []
        records = root
        parents = []
        last_el = None
        type = True
        while type:
            type = fp.read(1)
            if type:
                type = struct.unpack('<B', type)[0]
                if type in Record.records:
                    log.debug('%s found' % Record.records[type].__name__)
                    obj = Record.records[type].parse(fp)
                    if isinstance(obj, EndElementRecord):
                        if len(parents) > 0:
                            records = parents.pop()
                        #records.append(obj)
                    elif isinstance(obj, Element):
                        last_el = obj
                        records.append(obj)
                        parents.append(records)
                        obj.childs = []
                        records = obj.childs
                    elif isinstance(obj, Attribute) and last_el:
                        last_el.attributes.append(obj)
                    else:
                        records.append(obj)
                    log.debug('Value: %s' % str(obj))
                elif type-1 in Record.records:
                    log.debug('%s with end element found (0x%x)' %
                            (Record.records[type-1].__name__, type))
                    records.append(Record.records[type-1].parse(fp))
                    #records.append(EndElementRecord())
                    last_el = None
                    if len(parents) > 0:
                        records = parents.pop()
                else:
                    log.warn('type 0x%x not found' % type)

        return root

class Element(Record):
    pass

class Attribute(Record):
    pass

class Text(Record):
    pass

class EndElementRecord(Element):
    type = 0x01

class CommentRecord(Record):
    type = 0x02
    
    def __init__(self, comment, *args, **kwargs):
        self.comment = comment

    def to_bytes(self):
        """
        >>> CommentRecord('test').to_bytes()
        '\\x02\\x04test'
        """
        string = Utf8String(self.comment)

        return (super(CommentRecord, self).to_bytes() + 
                string.to_bytes())

    def __str__(self):
        """
        >>> str(CommentRecord('test'))
        '<!-- test -->'
        """
        return '<!-- %s -->' % self.comment

    @classmethod
    def parse(cls, fp):
        data = Utf8String.parse(fp).value
        return cls(data)

class ArrayRecord(Record):
    type = 0x03

    datatypes = {
            0xB5 : ('BoolTextWithEndElement', 1, '?'),
            0x8B : ('Int16TextWithEndElement', 2, 'h'),
            0x8D : ('Int32TextWithEndElement', 4, 'i'),
            0x8F : ('Int64TextWithEndElement', 8, 'q'),
            0x91 : ('FloatTextWithEndElement', 4, 'f'),
            0x93 : ('DoubleTextWithEndElement', 8, 'd'),
            0x95 : ('DecimalTextWithEndElement', 16, ''),
            0x97 : ('DateTimeTextWithEndElement', 8, ''),
            0xAF : ('TimeSpanTextWithEndElement', 8, ''),
            0xB1 : ('UuidTextWithEndElement', 16, ''),
            }

    def __init__(self, element, recordtype, data):
        self.element = element
        self.recordtype = recordtype
        self.count = len(data)
        self.data = data

    def to_bytes(self):
        """
        >>> from records.elements import ShortElementRecord
        >>> ArrayRecord(ShortElementRecord('item'), 0x8D, ['\\x01\\x00\\x00\\x00', '\\x02\\x00\\x00\\x00', '\\x03\\x00\\x00\\x00']).to_bytes()
        '\\x03@\\x04item\\x01\\x8d\\x03\\x01\\x00\\x00\\x00\\x02\\x00\\x00\\x00\\x03\\x00\\x00\\x00'
        """
        bytes = super(ArrayRecord, self).to_bytes()
        bytes += self.element.to_bytes()
        bytes += EndElementRecord().to_bytes()
        bytes += struct.pack('<B', self.recordtype)[0]
        bytes += MultiByteInt31(self.count).to_bytes()
        for data in self.data:
            if type(data) == str:
                bytes += data
            else:
                bytes += data.to_bytes()

        return bytes

    @classmethod
    def parse(cls, fp):
        element = struct.unpack('<B', fp.read(1))[0]
        element = __records__[element].parse(fp)
        recordtype = struct.unpack('<B', fp.read(1))[0]
        count = MultiByteInt31.parse(fp).value
        data = []
        for i in range(count):
            data.append(__records__[recordtype-1].parse(fp))
        return cls(element, recordtype, data)

    def __str__(self):
        """
        >>> from records.elements import ShortElementRecord
        >>> from records.text import Int32TextRecord
        >>> str(ArrayRecord(ShortElementRecord('item'), 0x8D, [Int32TextRecord(1),Int32TextRecord(2),Int32TextRecord(3)]))
        '<item >1</item><item >2</item><item >3</item>'
        """
        string = ''
        for data in self.data:
            string += str(self.element)
            string += str(data)
            string += '</%s>' % self.element.name

        return string

Record.add_records((EndElementRecord,
        CommentRecord,
        ArrayRecord,))