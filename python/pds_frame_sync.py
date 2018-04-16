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

SEARCH = 1
COPY = 2

class pds_frame_sync(gr.sync_block):
    """
    Expects Correlate Access Code - Tag block upstream.
    Tag indicates the last bit of the Biphase-L DECODED frame sync value
    Operates on unpacked byte stream.
    Operates on Biphase-L DECODED Stream.

    Logic:
     Detects a frame_sync tag.
     pulls out the following 576 bits (frame minus frame sync bits)
     Packs unpacked bit vector into bytes
     Emits a PMT/PDU Message of decoded frame
     Emitted Frame should contain three data packets, each with a 12 bit 'word sync' starting each packet
    """
    def __init__(self, tag_name="pds_sync"):
        gr.sync_block.__init__(self,
            name="pds_frame_sync",
            in_sig=[numpy.int8],
            out_sig=None)

        self.tag_name = tag_name
        self.message_port_register_out(pmt.intern("out"))
        self.len_encoded_msg = 576
        self.pds_msg = []
        self.msg_packed = []
        self.msg_count = 0
        self.state = SEARCH

    def pack_bytes(self):
        self.msg_count += 1
        a = [int("".join(map(str, self.pds_msg[i:i+8])), 2) for i in range(0, len(self.pds_msg), 8)]
        self.msg_packed = bytearray(a)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        num_input_items = len(in0)
        return_value = num_input_items
        nread = self.nitems_read(0)

        if self.state == SEARCH:
            tags = self.get_tags_in_window(0, 0, num_input_items)
            if len(tags) > 0:
                #print "Tags Detected"
                for t in tags:
                    t_str = pmt.symbol_to_string(t.key)
                    if t_str == self.tag_name:
                        #print "PDS Frame Sync"
                        del self.pds_msg[:]#empty encoded msg buffer
                        del self.msg_packed[:]#empty packed msg buffer
                        cur_idx = t.offset - nread
                        self.pds_msg.extend(in0[cur_idx:])
                        self.state = COPY

        elif self.state == COPY:
            cur_msg_len = len(self.pds_msg)
            if (cur_msg_len + num_input_items) < self.len_encoded_msg:  #doesn't exceed max frame length
                self.pds_msg.extend(in0)
            else:
                num_remain = self.len_encoded_msg - cur_msg_len
                self.pds_msg.extend(in0[0:num_remain])
                return_value = num_remain
                self.pack_bytes()
                msg_str = "[{:d}] {:s}\n".format(self.msg_count, binascii.hexlify(self.msg_packed))
                pmt_msg = pmt.cons(pmt.PMT_NIL, pmt.intern(msg_str))

                print msg_str
                self.message_port_pub(pmt.intern('out'), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(self.msg_packed),self.msg_packed)))
                self.state = SEARCH #RESET to SEARCH State

        return return_value
