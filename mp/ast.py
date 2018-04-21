from __future__ import division


class ParseError(Exception):
    def __init__(self, token):
        self.token = token
        self.message = 'Unrecognized character: %s' % token.value[0]

    @property
    def line_number(self):
        return self.token.lineno

    @property
    def pos(self):
        return self.token.lexpos

class SyntaxError(ParseError):
    def __init__(self, token):
        self.token = token
        self.message = 'Unexpected token: %s' % token.type


class LexicalError(Exception):
    def __init__(self, p=None, index=1, message=None):
        self.p = p
        self.error_index = index
        self.message = message if message else 'Invalid expression / statement'

    @property
    def line_number(self):
        return self.p.lineno(self.error_index)

    @property
    def pos(self):
        return self.p.lexpos(self.error_index)

class LookupError(LexicalError):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        super(LookupError, self).__init__(*args, **kwargs)
        self.message = 'Undefined name: %s' % name


class RuntimeError(Exception):
    def __init__(self, node, index=1, message=None, *args, **kwargs):
        super(RuntimeError, self).__init__(*args, **kwargs)
        self.node = node
        self.index = index
        self.message = message if message else 'Unexpected error'

    @property
    def line_number(self):
        return self.node.p.lineno(self.index)

    @property
    def pos(self):
        return self.node.p.lexpos(self.index)


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
                raise LookupError(name=name)

    def __setitem__(self, name, value):
        self.names[name] = value


root_scope = Scope()


class Node(object):
    def __init__(self, p=None, children=None, parent=None, scope=None):
        self.p = p

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
        r = []
        for stmt in self.children:
            if not isinstance(stmt, Statement):
                raise LexicalError(
                    p=self.p,
                    message='Expected a statement, got %s' % (stmt.__class__)
                )
            r.append(stmt.execute())
        return r


class Assign(Statement):
    def __init__(self, name, expr, *args, **kwargs):
        super(Assign, self).__init__(*args, **kwargs)
        self.name = name
        if not isinstance(expr, Expression):
            raise LexicalError(
                p=self.p,
                message='Expected an expression , got %s' % (stmt.__class__),
                index=3
            )

        self.expr = expr

    def execute(self):
        self.scope[self.name] = self.expr.evaluate()
        return self.scope[self.name]


class Print(Statement):
    def __init__(self, expr, *args, **kwargs):
        super(Print, self).__init__(*args, **kwargs)
        if not isinstance(expr, Expression):
            raise LexicalError(
                p=self.p,
                message='Unable to evaluate and print expression',
                index=2
            )

        self.expr = expr

    def execute(self):
        expr = self.expr.evaluate()
        print expr
        return expr


class ConditionalBranch(Node):
    def __init__(self, expr, statements=None, *args, **kwargs):
        super(ConditionalBranch, self).__init__(*args, **kwargs)
        if expr and not isinstance(expr, Expression):
            raise LexicalError(
                p=self.p,
                message='Invalid conditional expression',
                index=3
            )

        if statements and not isinstance(statements, StatementList):
            raise LexicalError(
                p=self.p,
                message='Invalid conditional body',
                index=6
            )

        self.expr = expr
        self.statements = statements


class Conditional(Statement):
    def __init__(self, fallback=None, *args, **kwargs):
        super(Conditional, self).__init__(*args, **kwargs)
        if fallback and not isinstance(fallback, StatementList):
            raise LexicalError(
                p=self.p,
                message='Invalid "else" body',
                index=11
            )

        self.fallback = fallback

    def execute(self):
        for branch in self.children:
            if branch.expr.evaluate():
                return branch.statements.execute()

        if self.fallback:
            return self.fallback.execute()

        return None


class Loop(Statement):
    def __init__(self, expr, body, *args, **kwargs):
        super(Loop, self).__init__(*args, **kwargs)
        if not isinstance(expr, Expression):
            raise LexicalError(
                p=self.p,
                message='Invalid loop condition',
                index=3
            )

        if not isinstance(body, StatementList):
            raise LexicalError(
                p=self.p,
                message='Invalid loop body',
                index=6
            )

        self.expr = expr
        self.body = body

    def execute(self):
        r = []
        while self.expr.evaluate():
            r.append(self.body.execute())
        return r

class Lookup(Expression):
    def __init__(self, name, *args, **kwargs):
        super(Lookup, self).__init__(*args, **kwargs)
        self.name = name

    def evaluate(self):
        try:
            return self.scope[self.name]
        except LookupError as e:
            e.p = self.p
            raise


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
            raise LexicalError(
                p=self.p,
                message='Invalid index expression',
                index=1
            )
        self.target = target
        self.index = index

    def evaluate(self):
        target = self.target.evaluate()
        if not isinstance(target, (str, list)):
            raise LexicalError(
                p=self.p,
                message='Invalid index target',
                index=1
            )

        index = self.index.evaluate()
        if not isinstance(index, int):
            raise LexicalError(
                p=self.p,
                message='Invalid index expression',
                index=3
            )

        if index < 0:
            raise RuntimeError(
                p=self.p,
                message='Negative indexes not supported',
                index=3
            )

        return target[index]


class BinaryOp(Expression):
    OPERATORS = []

    def __init__(self, left, right, op, *args, **kwargs):
        super(BinaryOp, self).__init__(*args, **kwargs)
        if not isinstance(left, Expression):
            raise LexicalError(
                p=self.p,
                message='Invalid left operand. Expected an %s' % Expression.__class__,
                index=1
            )

        if not isinstance(right, Expression):
            raise LexicalError(
                p=self.p,
                message='Invalid right operand. Expected an %s' % Expression.__class__,
                index=3
            )

        if op not in self.OPERATORS:
            raise LexicalError(
                p=self.p,
                message='Invalid operator: "%s". Supported operators are %s' % (
                    op, self.OPERATORS),
                index=2
            )

        self.left = left
        self.right = right
        self.op = op


class ArithmeticOp(BinaryOp):
    OPERATORS = ['+', '-', '/', '//', '*', '%', '^']

    def evaluate(self):
        l = self.left.evaluate()
        r = self.right.evaluate()

        if not isinstance(l, (int, float)) and self.op != '+':
            raise RuntimeError(
                node=self.left,
                message='Unsupported operation "%s" for type' % self.op
            )

        try:
            if self.op == '+':
                return l + r
            elif self.op == '-':
                return l - r
            elif self.op == '*':
                return l * r
            elif self.op == '/':
                return l / r
            elif self.op == '//':
                return l // r
            elif self.op == '%':
                return l % r
            elif self.op == '^':
                return l ** r
        except (TypeError, ArithmeticError) as e:
            raise RuntimeError(
                node=self.left,
                message='Unable to evaluate operation "%s"' % self.op
            )


class ComparisonOp(BinaryOp):
    OPERATORS = ['==', '!=', '<', '>', '<=', '>=']

    def evaluate(self):
        l = self.left.evaluate()
        r = self.right.evaluate()

        if not isinstance(l, type(r)):
            raise RuntimeError(
                node=self.left,
                message='Unable to compare non-matching types'
            )

        if self.op not in ['==', '!=']:
            if isinstance(l, list) or isinstance(r, list):
                raise RuntimeError(
                    node=self.left,
                    message='Unsupported operation "%s" for type' % self.op
                )

        if self.op == '==':
            return l == r
        elif self.op == '!=':
            return l != r
        elif self.op == '>':
            return l > r
        elif self.op == '<':
            return l < r
        elif self.op == '<=':
            return l <= r
        elif self.op == '>=':
            return l >= r


class LogicalOp(BinaryOp):
    OPERATORS = ['and', 'or']

    def evaluate(self):
        l = self.left.evaluate()
        r = self.right.evaluate()

        if self.op == 'and':
            return bool(l and r)
        elif self.op == 'or':
            return bool(l or r)


class UnaryOp(Expression):
    OPERATORS = ['-', 'not']

    def __init__(self, expr, op, *args, **kwargs):
        super(UnaryOp, self).__init__(*args, **kwargs)
        if not isinstance(expr, Expression):
            raise LexicalError(
                p=self.p,
                message='Invalid unary operand. Expected an %s' % Expression.__class__,
                index=1
            )

        if op not in self.OPERATORS:
            raise LexicalError(
                p=self.p,
                message='Invalid operator: "%s". Supported operators are %s' % (
                    op, self.OPERATORS),
                index=2
            )

        self.expr = expr
        self.op = op

    def evaluate(self):
        expr = self.expr.evaluate()

        if self.op == 'not':
            return bool(not expr)
        elif self.op == '-':
            if not isinstance(expr, (int, float)):
                raise RuntimeError(
                    node=self.expr,
                    message='Unsupported operation "%s" for type' % self.op
                )

            return -expr
