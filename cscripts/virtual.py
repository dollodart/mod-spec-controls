class DummySer:
    def readline(self,*args):
        return ('10,'*10).encode('ascii')
    def readlines(self,*args):
        return [self.readline()]
    def write(self,*args):
        pass

