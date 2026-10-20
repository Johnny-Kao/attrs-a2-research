"""Baseline-as-oracle against an untouched upstream checkout. Requires A2_BASELINE_SRC."""

# ruff: noqa: PTH100, PT006
import os
import subprocess
import sys

import pytest


BASELINE = os.environ.get("A2_BASELINE_SRC")
pytestmark = pytest.mark.skipif(
    not BASELINE, reason="A2_BASELINE_SRC not configured"
)
SCENARIOS = [
    ("both_atomic", "{str(i):i for i in range(100)}"),
    ("attrs_values", "{str(i): Point(i,i+1) for i in range(100)}"),
    ("attrs_keys", "{Point(i,i+1):i for i in range(100)}"),
    ("subclass", "{str(i): IntSub(i) for i in range(100)}"),
    ("mixed", "{str(i): i if i%2 else Point(i,i+1) for i in range(100)}"),
    ("ordered", "OrderedDict((str(i),i) for i in range(100))"),
]
SCRIPT = """
import attr
from collections import OrderedDict
@attr.define(frozen=True)
class Point:
    x:int
    y:int
class IntSub(int):pass
@attr.define
class Holder:
    m:dict
mapping = {mapping}
try:
    value=attr.astuple(Holder(mapping), filter={filter}, retain_collection_types={retain}, tuple_factory={factory})
    print('OK:' + repr(value))
except Exception as exc:
    print('ERROR:' + type(exc).__name__ + ':' + str(exc))
"""


def run(root, mapping, filter_code, retain, factory):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root)
    code = SCRIPT.format(
        mapping=mapping, filter=filter_code, retain=retain, factory=factory
    )
    return subprocess.check_output(
        [sys.executable, "-c", code], env=env, text=True
    ).strip()


@pytest.mark.parametrize("name,mapping", SCENARIOS)
@pytest.mark.parametrize("filter_code", ["None", "lambda a,v: a.name != 'y'"])
@pytest.mark.parametrize("retain", [True, False])
@pytest.mark.parametrize("factory", ["tuple", "list"])
def test_a2_oracle(name, mapping, filter_code, retain, factory):
    baseline = run(BASELINE, mapping, filter_code, retain, factory)
    candidate = run(
        os.path.abspath("src"), mapping, filter_code, retain, factory
    )
    assert baseline == candidate, name
