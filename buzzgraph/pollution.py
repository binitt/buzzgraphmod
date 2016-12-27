import sys, traceback
import nltk
import langdetect
import re
from operator import attrgetter
from buzzgraph.gephi_node import GephiNode
from buzzgraph.gephi_edge import GephiEdge
from buzzgraph.configs import Configs


class Pollution:
    """Pollution data processing"""

    # select topic words POS
    POS = { 
      "NNP":1, "NNS":2, "NNPS":3, "NN":4, 
      "VB":5, "VBD":6, "VBG":7, "VBN":8, "VBP":9, "VBZ":10,
      "JJ":11, "JJR":12, "JJS":13, 
      #"CD":14 
    }

    # remove these words
    Remove = { "@", "be" }

    nodeId = 0
    edgeId = 0
    nodes = {}
    edges = {}
    topN = 100

    def __init__(self):
        pass

    def process_file(self, filename):
        linenum = 0
        nonUtf8 = 0
        valid = 0
        noneng = 0
        errors = 0
        #with open(filename, encoding="Latin-1") as f:
        with open(filename, "rb") as f:
            for lineb in f:
                linenum += 1
                line = ""
                if (linenum % 1000 == 0): print("\rProcessing line:", 
                    linenum, end="")
                try:
                    if (not self.is_utf8(lineb)):
                        nonUtf8 += 1
                        continue
                    line = lineb.decode("utf-8")
                    if (not self.is_eng(line)):
                        noneng += 1
                        continue
                    self.process_line(line)
                    valid += 1
                except:
                    print("While processing linenum: {0}, line: {1}".format(
                      linenum, line))
                    errors += 1
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    print("*** Got Exception:", file=sys.stderr)
                    print(traceback.format_exc(), file=sys.stderr)

        self.select_top_n()
        print("Processed lines: {0}, valid: {1}, "
            "non-utf8: {2}, non-english: {3}, errors: {4}".format(
            linenum, valid, nonUtf8, noneng, errors))

    def process_line(self, line):
        line = line.strip("\"' \t\n")
        # remove urls
        line = re.sub(r"\bhttps?:\S*", "__LINK__", line)
        line = re.sub(r"\b@\w+", "__AT__", line)

        tokens = nltk.word_tokenize(line)
        tagged = nltk.pos_tag(tokens)

        # filling nodes
        topics = [(item[0], self.POS[item[1]]) for item in tagged 
          if item[1] in self.POS and len(item[0]) > 1 and 
          item[0] not in self.Remove]

        narr = []
        for t in topics:
            node = GephiNode(t[0], t[1], self.nodeId)
            if (node.key in self.nodes):
                node = self.nodes[node.key]
                node.freq += 1
            else:
                self.nodeId += 1
                self.nodes[node.key] = node
            narr.append(node)
        
        # filling edges
        #self.fill_edges_all2all(narr);
        self.fill_edges_nearby(narr);


    def fill_edges_nearby(self, narr):
        for i in range(1, len(narr)):
            nfrom = narr[i-1]
            nto = narr[i]
            if (nfrom.id == nto.id):
                continue
            edge = GephiEdge(nfrom.id, nto.id, self.edgeId)
            if (edge.key in self.edges):
                edge = self.edges[edge.key]
                edge.weight += 1
            else:
                self.edges[edge.key] = edge
                self.edgeId += 1


    def fill_edges_all2all(self, narr):
        for i in range(len(narr)):
            nfrom = narr[i]
            for j in range(i + 1, len(narr)):
                nto = narr[j]
                if (nfrom.id == nto.id):
                    continue
                edge = GephiEdge(nfrom.id, nto.id, self.edgeId)
                if (edge.key in self.edges):
                    edge = self.edges[edge.key]
                    edge.weight += 1
                else:
                    self.edges[edge.key] = edge
                    self.edgeId += 1


    def select_top_n(self):
        print("Before selection, nodes:{0}, edges: {1}".format(
          len(self.nodes), len(self.edges)))
        selnodes = sorted(self.nodes.values(), key=attrgetter('freq'),
          reverse=True)[:self.topN]
        selnodesD = { item.id for item in selnodes }
        self.nodes = { k:v for k,v in self.nodes.items() if v.id in selnodesD }
        self.edges = { k:v for k,v in self.edges.items() if 
          (v.source in selnodesD) and (v.target in selnodesD) }
        print("After selection, nodes:{0}, edges: {1}".format(
          len(self.nodes), len(self.edges)))

    def write_node_csv(self, filename):
        sortednodes = sorted(self.nodes.values(), key=attrgetter('id'))
        with open(filename, "w", encoding='utf8') as f:
            f.write(GephiNode.HEADER)
            for sn in sortednodes:
                f.write(sn.get_csv())
                

    def write_edge_csv(self, filename):
        sortededges = sorted(self.edges.values(), key=attrgetter('id'))
        with open(filename, "w", encoding='utf8') as f:
            f.write(GephiEdge.HEADER)
            for se in sortededges:
                f.write(se.get_csv())

    def is_utf8(self, textb):
        valid_utf8 = True
        try:
            textb.decode('utf-8')
        except UnicodeDecodeError:
                valid_utf8 = False
        return valid_utf8

    def is_eng(self, text):
        if (len(text) == 0): raise Exception("Text size: 0")
        return(langdetect.detect(text) == "en")


def main():
    try:
        pollution = Pollution()
        pollution.process_file(Configs.input_csv)
        pollution.write_node_csv(Configs.nodes_file)
        pollution.write_edge_csv(Configs.edges_file)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** Top Level Exception:", file=sys.stderr)
#        traceback.print_exc()
        print(traceback.format_exc(), file=sys.stderr)
