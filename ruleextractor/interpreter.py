from ruleextractor.functions import Select, SpacyProcessor, Masker, PathFinder

import numpy as np

class Block(object):
    def __init__(self, raw_string, tokens, ent, pos, dep):
        self.raw_string = raw_string
        self.tokens = tokens
        self.ent = ent
        self.pos = pos
        self.dep = dep
        self.arr = np.array([self.tokens, self.ent, self.pos, self.dep], dtype=np.unicode_)
        self.masked = None

    def __str__(self):
        if self.masked is not None:
            return str(self.masked)
        else:
            return '{0}\n{1}\n{2}\n{3}'.format(self.tokens, self.ent, self.pos, self.dep)

    def __unicode__(self):
        return unicode(self.__str__())

    def __repr__(self):
        return self.__str__()

class Interpreter(object):
    def __init__(self, indexer):
        self.funcs = {}
        self.init_functions(indexer)
        self.selection = None
        self.selection_history = []
        self.stack = []
        self.do_print = True
        self.history_enabled = True

    def init_functions(self, indexer):
        self.funcs['select'] = Select(indexer)
        self.funcs['mask'] = Masker(indexer)
        self.funcs['path'] = PathFinder(indexer)
        self.funcs['tokenize'] = SpacyProcessor(indexer, lambda x: x.text)
        self.funcs['dep'] = SpacyProcessor(indexer, lambda x: x.dep_)
        self.funcs['pos'] = SpacyProcessor(indexer, lambda x: x.pos_)
        self.funcs['ent'] = SpacyProcessor(indexer, lambda x: x.ent_type_)

    def run(self):
        while True:
            input_value = raw_input(':> ')
            values = input_value.split(' ')
            command = values[0]
            if self.isdigit(command): continue
            if self.unmask(command): continue
            if self.back(command): continue
            if self.push(command): continue
            if self.merge(command): continue
            if self.get_block(command): continue
            if self.check_is_function(command): continue

            self.execute_function(command, values)

    def unmask(self, command):
        if command == 'unmask':
            if isinstance(self.selection, Block):
                self.selection.masked = None
                self.print_selection()
            elif isinstance(self.selection, list):
                if isinstance(self.selection[0], Block):
                    for block in self.selection:
                        block.masked = None
                    self.print_selection()
                else:
                    print('No block selected, cannot unmask!')
            else:
                print('No block selected, cannot unmask!')
            return True
        else:
            return False

    def push(self, command):
        if command == 'push':
            self.stack.append(self.selection)
            self.back('back')
            return True
        else:
            return False

    def get_block(self, command):
        if command == 'block':
            self.do_print = False
            past = self.selection
            self.execute_function('tokenize', '')
            self.push('push')
            self.execute_function('ent', '')
            self.push('push')
            self.execute_function('pos', '')
            self.push('push')
            self.execute_function('dep', '')
            self.push('push')
            self.history_enabled = False
            self.merge('merge')

            if isinstance(past, list):
                blocks = []
                tokens = self.selection[0]
                ents = self.selection[1]
                poss = self.selection[2]
                deps = self.selection[3]
                for i, (token, ent, pos, dep) in enumerate(zip(tokens, ents, poss, deps)):
                    blocks.append(Block(past[i], token, ent, pos, dep))
                self.selection = blocks
            else:
                self.selection = Block(past, self.selection[0], self.selection[1], self.selection[2], self.selection[3])

            self.history_enabled = True
            self.do_print = True
            self.add_to_selection_history(past)
            self.print_selection()

            return True
        else:
            return False

    def merge(self, command):
        if command == 'merge':
            self.add_to_selection_history(self.selection)
            self.selection = self.stack[:]
            self.stack = []
            self.print_selection()
            return True
        else:
            return False

    def execute_function(self, command, values):
        if self.selection is not None: self.add_to_selection_history(self.selection)
        self.selection = self.funcs[command].execute_func(' '.join(values[1:]), self.selection)
        self.print_selection()

    def add_to_selection_history(self, selection):
        if self.history_enabled:
            self.selection_history.append(selection)


    def isdigit(self, command):
        if command.isdigit():
            self.add_to_selection_history(self.selection)
            self.selection = self.selection[int(command)]
            self.print_selection()
            return True
        else:
            return False

    def back(self, command):
        if command == 'back':
            if self.selection_history is None or len(self.selection_history) == 0:
                print('No selection history!')
                return True

            self.selection = self.selection_history.pop()
            self.print_selection()
            return True
        else:
            return False

    def check_is_function(self, command):
        if command not in self.funcs:
            print('Function unknown. Available functions are')
            for key in self.funcs:
                print(key)
            return True
        else:
            return False

    def print_selection(self):
        if self.do_print:
            print('-'*60)
            if isinstance(self.selection, unicode) or isinstance(self.selection, Block):
                print(self.selection)
            else:
                for i, results in enumerate(self.selection):
                    print(i, results)
            print('-'*60)
