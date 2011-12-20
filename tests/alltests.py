#!/usr/bin/env python2
# vim: set ts=4 sw=4 tw=79 fileencoding=utf-8:

from __future__ import absolute_import
import logging
import doctest
import unittest
    
from wcf.records import *

test_bin = (
"56020b0173040b0161065608440a1e0082993a687474703a2f2f646f6373"
"2e6f617369732d6f70656e2e6f72672f77732d73782f77732d7472757374"
"2f3230303531322f5253542f4973737565441aad5db293d4bc0ba547b9dc"
"cb2f140fd0c3442c442aab1401440c1e0082993c687474703a2f2f646377"
"733a35383435312f44617465762f4672616d65776f726b2f52656d6f7465"
"536572766963654d6f64656c2f456e61626c657201560e41057472757374"
"14526571756573745365637572697479546f6b656e0407436f6e74657874"
"982c757569642d34393037636538322d303630372d346263302d62643861"
"2d6531633937663165323862372d32320905747275737430687474703a2f"
"2f646f63732e6f617369732d6f70656e2e6f72672f77732d73782f77732d"
"74727573742f3230303531324105747275737409546f6b656e5479706599"
"41687474703a2f2f646f63732e6f617369732d6f70656e2e6f72672f7773"
"2d73782f77732d736563757265636f6e766572736174696f6e2f32303035"
"31322f736374410574727573740b52657175657374547970659936687474"
"703a2f2f646f63732e6f617369732d6f70656e2e6f72672f77732d73782f"
"77732d74727573742f3230303531322f497373756541057472757374074b"
"657953697a658b0001410574727573740e42696e61727945786368616e67"
"650674aaa60306d402aad8029e364e544c4d5353500001000000b7b218e2"
"0a000a002d00000005000500280000000601b11d0000000f434c57533157"
"45425345525649439f0145010101").decode('hex')

class TransformTest(unittest.TestCase):

    def runTest(self):
        from StringIO import StringIO
        sio = StringIO(test_bin)
        new = dump_records(Record.parse(sio))

        self.assertEqual(test_bin, new)

class Suite(unittest.TestSuite):

    def __init__(self, *args, **kwargs):
        super(Suite, self).__init__(*args, **kwargs)

        self.addTest(doctest.DocTestSuite(base))
        self.addTest(doctest.DocTestSuite(elements))
        self.addTest(doctest.DocTestSuite(attributes))
        self.addTest(doctest.DocTestSuite(text))
        self.addTest(TransformTest())

if __name__ == '__main__':
    unittest.main()