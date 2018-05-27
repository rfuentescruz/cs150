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
    '''Container for variable bindings in a given scope

    These scope objects are dictionary-like objects that contains the name and
    value bindings for a variable in their scope. Scopes have a hierarchy that
    allows a lookup to fallback to the parent scope when the value cannot be
    found in the current scope but provide a Copy-on-Write method that will
    override the variable in the current scope only, allowing recursion.
    '''
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

    def __delitem__(self, name):
        del self.names[name]


root_scope = Scope()


class Node(object):
    '''Base AST node'''
    def __init__(self, p=None, children=None, parent=None, scope=None):
        self.p = p

        self.children = children if children else []
        self.parent = parent

        self.scope = scope if scope else root_scope

    def add_child(self, child):
        self.children.append(child)
        child.parent = self


class Statement(Node):
    '''Statement AST node

    These nodes execute some procedure without and do not return a value.
    '''
    def execute(self, scope=root_scope):
        pass


class Expression(Node):
    '''Expression AST node

    These nodes are evaluated / executed and are expected to return a value
    that can be used or chained with other expressions as well.
    '''
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
            # Return statements should immediately halt execution or if the
            # current scope signals that a return has happened in any of the
            # nested statement lists within the scope (i.e. loop bodies inside
            # functions).
            if isinstance(stmt, Return) or 'return' in scope:
                return r


class Assign(Statement):
    '''Assign the value of an expression to a variable `name`'''
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

class IndexAssign(Statement):
    '''Assign the value of an expression to an array `ref` at index `index`'''
    def __init__(self, ref, index, value, *args, **kwargs):
        super(IndexAssign, self).__init__(*args, **kwargs)
        # References can be expressions so we can access indeces like this
        # `(array_a + array_b)[2]`
        if not isinstance(ref, Expression):
            raise LexicalError(
                p=self.p,
                message='Expected an expression , got %s' % (ref.__class__),
                index=1
            )
        self.ref = ref

        # Indeces can be expressions too
        if not isinstance(index, Expression):
            raise LexicalError(
                p=self.p,
                message='Expected an expression , got %s' % (index.__class__),
                index=3
            )

        self.index = index

        if not isinstance(value, Expression):
            raise LexicalError(
                p=self.p,
                message='Expected an expression , got %s' % (value.__class__),
                index=6
            )
        self.value = value

    def execute(self, scope=root_scope):
        ref = self.ref.evaluate(scope)
        if not isinstance(ref, (str, list)):
            raise RuntimeError(
                node=self, index=1, message='Unable to index a non-list'
            )

        index = self.index.evaluate(scope)
        if not isinstance(index, int) or index < 0:
            raise RuntimeError(
                node=self,
                index=3,
                message='Invalid index expression. Indeces must be positive integers.'
            )

        if len(ref) <= index:
            raise RuntimeError(
                node=self,
                message='Index out of range',
                index=3
            )
        ref[index] = self.value.evaluate(scope)


class Print(Statement):
    '''Print the value of an expression'''
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
    '''Defines a branch in a conditional expression (`if`, `else if`) and its body (`statements`)'''
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
    '''A conditional statement composed of one or more branches (`if`, `else if`) and fallback (`else`)'''
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
        # Children of a conditional node are conditional branches (if, else-if)
        # that we evaluate to determine which branch to execute
        for branch in self.children:
            if branch.expr.evaluate(scope):
                branch.statements.execute(scope)
                # do not evaluate other branches anymore
                return

        # If we reach this, then couldn't find a matching branch, execute `else`
        if self.fallback:
            self.fallback.execute(scope)


class Loop(Statement):
    '''Execute a `body` of statements repeatedly until `expr` is false'''
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
        # Loop until the conditional for the loop is `false` or a `return` was
        # signalled from any of the nested code blocks
        while self.expr.evaluate(scope) and 'return' not in scope:
            self.body.execute(scope)


class Return(Statement):
    '''Return control to the previous caller'''
    def __init__(self, expr, *args, **kwargs):
        super(Return, self).__init__(*args, **kwargs)
        self.expr = expr

    def execute(self, scope):
        # Signal the current scope that we need to return control to the caller
        # this signal will be checked by loop bodies to make sure that they
        # do not continue processing the loop and return instead.
        scope['return'] = self.expr.evaluate(scope)
        return scope['return']


class Function(Statement):
    '''Define a function `name` with an expected list of arguments `arg_list`'''
    def __init__(self, name, arg_list, body, *args, **kwargs):
        super(Function, self).__init__(*args, **kwargs)
        self.name = name
        self.arg_list = arg_list
        self.body = body

    def execute(self, scope):
        # Define the function in scope
        if self.name in scope:
            raise RuntimeError(
                node=self.p,
                message='Unable to define function "%s". Name already defined',
                index=2
            )
        scope[self.name] = self


class BareExpression(Statement):
    '''Execute an expression as-is

    This doesn't look like all that use full because this implies that a
    statement `1 + 2` is possible without assigning it to a variable. But this
    allows us to execute functions and not care about the return value.
    '''
    def __init__(self, expr, *args, **kwargs):
        super(BareExpression, self).__init__(*args, **kwargs)
        self.expr = expr

    def execute(self, scope):
        self.expr.evaluate(scope)

class FunctionCall(Expression):
    '''Execute a function named `name` with the arguments `call_args`'''
    def __init__(self, name, call_args, *args, **kwargs):
        self.name = name
        self.call_args = call_args

    def evaluate(self, scope):
        # Get the function from the current scope
        f = scope[self.name]

        # Create a new scope based on the current scope
        new_scope = Scope(parent=scope)
        for (i, arg) in enumerate(self.call_args.items):
            # Inject the argument values in the new scope of the function
            new_scope[f.arg_list[i]] = arg.evaluate(scope)

        # Execute the function body with the new scope
        r = f.body.execute(new_scope)

        # If the function returned something, use the return value as the
        # value of this expression
        if 'return' in new_scope:
            r = new_scope['return']
            del new_scope['return']

        return r

class Lookup(Expression):
    '''Lookup a name from the current scope and return its value'''
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
    '''Return the value of the item in an array `target` at index `index`'''
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
            raise RuntimeError(
                node=self,
                message='Invalid index expression: "%s"' % index,
                index=3
            )

        if index < 0:
            raise RuntimeError(
                node=self,
                message='Negative indexes not supported: %d' % index,
                index=3
            )

        if len(target) <= index:
            raise RuntimeError(
                node=self,
                message='Index out of range',
                index=3
            )

        return target[index]


class BinaryOp(Expression):
    '''Operators representing an operation against two expressions `left` and `right`'''
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

        # If the operation is not addition, then only allow integers and
        # floating point numbers. Else addition is ok for list and strings as
        # concatenation.
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
                if r == 0:
                    raise RuntimeError(
                        node=self.left,
                        message='Division by zero'
                    )
                return l / r
            elif self.op == '//':
                if r == 0:
                    raise RuntimeError(
                        node=self.left,
                        message='Division by zero'
                    )
                return l // r
            elif self.op == '%':
                if r == 0:
                    raise RuntimeError(
                        node=self.left,
                        message='Division by zero'
                    )
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

        # Only allow equality comparison for lists
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

        # Short-circuit evaluation
        if self.op == 'and' and not l:
            return False
        elif self.op == 'or' and l:
            return True

        r = self.right.evaluate(scope)

        if self.op == 'and':
            return bool(l and r)
        elif self.op == 'or':
            return bool(l or r)


class UnaryOp(Expression):
    '''Represents operations for a single value'''
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
            # Only allow negation for integers and floats
            if not isinstance(expr, (int, float)):
                raise RuntimeError(
                    node=self.expr,
                    message='Unsupported operation "%s" for type' % self.op
                )

            return -expr


class Length(Expression):
    '''Get the length of list or string'''
    def __init__(self, array, *args, **kwargs):
        super(Length, self).__init__(*args, **kwargs)
        if not isinstance(array, Expression):
            raise LexicalError(
                p=self.p,
                index=2,
                message='Expected an expression, got "%s"' % array.__class__
            )
        self.array = array

    def evaluate(self, scope=root_scope):
        a = self.array.evaluate(scope)
        if not isinstance(a, (list, str)):
            raise RuntimeError(node=self, index=2, message='Unable to calculate length of a non-list')
        return len(a)
