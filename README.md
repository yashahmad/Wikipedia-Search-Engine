# Wikipedia-Search-Engine
Search Engine project based on performing search over dump data of Wikipedia

---
### Instructions
- Install Python 3.6
- Install the pip dependencied using pip install -r requirements.txt
- Setup the appropriate values in config.py mentioning the kind of values to store in the indexer. These values can have a major impact on the performance of indexing as well as the searching part.
- Increase the value of open files limit in Ubuntu if you are indexing on a large corpus as K-way merge sort requires opening a large number of files and by default, the max number of files that you can open at a time is 1024.
**Instructions:** [https://easyengine.io/tutorials/linux/increase-open-files-limit/](https://easyengine.io/tutorials/linux/increase-open-files-limit/)

### Problem Statement
---
- The mini project involves building a search engine on the Wikipedia Dump Data without using any external index. For this project, we use the dump data of size ~78 GB. The search results return in real time. Multi-word and multi-field search on Wikipedia Corpus is implemented.
- You also need to rank the documents and display only the top 10 most relevant documents.
- Search should take <5 seconds and the index should be ~20% of the dump size.

### Search Engine Specifications
---
**1. Parsing : Read through the raw dump & extract essential words/phrases for indexing & searchhing**
SAX Parser is used to parse the XML without loading the entire corpus in memory. This helps parse the corpus with minimum memory. After parsing the following morphological operations are performed to obtain clean vocabulary.
- Stemming: python library PyStemmer is used.
- Casefolding: Casefolding is easily done.
- Tokenisation: Tokenisation is done using regular expressions.
- Stop Word Removal: Stop words are removed by referring a stop word list.
- Stemming: This converts all the words into its root words. Python library PyStemmer is used.
- Lemmatization (Optional): This removes all the morphological transformations from the words and provides its raw form. NLTK lemmatizer is used for this purpose.
- Term filter: This removes some of the common terms that are found in abundance in all the pages. These include terms like redirect, URL, ping, HTTP ,etc.

**2. Partial Indexes: Extracting & storing essential information in small partial indexes**
The index, consisting of stemmed words and posting list is built for the corpus after performing the above operations. Similar operations are performed for all the other fields. We assign new docids to each instance of the Wikipedia page which helps in reducing the size as the document_id while storing , thereby reducing the index size. Since the size of the corpus will not fit into the main memory thus several index files are generated. We generate the following files:

    - title.txt: It stores the title of the Wikipedia document. Each line in the file is of the following format:

        - 76 International Atomic Time: Here, the 1st token denoted the doc_id of the Wikipedia page in the whole corpus. It will be later used by the search tool to map the doc_id to doc_name.
    
    - titleoffset.txt: This file denotes the offsets that would be used to obtain the title of a particular doc_id using Binary Search on the offsets. Offsets essentially provide the seek values to be used while reading the file to directly read a particular line. Each of the line in the offset denotes the seek value that must be used to read that line directly in the title.txt file

    - numberOfFiles.txt: This denotes the total number of documents that are parsed and indexed. This should be equal to the total number of lines in the file titles.txt

    - index0.txt, index1.txt,..... index9.txt: These files are partial indexes of size as denoted in the config file. Each of these files contain information about the occurence of a word in the corpus. The syntax of each line is as follows:

        - bilstein 139 0 4 0 0 0 642 0 10 0 0 0 4388 0 1 0 0 0 - Here each occurance of the word in a document is denoted by tuple of 6 tokens(eg, 139 0 4 0 0 0). Each of these tuples gives information about its occurence in a Wikipedia document.

        - 139 0 4 0 0 0: Each occurence of term in a document has the following syntax . It corresponds to Doc_Id TitleScore BodyScore InfoScore CategoryScore ExternalLinksScore. Default it stores the frequency of the terms in the following field. The indexer can be configured using config.py to store the scores instead of frequency to improve both the ranking performance as well as improve the search time.

Once we have generated the partial indexes, we can perform merging to obtain a global index that can allow us to search for a term efficiently.

**3. The Global Index: Merging the partial indexes to obtain a sorted big index.**

Now each of these seperate indexes might contain common terms(in fact a large number of terms are common), so we need to merge the terms and create a common index.

Next, these index files are merged using **K-Way Merge Sort Algorithm** creating field-based global index files along with their offsets. After the size of the format [fieldname][fieldnumber].txt . It also stores the offsets in this data in another file named o[fieldname][filenumber].txt for performing the search of a term in the file  in log(n).

Hence, K Way Merge is applied and field-based files are generated along with their respective offsets. These field-based files can be generated using multi-threaded or single-threaded I/0. Multiple I/O simultaneously might not improve the performance, it depends on the configuration of the indexer. Along with this, the vocabulary file is also generated. We generate the following files in this step:

    - b1.txt, t45.txt, i3.txt, c82.txt, e0.txt: These files denote the fields indexes corresponding to the fields Body, Title,, Info Box, Category and External Links respectively, of the file numbers 1,45, 3, 82, 0 respectively. Each of these lines in these files is of the format:

        - aadhar 1324575 12 619212 3 7185170 1 - Here the 1st token correspinds to the name of the word. The next token will correspond to the doc_id of the document in which this word occured followed by the score of the document. Default score is freq. This can be modified to store other score_types by changing the config.py file.
        -The order of doc_id in each line is sorted by the doc score(default score is freq, so sorted by frequency) corresponding to that word.
        - This property is useful as it allows us to obtain Top N documents for each term allowing us to perform various time-based heuristics or word importance based heuristics to improve performance.

