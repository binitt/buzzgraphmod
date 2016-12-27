
class GephiEdge:
    source=0
    target=0
    type="Undirected"
    id=0
    label=""
    timeset=""
    weight=1

    key=""
    HEADER="Source,Target,Type,id,label,timeset,weight\n"

    def __init__(self, source, target, id):
        # make sure source<target
        if (source>target):
            source,target = target,source

        self.source = source
        self.target = target
        self.id = id
        self.weight = 1
        
        self.key = "%d:%d"%(source, target)


    def get_csv(self):
        return("%d,%d,%s,%d,%s,%s,%d\n"%(
            self.source, self.target, self.type, self.id,
            self.label, self.timeset, self.weight))
