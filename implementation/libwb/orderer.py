#-*- coding:utf-8 -*-

class Multiset(object):
    def __init__(self):
        self.data = {}

    def add(self, obj, num=1):
        self.data.setdefault(obj, 0)
        self.data[obj] += num

    def remove(self, obj, num=1):
        self.data[obj] -= num
        assert self.data[obj] >= 0
        if self.data[obj] == 0:
            del self.data[obj]

    def remove_all(self, obj):
        del self.data[obj]

    def items(self):
        return self.data.items()

    def __len__(self):
        return len(self.data)

    def __contains__(self, obj):
        return obj in self.data

    def __iter__(self):
        return self.data.__iter__()

    def __nonzero__(self):
        return bool(self.data)

class ComputationOrder(object):
    ACTION_COMPUTE = "compute"
    ACTION_FREE = "free"
    # ACTION_ALLOC = "alloc"

    def __init__(self, code, xbits, ybits):
        self.code = code
        self.xbits = tuple(xbits)
        self.ybits = tuple(ybits)

CO = ComputationOrder

class Orderer(object):
    def __init__(self, xbits, ybits, quiet=False):
        self.ybits = ybits
        self.xbits = list(xbits)

        self.quiet = quiet

    def log(self, *args):
        if not self.quiet:
            print "::",
            for arg in args:
                print arg,
            print

    def compile(self):
        self.log("circuit walk")

        visited = set()
        using = {}

        q = []
        for b in self.ybits:
            q.append(b)
            visited.add(b)
        while q:
            b = q.pop()
            for sub in b.args:
                if type(sub) == type(b):
                    if sub not in visited:
                        visited.add(sub)
                        q.append(sub)

                    if sub not in using:
                        using[sub] = Multiset()
                    using[sub].add(b)

        self.log("ordering", len(visited), "nodes")

        order = sorted(visited, key=lambda b: b.id)
        ready = set()
        code = []
        for b in order:
            if b.is_primitive():
                ready.add(b)
                continue

            code.append((CO.ACTION_COMPUTE, b))
            ready.add(b)

            for sub in b.args:
                if type(sub) != type(b):
                    continue
                assert sub in ready
                using[sub].remove_all(b)
                if not using[sub]:
                    code.append((CO.ACTION_FREE, sub))
        code = tuple(code)

        self.log("code size: %d operations" % len(code))

        return ComputationOrder(xbits=self.xbits, ybits=self.ybits, code=code)
