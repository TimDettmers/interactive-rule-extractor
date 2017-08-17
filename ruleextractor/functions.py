import re
import spacy

nlp = spacy.load('en')

class AbstractFunction(object):
    def __init__(self, indexer):
        self.indexer = indexer

    def execute_func(self, arg_string, selection):
        raise NotImplementedError('Classes that inherit from AbstractFunction need to implement the execute_func function!')

    def parse_args(self, arg_string):
        raise NotImplementedError('Classes that inherit from AbstractFunction need to implement the parse_args function!')

class Select(AbstractFunction):
    def __init__(self, indexer):
        super(Select, self).__init__(indexer)
        self.extact_match = re.compile(r'([^"]+)')

    def execute_func(self, arg_string, selection):
        query_text, exact_matches = self.parse_args(arg_string)
        return self.indexer.get_sentences(query_text, exact_matches=exact_matches)

    def parse_args(self, arg_string):
        exact_matches = []
        if '"' in arg_string:
            exact_matches = self.extact_match.findall(arg_string)
        return arg_string, exact_matches

class SpacyProcessor(AbstractFunction):
    def __init__(self, indexer, selection_function):
        super(SpacyProcessor, self).__init__(indexer)
        self.selection_function = selection_function


    def execute_func(self, arg_string, selection):
        if isinstance(selection, list):
            # list of sentences
            return_values = []
            for sent in selection:
                tokens = []
                for token in nlp(sent):
                    tokens.append(self.selection_function(token))
                return_values.append(tokens)
            return return_values
        else:
            tokens = []
            for token in nlp(selection):
                tokens.append(self.selection_function(token))
            return tokens
            # sentence

    def parse_args(self, arg_string):
        pass


