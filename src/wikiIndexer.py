import xml.sax.handler
from textProcessing import processText, processTitle
from fileHandling import writeIntoFile, mergeFiles
from collections import defaultdict
import sys
import timeit
import pdb
from config import *

index  = defaultdict(list)
count  = 0
countFile = 0
dict_Id = {}
offset = 0

OUTPUT_FOLDER = ""

class WikiHandler(xml.sax.handler.ContentHandler):
    flag = 0
    def createIndex(self,title,text,infoBox,category,externalLink):
        global index,dict_id,countFile,offset,count,OUTPUT_FOLDER
        vocabularyList = list(set(title.keys() + text.keys() + infoBox.keys() + externalLink.keys()))
        t,b,i,c,e = float(len(title)),float(len(text)),float(len(infoBox)),float(len(category)),float(len(externalLink))
        for key in vocabularyList:
            string = str(count)+' '
            for (contentType, contentLen) in [(title,t),(text,b),(infoBox,i),(category,c),(externalLink,e)]:
                try:
                    if SCORE_TYPE == "freq":
                        string += str(int(contentType[key])) + ' '
                    elif SCORE_TYPE == "freq_ratio":
                        string += str(round(contentType[key]/contentLen,3))+' '
                    else:
                        print("ERROR: Unknown scoring type")
                except ZeroDivisionError:
                    string += str(SCORE_TYPE_TYPE(0)) + ' '
            index[key].append(string)
            
        count+=1
        if count % WRITE_PAGES_TO_FILE == 0:
            print(f"Pages Processed: {count} | Writing the partial index to disk ....")
            offset = writeIntoFile(OUTPUT_FOLDER, index, dict_Id, countFile, offset)
            index = defaultdict(list)
            dict_Id = {}
            countFile += 1
        
    def __init__(self):
        self.inTitle, self.inId, self.inText = 0,0,0
    
    def startElement(self, name, attributes):
        if name == "id" and WikiHandler.flag == 0:
            self.bufferId = ""
            self.inId = 1
            WikiHandler.flag = 1
        elif name == "title":
            self.bufferTitle = ""
            self.inTitle = 1
        else:
            self.bufferText = ""
            self.inText = 1
        
    def characters(self, data):
        global count, dict_Id
        if self.inId and WikiHandler.flag == 1:
            self.bufferId += data
        elif self.inTitle:
            self.bufferTitle += data.encode('utf-8')
        elif self.inText:
            self.bufferText += data
    
    def endElement(self, name):
        if name == "title":
            WikiHandler.titleWords = processTitle(self.bufferTitle)
            self.inTitle = 0
        elif name == "text":
            WikiHandler.textWords, WikiHandler.infoBoxWords, WikiHandler.categoryWords, WikiHandler.externalLinkWords = processText(self.bufferText)
            WikiHandler.createIndex(self, WikiHandler.titleWords, WikiHandler.textWords, WikiHandler.infoBoxWords, WikiHandler.categoryWords, WikiHandler.externalLinkWords)
            self.inText = 0
        elif name == "id":
            self.inId = 0
        elif name == "page":
            WikiHandler.flag = 0
    
def main():
    global offset, countFile, OUTPUT_FOLDER
    if len(sys.argv) != 3:
        print("Usage:: python wikihandler.py sample.xml ./output")
        sys.exit(0)
    OUTPUT_FOLDER = sys.argv[2]

    parser = xml.sax.make_parser()
    handler = WikiHandler()
    parser.setContentHandler(handler)
    parser.parse(sys.argv[1])
    with open(OUTPUT_FOLDER + '/numberOfFiles.txt','wb') as f:
        f.write(str(count))
    
    offset = writeIntoFile(OUTPUT_FOLDER, index, dict_Id, countFile, offset)
    countFile += 1
    mergeFiles(OUTPUT_FOLDER, countFile)

    titleOffset = []
    with open(OUTPUT_FOLDER + './title.txt','rb') as f:
        titleOffset.append('0')
        for line in f:
            titleOffset.append(str(int(titleOffset[-1]) + len(line)))
            for line in f:
                titleOffset.append(str(int(titleOffset[-1]) + len(line)))
            titleOffset = titleOffset[:-1]
        
        with open(OUTPUT_FOLDER + './titleoffset.txt','wb') as f:
            f.write('\n'.join(titleOffset))

if __name__ == "__main__":
    start = timeit.default_timer()
    main()
    stop = timeit.default_timer()
    print("Query Time",stop-start)



