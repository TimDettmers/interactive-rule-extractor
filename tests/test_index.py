import pytest

from ruleextractor.index import Indexer


def test_get_sentences():
    idx = Indexer('tests/test_data')
    sents = idx.get_sentences('married to')
    assert len(sents) == 10
