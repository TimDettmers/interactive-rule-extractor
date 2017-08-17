from __future__ import print_function
import lucene
import spacy
import sys

from nltk.tokenize import WordPunctTokenizer, PunktSentenceTokenizer
from os.path import join
from java.nio.file import Paths

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import IndexReader, DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.analysis import StopFilter

tok = WordPunctTokenizer()
nlp = spacy.load('en')

#index_dir = "/media/tim/0968cc48-1eab-473a-9133-b15152b5c666/wikipedia/indexdir"
index_dir = "/media/tim/1e30aaa5-4048-4d95-ad4c-402d2ac44544/wikipedia/test"

lucene.initVM()
stopWords = []
stop_set = StopFilter.makeStopSet(stopWords)
analyzer = StandardAnalyzer(stop_set)
reader = DirectoryReader.open(SimpleFSDirectory(Paths.get(index_dir)))
searcher = IndexSearcher(reader)


if len(sys.argv) > 1:
    query_text = ' '.join(sys.argv[1:])
    print(query_text)
else:
    query_text = 'originated in'

while True:
    variable = raw_input('input query!: ')
    parser = QueryParser("sent", analyzer)
    parser.setDefaultOperator(QueryParser.Operator.AND)
    query = parser.parse(variable)
    MAX = 1000
    hits = searcher.search(query, MAX)
    print('%'*80)
    print(variable)
    print('%'*80)

    #print("Found %d document(s) that matched query '%s':" % (hits.totalHits, query))
    for hit in hits.scoreDocs:
        doc = searcher.doc(hit.doc)
        sent = doc.get('sent')
        if variable not in sent: continue
        tokens = [token.text for token in nlp.tokenizer(sent)]
        parse = doc.get('dep')
        tokens_parse = parse.split(' ')
        assert len(tokens) == len(tokens_parse)
        query_tokens = tok.tokenize(query_text)
        ent = doc.get('ent')
        tokens_ent = ent.split(' ')
        pos = doc.get('pos')
        tokens_pos = pos.split(' ')


        quads = []
        for i in range(len(tokens)):
            quads.append((tokens[i], tokens_ent[i], tokens_parse[i], tokens_pos[i]))

        #print(quads)
        print(tokens)
        #start_idx, end_idx = get_idx_of_query_tokens(tokens, query_tokens)

        #person_idx = search_left(tokens_ent, start_idx, set(['PERSON']))
        #org_idx = search_right(tokens_ent,end_idx, set(['ORG', 'GPE']))
        #if person_idx == -1: continue
        #if org_idx == len(tokens_ent): continue
        #indices_p = merge_idx(tokens_ent, person_idx)
        #indices_o = merge_idx(tokens_ent, org_idx)
        #print(merge_indicies_to_text(tokens, indices_p))
        #print(merge_indicies_to_text(tokens, indices_o))
        #print(indices_o, indices_p)
        #print(sent)



        print('='*50)

