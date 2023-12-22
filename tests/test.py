#!/usr/bin/env python3

from shutil import rmtree
import unittest
import sys
import json
import subprocess
import os
import datetime

PATH_TEST_DIR = sys.argv[1]
PATH_PDI_PY = sys.argv[2]


def recursiveDirFind(path, extension: str):
    """Recursively finds files with a given extension in a given path"""
    files = []
    # print("path", path)
    for root, dirs, filenames in os.walk(path):
        if filenames:
            for f in filenames:
                if f.endswith(extension):
                    files.append(os.path.join(root, f))
    return files


class assignementOne(unittest.TestCase):
    data = None

    def __init__(self, *args, **kwargs):
        super(assignementOne, self).__init__(*args, **kwargs)

    def setUp(self):
        """Runs the PDI script and returns the output"""

        # print(PATH_PDI_PY)
        # print(PATH_TEST_DIR)

        if assignementOne.data != None:
            return

        print("\nRunning PDI script  Assignment 1")

        res = subprocess.run(
            [
                "python3",
                "pdi.py",
                "-d",
                PATH_TEST_DIR,
                "-o",
                "testing_out",
                "-a",
                "1",
                "-t",
            ],
            capture_output=True,
        )

        out = res.stdout.decode("utf-8")
        out = out.split("\n")
        # print(out)
        o = []
        for s in out:
            if len(s) > 0:
                if s[0] == "[":
                    o.append(s)

        assignementOne.data = o

        orig_data = []
        for file in os.listdir(PATH_TEST_DIR):
            with open(PATH_TEST_DIR + "/" + file, "r") as f:
                fc = json.load(f)
                orig_data.append(fc)
        assignementOne.orig_data = orig_data

    def test_output_not_empty(self):
        self.assertNotEqual(self.data, None)

    def test_output_length(self):
        heading_north = []
        for i in self.orig_data:
            if i["attributes"]["isinactive"] != "false":
                continue
            if (
                i["attributes"]["bearing"] <= 45 and i["attributes"]["bearing"] >= 0
            ) or (
                i["attributes"]["bearing"] >= 315 and i["attributes"]["bearing"] <= 360
            ):
                heading_north.append(i)

        self.assertEqual(len(self.data), len(heading_north))

    def test_0(self):
        example = [x for x in self.orig_data if x["attributes"]["bearing"] == 0]
        example = example[0]
        example = (
            f"[\"{example['attributes']['id']}\", {example['attributes']['bearing']}]"
        )
        if example in self.data:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_45(self):
        example = [x for x in self.orig_data if x["attributes"]["bearing"] == 45]
        example = example[0]
        example = (
            f"[\"{example['attributes']['id']}\", {example['attributes']['bearing']}]"
        )
        if example in self.data:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_315(self):
        example = [x for x in self.orig_data if x["attributes"]["bearing"] == 315]
        example = example[0]
        example = (
            f"[\"{example['attributes']['id']}\", {example['attributes']['bearing']}]"
        )
        if example in self.data:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_180(self):
        example = [x for x in self.orig_data if x["attributes"]["bearing"] == 180]
        example = example[0]
        example = (
            f"[\"{example['attributes']['id']}\", {example['attributes']['bearing']}]"
        )
        if example in self.data:
            self.assertTrue(False)
        else:
            self.assertTrue(True)


class assignementTwo(unittest.TestCase):
    data = None

    def setUp(self):
        if assignementTwo.data != None:
            return

        print("\nRunning PDI script Assignment 2")

        res = subprocess.run(
            [
                "python3",
                "pdi.py",
                "-d",
                PATH_TEST_DIR,
                "-o",
                "testing_out",
                "-a",
                "2",
                "-t",
            ],
            capture_output=True,
        )

        out = None
        out_file = "testing_out/assignement2_trains.txt"
        with open(out_file, "r") as f:
            out = f.read()

        out = out.split("\n")
        out = [x for x in out if len(x) > 0]
        o = []
        for x in out:
            x = x.split(",")
            o.append(x)
        # print(o)
        assignementTwo.data = o

        orig_data = []
        for file in os.listdir(PATH_TEST_DIR):
            with open(PATH_TEST_DIR + "/" + file, "r") as f:
                fc = json.load(f)
                orig_data.append(fc)
        assignementTwo.orig_data = orig_data

    def test_time(self):
        # the testing stream ended at 21-12-2020 19:05:00, started at 19:00:00
        # most last trains should be at 19:03:00 or later

        timestamps = [x[2] for x in self.data]
        timestamps = [x.replace("'", "") for x in timestamps]
        timestamps = timestamps[1:]
        timestamps = [
            datetime.datetime.fromtimestamp(int(x) / 1000) for x in timestamps
        ]

        total = len(timestamps)
        after4 = len([x for x in timestamps if x.hour >= 19 and x.minute >= 4])
        if after4 / total > 0.9:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_no_duplicate_ids(self):
        ids = [x[0] for x in self.data]
        self.assertEqual(len(ids), len(set(ids)))

    def test_include_all_trains(self):
        trains = [
            x
            for x in self.orig_data
            if x["attributes"]["ltype"] == 5
            and x["attributes"]["isinactive"] == "false"
        ]
        trains = [x for x in trains if x != ""]
        trains = [x["attributes"]["id"] for x in trains]
        trains_set = sorted(set(trains))

        ids = [x[0].replace("'", "") for x in self.data]
        ids_set = sorted(set(ids))
        ids_set.remove("id")

        self.assertAlmostEqual(len(trains_set), len(ids_set))
        self.assertAlmostEqual(len(trains_set), len(ids_set))


class assignementThree(unittest.TestCase):
    data = None

    def setUp(self):
        if assignementThree.data != None:
            return

        print("\nRunning PDI script Assignment 3")

        res = subprocess.run(
            [
                "python3",
                "pdi.py",
                "-d",
                PATH_TEST_DIR,
                "-o",
                "testing_out",
                "-a",
                "3",
                "-t",
            ],
            capture_output=True,
        )

        out = res.stdout.decode("utf-8")
        out = out.split("\n")
        # print(out)
        o = []
        for s in out:
            if len(s) > 0:
                if s[0] == "[":
                    s = s.replace("(", '["').replace(")", '"]')
                    s_json = json.loads(s)
                    o.append(s_json)

        assignementThree.data = o

        orig_data = []
        for file in os.listdir(PATH_TEST_DIR):
            with open(PATH_TEST_DIR + "/" + file, "r") as f:
                fc = json.load(f)
                orig_data.append(fc)
        assignementThree.orig_data = orig_data

    def test_ids(self):
        self.orig_data = [
            x for x in self.orig_data if x["attributes"]["isinactive"] == "false"
        ]
        ten_top_delayed = sorted(
            self.orig_data, key=lambda x: x["attributes"]["delay"], reverse=True
        )[:100]

        ten_top_delayed = [
            (x["attributes"]["id"], x["attributes"]["delay"]) for x in ten_top_delayed
        ]
        ten_top_delayed_set = []
        for x in ten_top_delayed:
            if x not in ten_top_delayed_set:
                ten_top_delayed_set.append(x[0])

        last_record = self.data[-1]
        ids_last_record = [
            (x[0].split(",")[0].replace("'", ""), x[0].split(",")[1].replace("'", ""))
            for x in last_record
        ]

        good = True
        for i in ids_last_record:
            i = i[0]
            if i not in ten_top_delayed_set:
                good = False
                break
        self.assertTrue(good)


class assignementFour(unittest.TestCase):
    data = None

    def setUp(self):
        if assignementFour.data != None:
            return

        print("\nRunning PDI script Assignment 4")

        res = subprocess.run(
            [
                "python3",
                "pdi.py",
                "-d",
                PATH_TEST_DIR,
                "-o",
                "testing_out",
                "-a",
                "4",
                "-t",
            ],
            capture_output=True,
        )

        out = res.stdout.decode("utf-8")
        out = out.split("\n")
        # print(out)
        o = []
        for s in out:
            if len(s) > 0:
                if s[0] == "[":
                    s = s.replace("(", '["').replace(")", '"]')
                    s_json = json.loads(s)
                    o.append(s_json)

        assignementFour.data = o

        orig_data = []
        for file in os.listdir(PATH_TEST_DIR):
            with open(PATH_TEST_DIR + "/" + file, "r") as f:
                fc = json.load(f)
                orig_data.append(fc)
        assignementFour.orig_data = orig_data

    def test_time(self):
        last_record = self.data[-1]
        last_record_ids = sorted([x[0] for x in last_record], reverse=True)
        last_record_ids = [x.split(",")[0].replace("'", "") for x in last_record_ids]

        self.orig_data = [
            x for x in self.orig_data if x["attributes"]["isinactive"] == "false"
        ]

        original_timestamps = sorted(
            self.orig_data, key=lambda x: x["attributes"]["delay"], reverse=True
        )

        # the testing stream ended at 21-12-2020 19:05:00
        # last three minutes of data
        t = 1703181905807 - 60 * 3 * 1000

        original_timestamps = [
            x["attributes"]["id"]
            for x in original_timestamps
            if x["attributes"]["delay"] != "" and x["attributes"]["lastupdate"] >= t
        ]
        or_tim_set = sorted(set(original_timestamps), reverse=True)
        or_tim_set = [x.split(",")[0].replace("'", "") for x in or_tim_set]

        good = True
        for i in last_record_ids:
            if i not in or_tim_set:
                good = False
                break

        self.assertTrue(good)

    def test_ids(self):
        self.orig_data = [
            x for x in self.orig_data if x["attributes"]["isinactive"] == "false"
        ]
        original_delays = [x for x in self.orig_data if x["attributes"]["delay"] > 0]

        original_delays_ids_last_time = [
            (
                x["attributes"]["id"],
                x["attributes"]["delay"],
                x["attributes"]["lastupdate"],
            )
            for x in sorted(
                original_delays,
                key=lambda x: x["attributes"]["lastupdate"],
                reverse=True,
            )
        ]

        # print(original_delays_ids_last_time)
        original_ids = [x[0] for x in original_delays_ids_last_time]

        # ten_top_delayed = [
        #     (x["attributes"]["id"], x["attributes"]["delay"]) for x in ten_top_delayed
        # ]
        # ten_top_delayed_set = []
        # for x in ten_top_delayed:
        #     if x not in ten_top_delayed_set:
        #         ten_top_delayed_set.append(x[0])

        last_record = self.data[-1]
        ids_last_record = [
            (
                x[0].split(",")[0].replace("'", ""),
                x[0].split(",")[1].replace("'", ""),
                x[0].split(",")[2].replace("'", ""),
            )
            for x in last_record
        ]

        good = True
        for i in ids_last_record:
            i = i[0].split(",")[0]
            if i not in original_ids:
                good = False
                break
        self.assertTrue(good)

    def test_no_less_than_19_02(self):
        recs = self.data[-10:]
        timestamp = datetime.datetime.fromtimestamp(1703181705000 / 1000)
        for records in recs:
            for record in records:
                timestamp_record = datetime.datetime.fromisoformat(
                    record[0].split(",")[2].replace("'", "").strip()
                )
                if timestamp_record < timestamp:
                    self.assertTrue(False)
                    return
        self.assertTrue(True)


class assignementFive(unittest.TestCase):
    data = None

    def setUp(self):
        if assignementFive.data != None:
            return

        print("\nRunning PDI script Assignment 5")

        res = subprocess.run(
            [
                "python3",
                "pdi.py",
                "-d",
                PATH_TEST_DIR,
                "-o",
                "testing_out",
                "-a",
                "5",
                "-t",
            ],
            capture_output=True,
        )

        out = res.stdout.decode("utf-8")
        out = out.split("\n")
        # print(out)
        o = []
        for s in out:
            if len(s) > 0:
                o.append(s)

        assignementFive.data = o

        orig_data = []
        for file in os.listdir(PATH_TEST_DIR):
            with open(PATH_TEST_DIR + "/" + file, "r") as f:
                fc = json.load(f)
                orig_data.append(fc)
        assignementFive.orig_data = orig_data

    def test_threeminutes(self):
        self.orig_data = [
            x for x in self.orig_data if x["attributes"]["isinactive"] == "false"
        ]
        last_three_minutes = [
            x
            for x in self.orig_data
            if x["attributes"]["lastupdate"] >= 1703181905807 - 60 * 3 * 1000
        ]

        three_min_delays = [x["attributes"]["delay"] for x in last_three_minutes]
        three_min_delays = [x for x in three_min_delays if x != ""]
        three_min_delays = [int(x) for x in three_min_delays]
        three_min_avg = sum(three_min_delays) / len(three_min_delays)

        computed_floats = []
        for x in self.data:
            try:
                x = float(x)
                computed_floats.append(x)
            except:
                continue

        last_computed = float(computed_floats[-1])

        self.assertAlmostEqual(three_min_avg, last_computed, delta=0.1)


class assignementSix(unittest.TestCase):
    data = None

    data_timestamps = None
    orig_avg = None

    def setUp(self):
        if assignementSix.data != None:
            return

        print("\nRunning PDI script Assignment 6")

        res = subprocess.run(
            [
                "python3",
                "pdi.py",
                "-d",
                PATH_TEST_DIR,
                "-o",
                "testing_out",
                "-a",
                "6",
                "-t",
            ],
            capture_output=True,
        )

        out = res.stdout.decode("utf-8")
        out = out.split("\n")
        # print(out)
        o = []
        for s in out:
            if len(s) > 0:
                o.append(s)

        assignementSix.data = o

        orig_data = []
        for file in os.listdir(PATH_TEST_DIR):
            with open(PATH_TEST_DIR + "/" + file, "r") as f:
                fc = json.load(f)
                orig_data.append(fc)
        assignementSix.orig_data = orig_data

    def test_1(self):
        original_data_sorted = sorted(
            self.orig_data, key=lambda x: x["attributes"]["lastupdate"], reverse=True
        )
        orig_sorted_ten = original_data_sorted[:10]

        orig_sorted_ten_date = [
            datetime.datetime.fromtimestamp(x["attributes"]["lastupdate"] / 1000)
            for x in orig_sorted_ten
        ]

        orig_deltas = [
            orig_sorted_ten_date[i] - orig_sorted_ten_date[i - 1]
            for i in range(1, len(orig_sorted_ten_date))
        ]

        def sumTimeDeltas(deltas):
            return sum(deltas, datetime.timedelta())

        orig_sorted_ten_date_sum = sumTimeDeltas(orig_deltas)
        orig_avg = orig_sorted_ten_date_sum / len(orig_deltas)

        orig_avg = str(orig_avg)

        data_timestamps = [x for x in self.data if len(x) > 0 and x[0] == "0"]

        assignementSix.orig_avg = orig_avg
        assignementSix.data_timestamps = data_timestamps

        if orig_avg in data_timestamps:
            self.assertTrue(True)
        else:
            self.assertTrue(False)


if __name__ == "__main__":
    args = sys.argv

    print(args)

    if len(args) != 3:
        print("Usage: python3 test.py <path_to_testing_data> <path_to_pdi_py>")
        sys.exit(1)

    path = args[1]

    print(f"Running tests with data from {path}, using {PATH_PDI_PY} as pdi.py")

    rmtree("testing_out", ignore_errors=True)

    unittest.main(
        argv=["first-arg-is-ignored"],
    )
