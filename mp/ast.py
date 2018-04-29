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

    def __contains__(self, name):
        return name in self.names


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
    def execute(self, scope=root_scope):
        pass


class Expression(Node):
    def evaluate(self, scope):
        return None


class StatementList(Node):
    def execute(self, scope=root_scope):
        for stmt in self.children:
            if not isinstance(stmt, Statement):
                raise LexicalError(
                    p=self.p,
                    message='Expected a statement, got %s' % (stmt.__class__)
                )
            r = stmt.execute(scope)
            if isinstance(stmt, Return):
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

    def execute(self, scope=root_scope):
        scope[self.name] = self.expr.evaluate(scope)


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

    def execute(self, scope=root_scope):
        print self.expr.evaluate(scope)


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

    def execute(self, scope=root_scope):
        for branch in self.children:
            if branch.expr.evaluate(scope):
                branch.statements.execute(scope)
                return

        if self.fallback:
            self.fallback.execute(scope)


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

    def execute(self, scope=root_scope):
        while self.expr.evaluate(scope):
            self.body.execute(scope)



class Lookup(Expression):
    def __init__(self, name, *args, **kwargs):
        super(Lookup, self).__init__(*args, **kwargs)
        self.name = name

    def evaluate(self, scope):
        try:
            return scope[self.name]
        except LookupError as e:
            e.p = self.p
            raise


class Literal(Expression):
    def __init__(self, value, *args, **kwargs):
        super(Literal, self).__init__(*args, **kwargs)
        self.value = value

    def evaluate(self, scope):
        return self.value


class List(Expression):
    def __init__(self, items, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.items = items if items else []

    def evaluate(self, scope):
        return [i.evaluate(scope) for i in self.items]


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

    def evaluate(self, scope):
        target = self.target.evaluate(scope)
        if not isinstance(target, (str, list)):
            raise LexicalError(
                p=self.p,
                message='Invalid index target',
                index=1
            )

        index = self.index.evaluate(scope)
        if not isinstance(index, int):
            raise LexicalError(
                p=self.p,
                message='Invalid index expression',
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

    def evaluate(self, scope):
        l = self.left.evaluate(scope)
        r = self.right.evaluate(scope)

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

    def evaluate(self, scope):
        l = self.left.evaluate(scope)
        r = self.right.evaluate(scope)

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

    def evaluate(self, scope):
        l = self.left.evaluate(scope)
        r = self.right.evaluate(scope)

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

    def evaluate(self, scope):
        expr = self.expr.evaluate(scope)

        if self.op == 'not':
            return bool(not expr)
        elif self.op == '-':
            if not isinstance(expr, (int, float)):
                raise RuntimeError(
                    node=self.expr,
                    message='Unsupported operation "%s" for type' % self.op
                )

            return -expr
