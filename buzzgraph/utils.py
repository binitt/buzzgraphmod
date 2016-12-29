import re
import nltk
import langdetect
from nltk.tokenize import TweetTokenizer
from langdetect.lang_detect_exception import LangDetectException

def is_utf8(textb):
    valid_utf8 = True
    try:
        textb.decode('utf-8')
    except UnicodeDecodeError:
            valid_utf8 = False
    return valid_utf8

def is_eng(text):
    """
    Returns tuple(isEnglish, isError)
    """
    try:
        return(langdetect.detect(text) == "en", False)
    except LangDetectException:
        return (False, True)

def tokenize(line):
    """Split text into tokens
    """
    line = line.strip("\"' \t\n")
    # remove urls
    #line = re.sub(r"\bhttps?:\S*", "__LINK__", line)
    #line = re.sub(r"\b@\w+", "__AT__", line)
    tt = TweetTokenizer()
    tokens = tt.tokenize(line)
    return tokens


def pos_tag(tokens):
    """Apply POS tagging to word list
    """
    tagged = nltk.pos_tag(tokens)
    tag_corrected = list()

    EMOTICON_RE = nltk.tokenize.casual.EMOTICON_RE
    URL_RE = re.compile(nltk.tokenize.casual.URLS, re.X)
    REPLY_RE = re.compile(r"^@\w+")
    
    for (w, tag) in tagged:
        if (nltk.tokenize.casual.EMOTICON_RE.match(w)):
            tag = "__EMOJI__"
        elif (URL_RE.match(w)):
            tag = "__LINK__"
        elif (REPLY_RE.match(w)):
            tag = "__REPLY__"
        
        tag_corrected.append((w, tag))
    return tag_corrected
