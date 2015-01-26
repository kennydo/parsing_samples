#!/usr/bin/env python

# Playing around with the Parsley library.
# The TimeSeries class doesn't do any sort of error checking, so
# don't use this in any production code.

import math
import parsley
import string

import nodes
from timeseries import ScalarTimeSeries, TimeSeries, generate_two_dummy_data_sets


if __name__ == "__main__":
    a_ts, b_ts = generate_two_dummy_data_sets()

    grammar = parsley.makeGrammar("""
        digit = anything:x ?(x in string.digits) -> x
        uppercase_alpha = anything:x ?(x in string.ascii_uppercase) -> x
        timeseries_name = <(uppercase_alpha|'_')+>:x -> x
        number = <digit+ '.'? digit*>:x -> float(x)

        expr = ( expr:a '+' expr:b -> nodes.AdditionNode(a, b)
               | expr:a '-' expr:b -> nodes.SubtractionNode(a, b)
               | expr:a '*' expr:b -> nodes.MultiplicationNode(a, b)
               | expr:a '/' expr:b -> nodes.DivisionNode(a, b)
               | expr:a '%' number:quotient -> nodes.ModuloNode(a, quotient)
               | timeseries_name:a -> nodes.TimeSeriesNode(input_ts[a])
               | number:scalar -> nodes.TimeSeriesNode(ScalarTimeSeries(scalar))
               | '(' expr:e ')' -> nodes.IdentityNode(e)
               )
    """, {
        'string': string,
        'nodes': nodes,
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
