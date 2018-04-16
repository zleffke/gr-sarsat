#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2018 zleffke
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import numpy
import pmt
import binascii
from gnuradio import gr

class sarp_msg_extract(gr.basic_block):
    """
    Expects PDU from PDS Frame Sync Block.
    Each PDS Frame should contain 3 SARP Messages.
    Each SARP Message should begin with 0xD60.

    Extracts each SARP Message, emits on output port.
    'valid' output port:
    -If sync word of SARP message matches 0xD60.
    -May still contain bit errors, check BCH codes.

    'invalid' output port:
    -if sync word of SARP message does not match 0xD60.
    -Beacon data may still be valid, check BCH codes.
    """
    def __init__(self):
        gr.basic_block.__init__(self,
            name="sarp_msg_extract",
            in_sig=None,
            out_sig=None)

        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)
        self.message_port_register_out(pmt.intern('valid'))
        self.message_port_register_out(pmt.intern('invalid'))

    def handle_msg(self, msg_pmt):
        pds_msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(pds_msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
            return

        buff = bytearray(pmt.u8vector_elements(pds_msg))
        #print len(buff), binascii.hexlify(buff)
        sarp_msg_1 = bytearray(buff[0:24])
        sarp_msg_2 = bytearray(buff[24:48])
        sarp_msg_3 = bytearray(buff[48:])

        #print len(sarp_msg_1), binascii.hexlify(sarp_msg_1)
        #print len(sarp_msg_2), binascii.hexlify(sarp_msg_2)
        #print len(sarp_msg_3), binascii.hexlify(sarp_msg_3)

        out_port = 'invalid'
        if ((sarp_msg_1[0] == 0xD6) and ((sarp_msg_1[1] & 0xF0) == 0x00)): out_port = 'valid'
        self.message_port_pub(pmt.intern(out_port), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(sarp_msg_1),sarp_msg_1)))

        out_port = 'invalid'
        if ((sarp_msg_2[0] == 0xD6) and ((sarp_msg_2[1] & 0xF0) == 0x00)): out_port = 'valid'
        self.message_port_pub(pmt.intern(out_port), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(sarp_msg_2),sarp_msg_2)))

        out_port = 'invalid'
        if ((sarp_msg_3[0] == 0xD6) and ((sarp_msg_3[1] & 0xF0) == 0x00)): out_port = 'valid'
        self.message_port_pub(pmt.intern(out_port), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(sarp_msg_3),sarp_msg_3)))
