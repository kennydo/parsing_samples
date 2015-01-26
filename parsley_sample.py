#!/usr/bin/env python

# Playing around with the Parsley library.
# The TimeSeries class doesn't do any sort of error checking, so
# don't use this in any production code.

import math
import parsley
import string

class TimeSeries(object):
    def __init__(self, xy_pairs):
        self.data = dict(xy_pairs)
        self.is_time_series = True

    def add_time_series(self, other_ts):
        xy_pairs = []
        timestamps = set(self.data.keys()).union(set(other_ts.data.keys()))
        for timestamp in timestamps:
            xy_pairs.append((timestamp, self.data.get(timestamp, 0) + other_ts.data.get(timestamp, 0)))
        return TimeSeries(xy_pairs)

    def subtract_time_series(self, other_ts):
        xy_pairs = []
        timestamps = set(self.data.keys()).union(set(other_ts.data.keys()))
        for timestamp in timestamps:
            xy_pairs.append((timestamp, self.data.get(timestamp, 0) - other_ts.data.get(timestamp, 0)))
        return TimeSeries(xy_pairs)

    def multiply_time_series(self, other_ts):
        xy_pairs = []
        timestamps = set(self.data.keys()).union(set(other_ts.data.keys()))
        for timestamp in timestamps:
            xy_pairs.append((timestamp, self.data.get(timestamp, 0) * other_ts.data.get(timestamp, 0)))
        return TimeSeries(xy_pairs)

    def divide_time_series(self, other_ts):
        xy_pairs = []
        timestamps = set(self.data.keys()).union(set(other_ts.data.keys()))
        for timestamp in timestamps:
            xy_pairs.append((timestamp, float(self.data.get(timestamp, 0)) / float(other_ts.data.get(timestamp, 0))))
        return TimeSeries(xy_pairs)

    def modulo(self, quotient):
        return TimeSeries([(timestamp, value % quotient) for timestamp, value in self.data.iteritems()])

    def pretty_print(self, title=None):
        print '>' + '-' * 79
        if title:
            print title
        for timestamp in sorted(result_ts.data.keys()):
            print timestamp, " -> ", result_ts.data[timestamp]
        print '-' * 79 + '<'


class ConstantDict(object):
    """A fake dictionary that always returns the same value
    """
    def __init__(self, value):
        self.value = value

    def __len__(self):
        return 1

    def get(self, key, default=None):
        return self.value

    def __getitem__(self, key):
        return self.value

    def __setitem__(self, key, value):
        raise ValueError("Can't change the value of a ConstantDict!")

    def __delitem__(self, key):
        raise ValueError("Can't delete from a ConstantDict!")

    def iteritems(self):
        return []

    def __iter__(self):
        return []

    def __contains__(self, item):
        return True

    def keys(self):
        return []


class ScalarTimeSeries(TimeSeries):
    def __init__(self, scalar):
        self.data = ConstantDict(scalar)


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


if __name__ == "__main__":
    # this is just some dummy data
    timestamps = [
        1422244726 + (x * 60)
        for x in range(0, 10)
    ]
    data_a = range(0, 10, 1)
    # data_b alternates between 20 and 30
    data_b = [20 + 10 * (x % 2) for x in range(0,10)]

    a_ts = TimeSeries(zip(timestamps, data_a))
    b_ts = TimeSeries(zip(timestamps, data_b))

    grammar = parsley.makeGrammar("""
        digit = anything:x ?(x in string.digits) -> x
        uppercase_alpha = anything:x ?(x in string.ascii_uppercase) -> x
        timeseries_name = <(uppercase_alpha|'_')+>:x -> x
        number = <digit+ '.'? digit*>:x -> float(x)

        expr = ( expr:a '+' expr:b -> AdditionNode(a, b)
               | expr:a '-' expr:b -> SubtractionNode(a, b)
               | expr:a '*' expr:b -> MultiplicationNode(a, b)
               | expr:a '/' expr:b -> DivisionNode(a, b)
               | expr:a '%' number:quotient -> ModuloNode(a, quotient)
               | timeseries_name:a -> TimeSeriesNode(input_ts[a])
               | number:scalar -> TimeSeriesNode(ScalarTimeSeries(scalar))
               | '(' expr:e ')' -> IdentityNode(e)
               )
    """, {
        'string': string,
        'TimeSeriesNode': TimeSeriesNode,
        'IdentityNode': IdentityNode,
        'AdditionNode': AdditionNode,
        'SubtractionNode': SubtractionNode,
        'MultiplicationNode': MultiplicationNode,
        'DivisionNode': DivisionNode,
        'ModuloNode': ModuloNode,
        'ScalarTimeSeries': ScalarTimeSeries,
        'input_ts': {
            'A_TS': a_ts,
            'B_TS': b_ts,
        },
    })

    result_ts = grammar("A_TS").expr().eval()
    result_ts.pretty_print("Raw time series")

    result_ts = grammar("100").expr().eval()
    result_ts.pretty_print("Just a scalar")

    result_ts = grammar("A_TS+100").expr().eval()
    result_ts.pretty_print("Time series plus scalar")

    # Two constants in a row don't work well right now, so use parens
    result_ts = grammar("(A_TS+1000)-600").expr().eval()
    result_ts.pretty_print("Time series plus scalar minus scalar")

    result_ts = grammar("A_TS+2000+B_TS").expr().eval()
    result_ts.pretty_print("Time series plus scalar plus time series")

    result_ts = grammar("A_TS*0.75").expr().eval()
    result_ts.pretty_print("Time series times scalar")

    result_ts = grammar("(A_TS/B_TS)*100").expr().eval()
    result_ts.pretty_print("Time series divided by time series")

    result_ts = grammar("A_TS%3").expr().eval()
    result_ts.pretty_print("Time series modulo scalar")
