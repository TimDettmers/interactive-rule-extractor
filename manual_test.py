from ruleextractor.index import Indexer
from ruleextractor.interpreter import Interpreter

idx = Indexer('tests/test_data')
intp = Interpreter(idx)
intp.run()

