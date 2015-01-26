#!/usr/bin/env python

class ExprNode(object):
    def eval(self):
        raise NotImplementedError("Can't use base Expr's eval()")


class IdentityNode(object):
    def __init__(self, node):
        self.node = node

    def eval(self):
        return self.node.eval()


class TimeSeriesNode(ExprNode):
    def __init__(self, ts):
        self.time_series = ts

    def eval(self):
        return self.time_series


class TwoOperandNode(ExprNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class SubtractionNode(TwoOperandNode):
    def eval(self):
        return self.left.eval().subtract_time_series(self.right.eval())


class AdditionNode(TwoOperandNode):
    def eval(self):
        return self.left.eval().add_time_series(self.right.eval())


class MultiplicationNode(TwoOperandNode):
    def eval(self):
        return self.left.eval().multiply_time_series(self.right.eval())


class DivisionNode(TwoOperandNode):
    def eval(self):
        return self.left.eval().divide_time_series(self.right.eval())


class ModuloNode(ExprNode):
    def __init__(self, node, quotient):
        self.node = node
        self.quotient = quotient

    def eval(self):
        return self.node.eval().modulo(self.quotient)
