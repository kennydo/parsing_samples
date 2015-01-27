#!/usr/bin/env python

import string
import funcparserlib.parser as p

import nodes
from timeseries import ScalarTimeSeries, TimeSeries, generate_two_dummy_data_sets


if __name__ == "__main__":
    input_ts = dict(zip(['A_TS', 'B_TS'], generate_two_dummy_data_sets()))

    integer = p.oneplus(p.some(lambda c: c.isdigit())) >> (lambda toks: int(''.join(toks)))
    def to_number(toks):
        if not toks[1]:
            return float(toks[0])
        return float("%s.%s".format(toks))
    number = integer + p.maybe(p.skip(p.a('.')) + integer) >> to_number
    timeseries_name = p.oneplus(p.some(lambda c: c.isupper() or c == '_')) >> (lambda toks: ''.join(toks))

    timeseries_expr = timeseries_name >> (lambda name: nodes.TimeSeriesNode(input_ts[name]))
    scalar_expr = number >> (lambda n: nodes.TimeSeriesNode(ScalarTimeSeries(n)))

    expr = p.forward_decl()

    expr_rest = p.forward_decl()
    expr.define(
        timeseries_expr + expr_rest >> (lambda x: x[1](x[0]))
        | scalar_expr + expr_rest >> (lambda x: x[1](x[0]))
    )

    # Holy cow, is this there a better way to get around left-recursion?
    def generate_arithmetic_node_function(node_type):
        # the left and right names here are misleading and wrong
        def outer(right):
            def inner(left):
                if left is not None and right is not None:
                    #print "Making " + str(node_type) + " with " + str(right) + " and " + str(left)
                    return node_type(left, right)
                return left or right
            return inner
        return outer

    expr_rest.define(
        p.maybe(p.skip(p.a('+')) + expr) >> generate_arithmetic_node_function(nodes.AdditionNode)
        | p.maybe(p.skip(p.a('-')) + expr) >> generate_arithmetic_node_function(nodes.SubtractionNode)
        | p.maybe(p.skip(p.a('*')) + expr) >> generate_arithmetic_node_function(nodes.MultiplicationNode)
        | p.maybe(p.skip(p.a('/')) + expr) >> generate_arithmetic_node_function(nodes.DivisionNode)
    )

    # the skip(finished) idiom is to keep errors from being swallowed
    user_expression = expr + p.skip(p.finished)
    result_ts = user_expression.parse("A_TS").eval()
    result_ts.pretty_print("Raw time series")

    result_ts = user_expression.parse("100").eval()
    result_ts.pretty_print("Just a scalar")

    result_ts = user_expression.parse("A_TS+100").eval()
    result_ts.pretty_print("Time series plus scalar")

    # things below here don't work correctly

    result_ts = expr.parse("A_TS+2000+B_TS").eval()
    result_ts.pretty_print("Time series plus scalar plus time series")

    result_ts = expr.parse("A_TS/0.75").eval()
    result_ts.pretty_print("Time series times scalar")

    result_ts = expr.parse("A_TS%3").eval()
    result_ts.pretty_print("Time series modulo scalar")
