import sys, traceback
import nltk
import langdetect
import re
import xlrd
from operator import attrgetter
from buzzgraph.pollution import Pollution
from buzzgraph.configs import Configs
from langdetect.lang_detect_exception import LangDetectException

class Word:
    word = ""
    freq = 1

    key=""
    HEADER="Word,Frequency"

    def __init__(self, word):
        self.word = word
        self.key = word.lower()

    def get_csv(self):
        return "{0},{1}".format(self.word, self.freq)

class WordCloud:
    startFrom = 0
    words = {}

    def process_file(self):
        if (Configs.input_ignore_header): self.startFrom = 1
        if (re.compile(r'(?i).xlsx?$').search(Configs.input_file) == None):
            self.process_file_csv()
        else:
            self.process_file_excel()

    def process_file_excel(self):
        print("Processing excel file:", Configs.input_file)

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
                lang = Pollution.is_eng(line)
                if (not lang[0]):
                    noneng += 1
                    if (lang[1]):
                        print("Error getting lang for linenum: {0}, "
                            "line: {1}".format(linenum, line))

                    continue
                self.process_line(line)
                valid += 1
            except:
                print("While processing linenum: {0}".format(
                  linenum))
                errors += 1
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print("*** Got Exception:", file=sys.stderr)
                print(traceback.format_exc(), file=sys.stderr)
        
        self.select_top_n()
        print("Processed lines: {0}, valid: {1}, "
            "non-utf8: {2}, non-english: {3}, errors: {4}".format(
            linenum, valid, nonUtf8, noneng, errors))


    def process_file_csv(self):
        print("Processing csv file:", Configs.input_file)
        linenum = 0
        nonUtf8 = 0
        valid = 0
        noneng = 0
        errors = 0
        with open(Configs.input_file, "rb") as f:
            for lineb in f:
                linenum += 1
                if (linenum < self.startFrom): next
                line = ""
                if (linenum % 1000 == 0): print("\rProcessing line:", 
                    linenum, end="")
                try:
                    if (not Pollution.is_utf8(lineb)):
                        nonUtf8 += 1
                        continue

                    line = lineb.decode("utf-8")

                    # we get (isEng, isError)
                    lang = Pollution.is_eng(line)
                    if (not lang[0]):
                        noneng += 1
                        if (lang[1]):
                            print("Error getting lang for linenum: {0}, "
                                "line: {1}".format(linenum, line))
    
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
        lineset = set()
        for token in tokens:
            word = Word(token)
            if (word.key in lineset):
                continue
            lineset.add(word.key)
            if (word.key in self.words):
                word = self.words[word.key]
                word.freq += 1
            else:
                self.words[word.key] = word

    def select_top_n(self):
        self.words = sorted(self.words.values(), key=attrgetter('freq'),
          reverse=True)[:Configs.topN]

    def write_csv(self):
        print("Writing nodes to", Configs.wordcloud_file)
        with open(Configs.wordcloud_file, "w", encoding='utf8') as f:
            f.write(Word.HEADER + "\n")
            for w in self.words:
                f.write(w.get_csv() + "\n")

def main():
    try:
        cloud = WordCloud()
        cloud.process_file()
        cloud.write_csv()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** Top Level Exception:", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
