#!/usr/bin/env python3

import csv
import re


class stop:
    def __init__(self, map_path="gtfs/stops.txt") -> None:
        self.map_path = map_path
        self.map = {}
        self.stop_regex = re.compile(r"^U(\d+)")
        # print(self.stop_regex)
        self.load_map()

    def load_map(self):
        with open(self.map_path, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                match = re.search(self.stop_regex, row[0])
                if match:
                    self.map[match.group(1).replace("U", "")] = row[1]

    def translate(self, stop_id):
        if type(stop_id) == int:
            stop_id = str(stop_id)
        print("tady ", stop_id)
        return self.map[stop_id]
