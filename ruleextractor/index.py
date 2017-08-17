from __future__ import print_function
import lucene
import sys

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


lucene.initVM()

class Indexer(object):
    def __init__(self, index_directory):
        stopWords = []
        stop_set = StopFilter.makeStopSet(stopWords)
        analyzer = StandardAnalyzer(stop_set)
        reader = DirectoryReader.open(SimpleFSDirectory(Paths.get(index_directory)))
        self.searcher = IndexSearcher(reader)
        self.sent_parser = QueryParser("sent", analyzer)
        self.sent_parser.setDefaultOperator(QueryParser.Operator.AND)

    def get_sentences(self, query_text, max_hits=1000, exact_matches=[]):
        query = self.sent_parser.parse(query_text)
        hits = self.searcher.search(query, max_hits)

        sents = []
        for hit in hits.scoreDocs:
            exclude = False
            doc = self.searcher.doc(hit.doc)
            sent = doc.get('sent')
            for exact_match in exact_matches:
                if exact_match not in sent:
                    exclude = True
                    break

            if exclude: continue
            sents.append(sent)
        return sents
