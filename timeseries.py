#!/usr/bin/env python


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
        for timestamp in sorted(self.data.keys()):
            print timestamp, " -> ", self.data[timestamp]
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


def generate_two_dummy_data_sets():
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
    return [a_ts, b_ts]
