from ruleextractor.functions import Select, SpacyProcessor

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
            if self.back(command): continue
            if self.push(command): continue
            if self.merge(command): continue
            if self.merge4(command): continue
            if self.check_is_function(command): continue

            self.execute_function(command, values)


    def push(self, command):
        if command == 'push':
            self.stack.append(self.selection)
            self.back('back')
            return True
        else:
            return False

    def merge4(self, command):
        if command == 'merge4':
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
                ordered = []
                print(type(self.selection[0]))
                print(type(self.selection[1]))
                print(type(self.selection[2]))
                print(type(self.selection[3]))
                print(len(self.selection))
                tokens = self.selection[0]
                ents = self.selection[1]
                poss = self.selection[2]
                deps = self.selection[3]
                for token, ent, pos, dep in zip(tokens, ents, poss, deps):
                    ordered.append(token)
                    ordered.append(ent)
                    ordered.append(pos)
                    ordered.append(dep)
                self.selection = ordered

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
            if isinstance(self.selection, unicode) or len(self.selection[0]) < 20:
                print(self.selection)
            else:
                for i, results in enumerate(self.selection):
                    print(i, results)
            print('-'*60)
