import sys, traceback
import re
import xlrd
from buzzgraph import *
from operator import attrgetter
from buzzgraph.gephi_node import GephiNode
from buzzgraph.gephi_edge import GephiEdge
from buzzgraph.configs import Configs
from buzzgraph.utils import *


class Pollution:
    """Pollution data processing"""

    # select topic words POS
    POS = { 
      "NNP":1, "NNS":2, "NNPS":3, "NN":4, 
      #"VB":5, "VBD":6, "VBG":7, "VBN":8, "VBP":9, "VBZ":10,
      "JJ":11, "JJR":12, "JJS":13, 
      #"CD":14 
    }

    # remove these words
    Remove = { "@", "be" }

    nodeId = 0
    edgeId = 0
    nodes = {}
    edges = {}
    keywords = set()

    startFrom = 0

    def __init__(self):
        pass

    def process_file(self):
        """Build set of keywords"""
        self.load_keywords()
        if (Configs.input_ignore_header): self.startFrom = 1
        if (re.compile(r'(?i).xlsx?$').search(Configs.input_file) == None):
            self.process_file_csv()
        else:
            self.process_file_excel()

    def load_keywords(self):
        if (Configs.keywords_csv == None):
            log.info("Keywords file not found, disabling feature")
            self.keywords = None
            return;

        log.info("Processing keywords file: %s", Configs.keywords_csv)
        linenum = 0
        with open(Configs.keywords_csv, "rb") as f:
            for lineb in f:
                linenum += 1
                if (linenum == 1): continue
                line = lineb.decode("utf-8")
                word = line.split(",")[0]
                kw = GephiNode.gen_key(word)
                self.keywords.add(kw)
        log.info("Loaded %d keywords", len(self.keywords))
        

    def process_file_excel(self):
        log.info("Processing excel file: %s", Configs.input_file)

        linenum = 0
        nonUtf8 = 0
        valid = 0
        noneng = 0
        errors = 0
        book = xlrd.open_workbook(Configs.input_file)
        sh = book.sheet_by_name(Configs.input_sheet)
        col = sh.col(Configs.input_column)

        for cell in col[self.startFrom:]:
            line = cell.value
            linenum += 1

            if (linenum % 1000 == 0): print("\rProcessing line:", 
                linenum, end="")
            try:
                # we get (isEng, isError)
                lang = is_eng(line)
                if (not lang[0]):
                    noneng += 1
                    if (lang[1]):
                        log.warning("Error getting lang for linenum: {0}, "
                            "line: {1}".format(linenum, line))

                    continue
                self.process_line(line)
                valid += 1
            except:
                log.error("While processing linenum: {0}, line: {1}".format(
                  linenum, line))
                errors += 1
                exc_type, exc_value, exc_traceback = sys.exc_info()
                log.error("*** Got Exception:")
                log.error(traceback.format_exc())
        
        self.select_top_n()
        log.info("Processed lines: {0}, valid: {1}, "
            "non-utf8: {2}, non-english: {3}, errors: {4}".format(
            linenum, valid, nonUtf8, noneng, errors))



    def process_file_csv(self):
        log.info("Processing csv file: %s", Configs.input_file)
        linenum = 0
        nonUtf8 = 0
        valid = 0
        noneng = 0
        errors = 0
        #with open(Configs.input_file, encoding="Latin-1") as f:
        with open(Configs.input_file, "rb") as f:
            for lineb in f:
                linenum += 1
                if (linenum < self.startFrom): next
                line = ""
                if (linenum % 1000 == 0): print("\rProcessing line:", 
                    linenum, end="")
                try:
                    if (not is_utf8(lineb)):
                        nonUtf8 += 1
                        continue
                    line = lineb.decode("utf-8")
                    if (not is_eng(line)):
                        noneng += 1
                        continue
                    self.process_line(line)
                    valid += 1
                except:
                    log.error("While processing linenum: {0}, line: {1}".format(
                      linenum, line))
                    errors += 1
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    log.error("*** Got Exception:")
                    log.error(traceback.format_exc())

        self.select_top_n()
        log.info("Processed lines: {0}, valid: {1}, "
            "non-utf8: {2}, non-english: {3}, errors: {4}".format(
            linenum, valid, nonUtf8, noneng, errors))

    def process_line(self, line):
        tokens = tokenize(line)
        tagged = pos_tag(tokens)

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
        # Ignore if keyword is not present in line
        if self.keywords != None and (
            not any (item for item in narr if item.label in self.keywords)):
            return;
        for i in range(1, len(narr)):
            nfrom = narr[i-1]
            nto = narr[i]
            if (nfrom.id == nto.id):
                continue
            """Ignore this edge if none of the words are in keywords
            if (not nto.label in self.keywords  and 
                not nfrom.label in self.keywords):
                continue;
            """

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
        log.info("Before selection, nodes:{0}, edges: {1}".format(
          len(self.nodes), len(self.edges)))
        selnodes = sorted(self.nodes.values(), key=attrgetter('freq'),
          reverse=True)[:Configs.topN]
        selnodesD = { item.id for item in selnodes }
        self.edges = { k:v for k,v in self.edges.items() if 
          (v.source in selnodesD) and (v.target in selnodesD) }
        # regenerate selnodesD again to filter out disconnected nodes
        selnodesD = set()
        for k,v in self.edges.items():
            selnodesD.add(v.source)
            selnodesD.add(v.target)
        self.nodes = { k:v for k,v in self.nodes.items() if v.id in selnodesD }
        log.info("After selection, nodes:{0}, edges: {1}".format(
          len(self.nodes), len(self.edges)))

    def write_node_csv(self):
        log.info("Writing nodes to %s", Configs.nodes_file)
        sortednodes = sorted(self.nodes.values(), key=attrgetter('id'))
        with open(Configs.nodes_file, "w", encoding='utf8') as f:
            f.write(GephiNode.HEADER)
            for sn in sortednodes:
                f.write(sn.get_csv())
                

    def write_edge_csv(self):
        log.info("Writing edges to %s", Configs.edges_file)
        sortededges = sorted(self.edges.values(), key=attrgetter('id'))
        with open(Configs.edges_file, "w", encoding='utf8') as f:
            f.write(GephiEdge.HEADER)
            for se in sortededges:
                f.write(se.get_csv())



def main():
    try:
        print("=======Starting Pollution===========")
        pollution = Pollution()
        pollution.process_file()
        pollution.write_node_csv()
        pollution.write_edge_csv()
        print("\nCompleted Execution")
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        log.error("*** Top Level Exception:")
        log.error(traceback.format_exc())
