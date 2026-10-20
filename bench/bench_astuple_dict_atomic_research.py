"""Standalone A2 benchmark; compare baseline and candidate via PYTHONPATH."""

# ruff: noqa: T201
import json
import statistics
import timeit

from collections import OrderedDict

import attr


@attr.define(frozen=True)
class Item:
    x: int
    y: int


@attr.define
class Holder:
    mapping: dict


class IntSub(int):
    pass


WORKLOADS = {
    "atomic_keys": {str(i): Item(i, i + 1) for i in range(1000)},
    "atomic_values": {Item(i, i + 1): i for i in range(1000)},
    "both_atomic": {str(i): i for i in range(1000)},
    "mixed": {str(i): Item(i, i + 1) if i % 2 else i for i in range(1000)},
    "int_subclass": {str(i): IntSub(i) for i in range(1000)},
    "ordered_dict": OrderedDict((str(i), i) for i in range(1000)),
}


def measure(data):
    def convert():
        return attr.astuple(data)

    result = convert()
    count = 150
    samples = timeit.repeat(convert, number=count, repeat=7)
    return {
        "us_per_call_median": round(
            statistics.median(samples) * 1e6 / count, 3
        ),
        "result_repr": repr(result)[:120],
    }


if __name__ == "__main__":
    print("attrs:", attr.__file__)
    for name, mapping in WORKLOADS.items():
        print(json.dumps({"workload": name, **measure(Holder(mapping))}))
