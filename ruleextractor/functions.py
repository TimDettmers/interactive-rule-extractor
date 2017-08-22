import re
import spacy
import ruleextractor
import numpy as np
import dijkstar
import copy

from dijkstar import Graph, find_path

nlp = spacy.load('en')


def check_for_block(selection):
    return_value = True
    if not isinstance(selection, ruleextractor.interpreter.Block):
        if not isinstance(selection[0], ruleextractor.interpreter.Block):
            return_value = False

    if not return_value:
        print('Argument needs to be a block. Call the block command to create a block!')
    return return_value

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
        if not check_for_block(selection): return selection
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

class SurroundFilter(AbstractFunction):
    def __init__(self, indexer):
        super(SurroundFilter, self).__init__(indexer)

    def execute_func(self, arg_string, selection):
        raise NotImplementedError('Classes that inherit from AbstractFunction need to implement the execute_func function!')

    def parse_args(self, arg_string):
        raise NotImplementedError('Classes that inherit from AbstractFunction need to implement the parse_args function!')

class Chunker(AbstractFunction):
    def __init__(self, indexer):
        super(Chunker, self).__init__(indexer)

    def execute_func(self, arg_string, selection):
        if not check_for_block(selection): return selection
        func = self.parse_args(arg_string)
        return func(selection)

    def parse_args(self, arg_string):
        values = arg_string.split(' ')
        chunk_type = values[0]
        if chunk_type == 'pos': return self.chunk_via_POS_tag
        elif chunk_type == 'ent': return self.chunk_via_entities
        else:
            print('Unknown chunk type!')
            return lambda x: x

    def chunk_via_POS_tag(self, selection):
        pass


    def reduce_to_chunk(self, array, end):
        value = array[0]
        for i in range(1, end):
            if array[1] not in value:
                value +=  ' ' + array[1]
        return value

    def chunk_via_entities(self, selection):
        if isinstance(selection, ruleextractor.interpreter.Block):
            blocks = [selection]
        else:
            blocks = selection

        chunked_blocks = []
        for block in blocks:
            prev_tag = None
            start_tag = 0
            scores = np.zeros_like(block.arr[0], dtype=np.int32)
            prev_tags = [None, None, None]
            start_tags = [0, 0, 0]
            chunked_block = ruleextractor.interpreter.Block(block.raw_string, [],[],[],[])

            for feature_id, feature in enumerate([block.ent, block.dep, block.pos]):
                prev_tag = prev_tags[feature_id]
                start_tag = start_tags[feature_id]
                for i, tag in enumerate(feature):
                    if prev_tag is None:
                        prev_tag = tag
                        continue

                    if prev_tag != tag or prev_tag == ' ':
                        if start_tag < i-1:
                            scores[start_tag:i] += 1
                        start_tag = i
                    prev_tag = tag

            data = [(s, t) for s, t in zip(scores, block.tokens)]
            print(data)
            prev_tag = None
            start_tag = 0
            for i, tag in enumerate(scores):
                if prev_tag is None:
                    prev_tag = tag
                    continue

                if prev_tag != tag:
                    if start_tag < i-1:
                        if prev_tag > 1:
                            chunked_block.tokens.append(self.reduce_to_chunk(block.tokens[start_tag:i], i-start_tag))
                            chunked_block.dep.append(self.reduce_to_chunk(block.dep[start_tag:i], i-start_tag))
                            chunked_block.pos.append(self.reduce_to_chunk(block.pos[start_tag:i], i-start_tag))
                            chunked_block.ent.append(self.reduce_to_chunk(block.ent[start_tag:i], i-start_tag))
                        else:
                            for j in range(start_tag, i):
                                chunked_block.tokens.append(block.tokens[j])
                                chunked_block.dep.append(block.dep[j])
                                chunked_block.pos.append(block.pos[j])
                                chunked_block.ent.append(block.ent[j])
                    else:
                        chunked_block.tokens.append(block.tokens[i-1])
                        chunked_block.dep.append(block.dep[i-1])
                        chunked_block.pos.append(block.pos[i-1])
                        chunked_block.ent.append(block.ent[i-1])
                    start_tag = i
                prev_tag = tag
            chunked_block.tokens.append(reduce((lambda x, y: x + ' ' + y), block.tokens[start_tag:]))
            chunked_block.dep.append(reduce((lambda x, y: x + ' ' + y), block.dep[start_tag:]))
            chunked_block.pos.append(reduce((lambda x, y: x + ' ' + y), block.pos[start_tag:]))
            chunked_block.ent.append(reduce((lambda x, y: x + ' ' + y), block.ent[start_tag:]))
            chunked_block.arr = np.array([chunked_block.tokens, chunked_block.ent, chunked_block.pos, chunked_block.dep], dtype=np.unicode_)
            chunked_blocks.append(chunked_block)

        return chunked_blocks






class PathFinder(AbstractFunction):
    def __init__(self, indexer):
        super(PathFinder, self).__init__(indexer)

    def parse_args(self, arg_string):
        func = lambda x: x
        args = []
        values = arg_string.split(' ')
        if len(values) == 3 and values[1] == 'p':
            args = [values[0], values[2]]
            func = self.path_between_words
        elif values[-1].isdigit():
            func = self.get_paths_from_words
            words = values[:-1]
            path_length = int(values[-1])
            args = [words, path_length]
        else:
            print('Could not parse query!')
        return func, args

    def get_paths_from_words(self, words, path_length, selection):
        words = set(words)
        if isinstance(selection, ruleextractor.interpreter.Block):
            blocks = [selection]
        else:
            blocks = selection

        paths = []
        for block in blocks:
            block_paths = []
            for word in nlp(block.raw_string):
                if word.text in words:
                    new_paths = []
                    _ = self.get_paths_from_word(word, path_length, word.text, new_paths)
                    block_paths += new_paths
            paths.append(block_paths)
        return paths


    def get_paths_from_word(self, word, path_length, path_string, path_strings):
        past = copy.deepcopy(path_string)
        if path_length == 0:
            path_strings.append(path_string)
            return path_string
        elif len(list(word.children)) == 0:
            path_strings.append(path_string)
            return path_string
        else:
            for child in word.children:
                self.get_paths_from_word(child, path_length-1, path_string + '->' + child.text, path_strings)
        return past

    def path_between_words(self, word1, word2, selection):
        if isinstance(selection, ruleextractor.interpreter.Block):
            blocks = [selection]
        else:
            blocks = selection
        paths = []
        for block in blocks:
            graph = self.get_graph(block.raw_string)
            cost_func = lambda u, v, e, prev_e: e['cost']
            path = (0, 9999)
            try:
                result = find_path(graph, word1, word2, cost_func=cost_func)
                path = result[0]
                total_cost = result[-1]
                paths.append(path)
            except dijkstar.algorithm.NoPathError:
                print('No path found!')
                pass
                paths.append([])
        return paths

    def get_graph(self, sentence):
        graph = Graph()
        todo = set()
        for word in nlp(sentence):
            root = word
            while root.dep_ != 'ROOT':
                root = root.head
            todo.add(root)

        todo = list(todo)
        while len(todo) > 0:
            child = todo.pop()
            for word in child.children:
                graph.add_edge(child.text, word.text, {'cost': 1})
                graph.add_edge(word.text, child.text, {'cost': 1})
                todo.append(word)
        return graph

    def execute_func(self, arg_string, selection):
        if not check_for_block(selection): return selection
        func, args = self.parse_args(arg_string)
        args.append(selection)
        return func(*args)

