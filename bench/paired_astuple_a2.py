"""Paired baseline/candidate benchmark using two imports in independent subprocesses.

Usage: python bench/paired_astuple_a2.py --baseline /tmp/baseline/src --candidate ./src
"""

# ruff: noqa: T201, PTH100, PTH118, PTH120, S603
import argparse
import json
import os
import statistics
import subprocess
import sys


parser = argparse.ArgumentParser()
parser.add_argument("--baseline", required=True)
parser.add_argument("--candidate", required=True)
parser.add_argument("--rounds", type=int, default=5)
args = parser.parse_args()
script = os.path.join(
    os.path.dirname(__file__), "bench_astuple_dict_atomic_research.py"
)
out = {}
for round_index in range(args.rounds):
    # ABBA balanced order
    order = (
        ("baseline", "candidate")
        if round_index % 2 == 0
        else ("candidate", "baseline")
    )
    for kind in order:
        root = args.baseline if kind == "baseline" else args.candidate
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.abspath(root)
        proc = subprocess.run(
            [sys.executable, script],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("{"):
                item = json.loads(line)
                out.setdefault(item["workload"], {}).setdefault(
                    kind, []
                ).append(item["us_per_call_median"])
for workload, values in out.items():
    a, b = (
        statistics.median(values["baseline"]),
        statistics.median(values["candidate"]),
    )
    print(
        json.dumps(
            {
                "workload": workload,
                "baseline_us": round(a, 3),
                "candidate_us": round(b, 3),
                "speedup": round(a / b, 3),
                "baseline_samples": values["baseline"],
                "candidate_samples": values["candidate"],
            }
        )
    )
