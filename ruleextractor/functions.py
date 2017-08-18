import re
import spacy
import ruleextractor
import numpy as np

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


class Masker(AbstractFunction):
    def __init__(self, indexer):
        super(Masker, self).__init__(indexer)

    def parse_args(self, arg_string):
        return arg_string.split(' ')

    def execute_func(self, arg_string, selection):
        if not self.check_for_block(selection): return selection
        mask_values = self.parse_args(arg_string)

        self.apply_mask(selection, mask_values)
        return selection

    def apply_mask(self, selection, mask_values):
        if isinstance(selection, list): blocks = selection
        else: blocks = [selection]
        for block in blocks:
            master_mask = np.zeros_like(block.arr[0], dtype=np.int32)
            for feature in block.arr:
                for mask_value in mask_values:
                    mask = mask_value == feature
                    if np.count_nonzero(mask) > 0:
                        master_mask += mask
            master_mask = master_mask > 0
            master_mask = master_mask.reshape(1, -1)
            master_mask = np.tile(master_mask, (block.arr.shape[0], 1))
            block.masked = block.arr[master_mask].reshape(block.arr.shape[0], -1)

    def check_for_block(self, selection):
        return_value = True
        if not isinstance(selection, ruleextractor.interpreter.Block):
            if not isinstance(selection[0], ruleextractor.interpreter.Block):
                return_value = False

        if not return_value:
            print('Argument needs to be a block. Call the block command to create a block!')
        return return_value
