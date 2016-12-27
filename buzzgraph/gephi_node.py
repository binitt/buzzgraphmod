
class GephiNode:
    id=0
    label=""
    timeset=""
    modularity_class=0
 
    key=""
    freq=1
    HEADER="id,label,timeset,pos,freq\n"
 
    def __init__(self, label, modularity_class, id):
        self.label = label
        self.modularity_class = modularity_class
        self.id = id
         
        self.key = label.lower()

    def get_csv(self):
        return("%d,%s,%s,%d,%d\n"%(self.id, self.label, 
          self.timeset, self.modularity_class, self.freq))



