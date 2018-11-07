import os

def Reader(filename, window=100, step=25, reverse=False):
    f = open(filename)
    sz = os.stat(filename).st_size

    off = 0
    tail = max(0, sz - window)
    if reverse:
        off = tail

    while True:
        f.seek(off)
        data = f.read(window)
        yield off, data

        if reverse:
            # finished
            if off == 0:
                return
            off = max(0, off - step)
        else:
            if off == tail:
                return
            off = min(tail, off + step)
