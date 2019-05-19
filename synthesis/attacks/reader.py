#-*- coding:utf-8 -*-

import os
from collections import deque

class Reader(object):
    TRACE_FILENAME_FORMAT = "%04d.bin"
    PLAINTEXT_FILENAME_FORMAT = "%04d.pt"
    CIPHERTEXT_FILENAME_FORMAT = "%04d.ct"

    def __init__(self, ntraces, window, step=None,
                       packed=True, reverse=False, dir="./traces"):

        self.packed = packed

        self.pts = []
        self.cts = []
        self.fds = []

        self.trace_bytes = None
        self.ntraces = int(ntraces)
        assert self.ntraces >= 1
        for i in xrange(self.ntraces):
            f_trace = os.path.join(dir, self.TRACE_FILENAME_FORMAT % i)
            f_pt = os.path.join(dir, self.PLAINTEXT_FILENAME_FORMAT % i)
            f_ct = os.path.join(dir, self.CIPHERTEXT_FILENAME_FORMAT % i)

            self.pts.append(open(f_pt, "rb").read())
            self.cts.append(open(f_ct, "rb").read())

            new_size = os.stat(f_trace).st_size
            if self.trace_bytes is None:
                self.trace_bytes = new_size
            assert self.trace_bytes == new_size, "Trace files must have the same size"

            self.fds.append(open(f_trace, "rb"))

        self.reverse = reverse
        if reverse:
            raise NotImplementedError("Not supported yet")

        if step is None:
            step = window
        assert 0 < step <= window

        if self.packed:
            # round up to multiple of 8
            window += (8 - window % 8) % 8
            step += (8 - step % 8) % 8
            self.window_bytes = window // 8
            self.step_bytes = step // 8
        else:
            self.window_bytes = window
            self.step_bytes = step

        self.window_bytes = min(self.window_bytes, self.trace_bytes)
        self.step_bytes = min(self.step_bytes, self.trace_bytes)

        # may be ceil? not accurate!
        self.num_windows = (self.trace_bytes - self.window_bytes + self.step_bytes - 1) // self.step_bytes + 1

        # not sure if working with longs is faster than with arrays
        # or some other structure, may be even makes sense to write C backend

    def __iter__(self):
        self.vectors = deque()
        self.offset = 0
        self.advance(self.window_bytes)
        for v in self.new_vectors:
            self.vectors.append(v)
        yield self.vectors

        while True:
            if self.offset + self.window_bytes >= self.trace_bytes:
                # already covered the whole trace
                return

            self.advance(self.step_bytes)
            for v in self.new_vectors:
                self.vectors.append(v)
                self.vectors.popleft()
            self.offset += self.step_bytes

            yield self.vectors


    def advance(self, num_bytes):
        self.new_vectors = [0] * (num_bytes * 8)
        for fd in self.fds:
            data = fd.read(num_bytes)
            self.process_window(data)
        self.new_vectors = self.new_vectors[:len(data)*8]

    def process_window(self, data):
        vectors = self.new_vectors
        if not self.packed:
            # 1 bit in byte
            for i, b in enumerate(data):
                val = ord(b) & 1
                vectors[i] = (vectors[i] << 1) | val
            assert b in "\x00\x01", "sure not packed?"
        else:
            # 8 bits in byte (packed)
            for i, b in enumerate(data):
                b = ord(b)
                for j in xrange(8):
                    id = (i << 3) | j
                    bit = (b >> (7 - j)) & 1
                    vectors[id] = (vectors[id] << 1) | bit
