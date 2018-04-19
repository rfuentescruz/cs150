class LexicalError(Exception):
    def __init__(self, node):
        self.node = node


class LookupError(LexicalError):
    def __init__(self, node, name):
        self.node = node
        self.name = name

    def __str__(self):
        return 'Undefined name: %s' % self.name

class Scope(object):
    def __init__(self, parent=None):
        self.names = {}
        self.parent = parent

    def __getitem__(self, name):
        try:
            return self.names[name]
        except KeyError:
            if self.parent is not None:
                return self.parent[name]
            else:
                raise LookupError(node=None, name=name)

    def __setitem__(self, name, value):
        self.names[name] = value


root_scope = Scope()


class Node(object):
    def __init__(
        self,
        line=None, children=None, parent=None, scope=None
    ):
        self.line = line
        self.children = children if children else []
        self.parent = parent
        self.scope = scope if scope else root_scope

    def add_child(self, child):
        self.children.append(child)
        child.parent = self


class Statement(Node):
    def execute(self):
        pass


class Expression(Node):
    def evaluate(self):
        return None


class StatementList(Node):
    def execute(self):
        for stmt in self.children:
            if not isinstance(stmt, Statement):
                raise LexicalError(node=self)
            stmt.execute()


class Assign(Statement):
    def __init__(self, name, expr, *args, **kwargs):
        super(Assign, self).__init__(*args, **kwargs)
        self.name = name
        if not isinstance(expr, Expression):
            raise LexicalError(node=self)

        self.expr = expr

    def execute(self):
        self.scope[self.name] = self.expr.evaluate()


class Print(Statement):
    def __init__(self, expr, *args, **kwargs):
        super(Print, self).__init__(*args, **kwargs)
        self.expr = expr

    def execute(self):
        print self.expr.evaluate()


class Lookup(Expression):
    def __init__(self, name, *args, **kwargs):
        super(Lookup, self).__init__(*args, **kwargs)
        self.name = name

    def evaluate(self):
        return self.scope[self.name]


class Literal(Expression):
    def __init__(self, value, *args, **kwargs):
        super(Literal, self).__init__(*args, **kwargs)
        self.value = value

    def evaluate(self):
        return self.value


class List(Expression):
    def __init__(self, items, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.items = items if items else []

    def evaluate(self):
        return [i.evaluate() for i in self.items]


class Index(Expression):
    def __init__(self, target, index, *args, **kwargs):
        super(Index, self).__init__(*args, **kwargs)
        if not isinstance(index, Expression):
            raise LexicalError(node=self)

        self.target = target
        self.index = index

    def evaluate(self):
        target = self.target.evaluate()
        if not isinstance(target, (str, list)):
            raise LexicalError(node=self)

        index = self.index.evaluate()

        if not isinstance(index, int):
            raise LexicalError(node=self)

        return target[index]
