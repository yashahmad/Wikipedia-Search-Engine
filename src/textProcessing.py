import re
from collections import defaultdict

from Stemmer import Stemmer
from nltk.stem import WordNetLemmatizer

from nltk.corpus import stopwords as nltk_stopwords
from config import *
import string

STOPWORDS = Set(nltk_stopwords.words('english'))
URL_STOP_WORDS = Set(["http","https","www","ftp","com","net","org","archives","pdf","html","png","txt","redirect"])
STEMMER = Stemmer('english')
LEMMATIZER = WordNetLemmatizer()
EXTENDED_PUNCTUATIONS = Set(list(string.punctuation)) + ['\n','\t',' '])
INT_DIGITS = Set(["0","1","2","3","4","5","6","7","8","9"])

MAX_WORD_LEN = 10
MIN_WORD_LEN = 3

def isEnglish(s):
    try:
        s.encode(encoding="utf-8").decode("ascii")
    except:
        return False
    else:
        return True

def tokenize(data):
    tokenizedWords = re.findall("\d+[\w]+",data)
    tokenizedWords = [key.encode('utf-8') for key in tokenizedWords]
    return tokenizedWords

def removeNumbersAndPunctuations(listOfWords):
    temp = []
    for w in listOfWords:
        s = ""
        for c in w:
            if c in INT_DIGITS:
                continue
            if c in EXTENDED_PUNCTUATIONS:
                if len(s) and isEnglish(s):
                    temp.append(s)
                s = ""
                continue
            s += c 
        if len(s) and isEnglish(s):
            temp.append(s)
    return temp

def removeStopWords(listOfWords):
    temp = []
    for w in listOfWords:
        if w in STOPWORDS:
            continue
        if w in URL_STOP_WORDS:
            continue
        if len(w) < MIN_WORD_LEN:
            continue
        if len(w) > MAX_WORD_LEN:
            continue
        temp.append(w)
    return temp

def stemmer(listofTokens):
    return [STEMMER.stemWord(key) for key in listofTokens]

def lemmatizer(listofTokens):
    return [LEMMATIZER.lemmatize(key) for key in listofTokens]

def create_word_to_freq_defaultdict(words):
    temp = defaultdict(int)
    for key in words:
        temp[key]+=1
    return temp

def cleanup_list(list_of_words, already_lowercase=False):
    temp = []
    if not in already_lowercase:
        list_of_words = [s.lower() for s in list_of_words]

    temp = removeNumbersAndPunctuations(list_of_words)
    temp = removeStopWords(temp)

    if LEMMATIZER_OR_STEMMER == "stemming":
        temp = stemmer(temp)
    elif LEMMATIZER_OR_STEMMER == "lemmatization":
        temp = lemmatizer(temp)
    else:
        print("ERROR: Unknown type")
    return temp

def cleanup_string(string, already_lowercase=False):
    if not already_lowercase:
        string = string.lower()
    return cleanup_list(tokenize(string), already_lowercase=True)

def findExternalLinks(data):
    links = []
    lines = data.split("==external links==")
    if len(lines) > 1:
        lines = lines[1].split("\n")
        for i in range(len(lines)):
            if '* [' in lines[i] or '*[' in lines[i]:
                list_of_words = lines[i].split(' ')
                links.extend(cleanup_list(list_of_words, already_lowercase=True))
    return create_word_to_freq_defaultdict(links)

def findInfoBoxTextCategory(data):
    info, bodyText, category, links = [], [], [], []
    flagtext = 1
    lines = data.split('\n')
    for i in range(len(lines)):
        if '{{infobox' in lines[i]:
            flag = 0
            temp = lines[i].split('{{infobox')[1:]
            info.extend(temp)
            while True:
                if '{{' in lines[i]:
                    flag += lines[i].count('{{')
                if '}}' in lines[i]:
                    flag -= lines[i].count('}}')
                if flag <= 0:
                    break
                i += 1
                try:
                    info.append(lines[i])
                except:
                    break
        elif flagtext:
            if '[[category' in lines[i] or '==external links==' in lines[i]:
                flagtext = 0
            bodyText.extend(lines[i].split())
        
        else:
            if "[[category" in lines[i]:
                line = data.split("[[category:")
                if len(line)>1:
                    category.extend(line[1:-1])
                    temp = line[-1].split(']]')
                    category.append(temp[0])
        
        category = cleanup_list(category, already_lowercase=True)
        info = cleanup_list(info, already_lowercase=True)
        bodyText = cleanup_list(bodyText, already_lowercase=True)

        info = create_word_to_freq_defaultdict(info)
        bodyText = create_word_to_freq_defaultdict(bodyText)
        category = create_word_to_freq_defaultdict(category)

        return info, bodyText, category
