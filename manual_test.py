from ruleextractor.index import Indexer
from ruleextractor.interpreter import Interpreter
index_path = '/media/tim/1e30aaa5-4048-4d95-ad4c-402d2ac44544/wikipedia/indexdir2'

#idx = Indexer('tests/test_data')
idx = Indexer(index_path)
intp = Interpreter(idx)
intp.run()

