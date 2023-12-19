import shutil
from time import sleep
import datetime
import time
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream import SourceFunction

import multiprocessing
import argparse
import logging
import sys
import asyncio
import stream_loader

# import stream_loader
import os
import json

from pyflink.common.typeinfo import Types
from pyflink.common import WatermarkStrategy, Encoder, Types
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.file_system import (
    FileSource,
    StreamFormat,
    FileSink,
    OutputFileConfig,
    RollingPolicy,
)
import json
from pyflink.common import Configuration
from pyflink.common import Row
from pyflink.datastream.functions import KeyedProcessFunction
from pyflink.datastream.execution_mode import RuntimeExecutionMode
from pyflink.datastream.functions import SourceFunction
from pyflink.datastream.state import MapStateDescriptor
from pyflink.datastream.time_characteristic import TimeCharacteristic
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.table import DataTypes
from pyflink.table.descriptors import Schema, Rowtime
from pyflink.datastream.window import (
    Window,
    SlidingEventTimeWindows,
    SlidingProcessingTimeWindows,
)
from pyflink.common import Duration
from pyflink.datastream.functions import MapFunction
from pyflink.datastream.window import Window, TumblingEventTimeWindows
from pyflink.datastream.state import MapStateDescriptor
from pyflink.datastream.functions import MapFunction
from pyflink.datastream.time_characteristic import TimeCharacteristic
from pyflink.common.time import Time
from pyflink.common import Row
from pyflink.datastream.functions import KeyedProcessFunction
from pyflink.datastream.state import MapStateDescriptor
from pyflink.datastream.state import ListStateDescriptor
from pyflink.datastream.time_characteristic import TimeCharacteristic
from pyflink.common import Row
from pyflink.datastream.functions import *
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.common import Row
from pyflink.common.typeinfo import Types
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.output_tag import OutputTag
from pyflink.datastream.checkpointing_mode import CheckpointingMode
from pyflink.datastream.checkpoint_config import ExternalizedCheckpointCleanup
from pyflink.datastream.functions import ProcessFunction
from pyflink.common import Row, WatermarkStrategy
from pyflink.common.typeinfo import Types
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.table import StreamTableEnvironment
from pyflink.common import Row, WatermarkStrategy
from pyflink.common.typeinfo import Types
from pyflink.common.typeinfo import Types
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.table import StreamTableEnvironment
from pyflink.datastream.connectors import file_system

import translate_stops


def dictFromJson(jsonString):
    jsonString = str(jsonString)
    jsonString = jsonString.replace("'", '"')
    return json.loads(jsonString)


def rowToJson(row: Row):
    return json.dumps(row.as_dict())


def posixtime_to_datetime(posixtime):
    return datetime.datetime.fromtimestamp(int(posixtime) / 1000)


outut_tag_traind = OutputTag("trains", Types.STRING())


class CountTenLastReports(FlatMapFunction):
    def __init__(self) -> None:
        self.count = 0

    def open(self, runtime_context: RuntimeContext):
        desc = ValueStateDescriptor("avg", Types.PICKLED_BYTE_ARRAY())
        self.count = runtime_context.get_state(desc)

    def flat_map(self, value):
        current_timestamp = value[1]["attributes"]["lastupdate"]

        current_count = self.count.value()
        if current_count is None:
            current_count = (1, [current_timestamp])
            self.count.update(current_count)
            yield value[0], current_count

        # if there are less than 10 reports, add the current timestamp to the list
        # only if the timestamp is not before any of the timestamps in the list

        if current_count[0] < 10:
            l = current_count[1]
            min_in_list = min(l)
            if current_timestamp > min_in_list:
                l.append(current_timestamp)
                l.sort()
                self.count.update((current_count[0] + 1, l))
                yield value[0], current_count

        # if there are 10 reports, check if the current timestamp is after the oldest timestamp in the list
        # if it is, remove the oldest timestamp and add the current timestamp to the list
        #
        else:
            l = current_count[1]
            min_in_list = min(l)
            min_list_index = l.index(min_in_list)
            if current_timestamp > min_in_list:
                l[min_list_index] = current_timestamp
                l.sort()
                self.count.update((current_count[0], l))
                yield value[0], current_count


class AverageAggregate(AggregateFunction):
    """
    The accumulator is used to keep a running sum and a count. The :func:`get_result` method
    computes the average.
    """

    def create_accumulator(self):
        r = tuple([0, 0])
        return r

    def add(self, value: tuple[int, dict], accumulator):
        dct = value[1]
        delay = dct["attributes"]["delay"]
        # print("zde")
        return accumulator[0] + delay, accumulator[1] + 1

    def get_result(self, accumulator):
        # print("zde2")
        return accumulator[0] / accumulator[1]

    def merge(self, a, b):
        # print("zde3")
        return a[0] + b[0], a[1] + b[1]


class AverageWindowFunction(ProcessWindowFunction):
    def process(self, key: str, context: ProcessWindowFunction.Context, averages):
        average = next(iter(averages))
        # print("average")
        yield key, average


class FiveMostDelayedTrainsThreeMinutes(ProcessWindowFunction):
    def __init__(self) -> None:
        self.top_delayed = []

    def process(self, key: str, ctx: "ProcessWindowFunction.Context", values):
        for i in values:
            # if new train ID, add it to the state
            key = i["attributes"]["id"]
            delay = i["attributes"]["delay"]
            lastupdate = i["attributes"]["lastupdate"]
            lastupdate = posixtime_to_datetime(lastupdate).strftime("%Y-%m-%d %H:%M:%S")

            rmvd = False

            for i in self.top_delayed:
                dt_lastupdate = datetime.datetime.strptime(
                    lastupdate, "%Y-%m-%d %H:%M:%S"
                )
                i_dt = datetime.datetime.strptime(i[2], "%Y-%m-%d %H:%M:%S")
                if i_dt < dt_lastupdate - datetime.timedelta(minutes=3):
                    self.top_delayed.remove(i)
                    # rmvd = True

            if len(self.top_delayed) < 5 and not rmvd:
                self.top_delayed.append((key, delay, lastupdate))
            else:
                self.top_delayed.sort(key=lambda x: x[1])
                keys = [x[0] for x in self.top_delayed]
                if delay > self.top_delayed[0][1] and key not in keys:
                    self.top_delayed[0] = (key, delay, lastupdate)
                elif key in keys and delay > self.top_delayed[keys.index(key)][1]:
                    index = keys.index(key)
                    self.top_delayed[index] = (key, delay, lastupdate)

        yield self.top_delayed


class FiveMostDelayedTrains(FlatMapFunction):
    def __init__(self) -> None:
        self.top_delayed = []

    def flat_map(self, value):
        # if new train ID, add it to the state
        key = value["attributes"]["id"]
        delay = value["attributes"]["delay"]

        if len(self.top_delayed) < 5:
            self.top_delayed.append((key, delay))
        else:
            self.top_delayed.sort(key=lambda x: x[1])
            keys = [x[0] for x in self.top_delayed]
            if delay > self.top_delayed[0][1] and key not in keys:
                self.top_delayed[0] = (key, delay)
            elif key in keys and delay > self.top_delayed[keys.index(key)][1]:
                index = keys.index(key)
                self.top_delayed[index] = (key, delay)

        yield self.top_delayed


class TrainDict(KeyedProcessFunction):
    def __init__(self) -> None:
        self.train_dict = dict()

    def process_element(self, line, ctx: "KeyedProcessFunction.Context"):
        train_id = line["attributes"]["id"]
        last_stop = line["attributes"]["laststopid"]
        last_update = line["attributes"]["lastupdate"]

        if train_id not in self.train_dict:
            self.train_dict[train_id] = {
                "last_stop": last_stop,
                "last_update": last_update,
            }
            # self.train_dict["updated"] = True
        else:
            if last_update > self.train_dict[train_id]["last_update"]:
                self.train_dict[train_id]["last_stop"] = last_stop
                self.train_dict[train_id]["last_update"] = last_update
            #     self.train_dict["updated"] = True
            # else:
            #     self.train_dict["updated"] = False

        yield self.train_dict


class saveToFile(KeyedProcessFunction):
    def __init__(
        self, header=None, timeformat="posix", translate=False, directory_path="data"
    ) -> None:
        self.tosavedict = dict()
        self.header = header
        self.timeformat = timeformat
        self.translate = False
        self.dir = directory_path
        if translate:
            self.translate = True
            self.map = translate_stops.stop().map

    def process_element(self, value, ctx: KeyedProcessFunction.Context):
        # if the state did not change, do not write to file
        if self.tosavedict == value:
            yield

        # TODO: translate stops

        lines = []
        if self.header:
            lines.append(",".join(self.header))
        for key in value.keys():
            lines.append(
                f"'{key}','{value[key]['last_stop']}','{value[key]['last_update']}'"
            )

        # if the state changed, write to file
        with open(self.dir + "/assignement2_trains.txt", "w") as f:
            f.write("\n".join(lines))
            f.close()

        self.tosavedict = value
        yield


class MyTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, value, record_timestamp):
        return value["attributes"]["lastupdate"]


def sourceDefine(input_path, env: StreamExecutionEnvironment, mode="stream"):
    if input_path is None:
        print("Executing word_count example with default input data set.")
        print("Use --input to specify file input.")
        env.close()
        return
    print(f"Defining source for {input_path}, mode: {mode}")
    if mode == "bulk":
        ds = env.from_source(
            source=FileSource.for_bulk_file_format(
                bulk_format=StreamFormat.text_line_format(), path=input_path
            )
        )
    elif mode == "stream":
        ds = env.from_source(
            source=FileSource.for_record_stream_format(
                StreamFormat.text_line_format(), input_path
            )
            .monitor_continuously(Duration.of_seconds(5))
            .build(),
            watermark_strategy=WatermarkStrategy.for_monotonous_timestamps(),
            source_name="file_source",
        )
    else:
        print("Unknown mode")
        env.close()
        return
    return ds


# # # ----------------------------------------------------------------------------------------------------------------


def Process(input_path, assignment, output_path):
    config = Configuration()
    config.set_string("python.client.executable", "~/.pyenv/shims/python3")

    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)  # BATCH predtim
    # write all the data to one file
    env.set_parallelism(1)
    env.set_stream_time_characteristic(TimeCharacteristic.EventTime)

    # start a checkpoint every 1000 ms
    env.enable_checkpointing(1000)

    # advanced options:

    # set mode to exactly-once (this is the default)
    env.get_checkpoint_config().set_checkpointing_mode(CheckpointingMode.EXACTLY_ONCE)

    # make sure 500 ms of progress happen between checkpoints
    env.get_checkpoint_config().set_min_pause_between_checkpoints(1000)

    # checkpoints have to complete within one minute, or are discarded
    env.get_checkpoint_config().set_checkpoint_timeout(60000)

    # only two consecutive checkpoint failures are tolerated
    env.get_checkpoint_config().set_tolerable_checkpoint_failure_number(2)

    # allow only one checkpoint to be in progress at the same time
    env.get_checkpoint_config().set_max_concurrent_checkpoints(1)

    # enable externalized checkpoints which are retained after job cancellation
    env.get_checkpoint_config().enable_externalized_checkpoints(
        ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
    )

    # enables the unaligned checkpoints
    env.get_checkpoint_config().enable_unaligned_checkpoints()

    # define rolling policy
    roll_pol = RollingPolicy.default_rolling_policy(
        rollover_interval=5 * 100,
        inactivity_interval=5 * 100,
    )

    # define the source
    ds = sourceDefine(input_path, env, mode="stream")

    # define the transformation
    # output is always first 10 words
    ds = ds.flat_map(lambda line: line.split())

    # each data point is a JSON object
    ds = ds.map(dictFromJson)

    # filter out those where isinactive = false
    ds = ds.filter(lambda line: line["attributes"]["isinactive"] == "false")

    # ----------------------------------------------------------------------------------------------------------------
    # # # Assignement 1 - průběžně vypisovat vozidla mířící na sever (s max. odchylkou ± 45 stupnů)

    if assignment == "1":
        # select only those vehicles that are heading north (+- 45 degrees)
        ds_north = ds.filter(
            lambda line: (
                line["attributes"]["bearing"] >= 315
                and line["attributes"]["bearing"] <= 360
            )
            or (
                line["attributes"]["bearing"] <= 45
                and line["attributes"]["bearing"] >= 0
            )
        )
        # select only vehicle id and bearing
        ds_north = ds_north.map(
            lambda line: (
                line["attributes"]["id"],
                line["attributes"]["bearing"],
            )
        )

        # define the sink for north bound vehicles
        ds_north = ds_north.map(
            lambda line: json.dumps(line),
            output_type=Types.STRING(),
        )
        ds_north.sink_to(
            sink=FileSink.for_row_format(
                base_path=output_path + "/assignement1_heading_north",
                encoder=Encoder.simple_string_encoder(),
            )
            .with_output_file_config(
                OutputFileConfig.builder()
                .with_part_prefix("heading_north")
                .with_part_suffix(".ext")
                .build()
            )
            .with_rolling_policy(RollingPolicy.default_rolling_policy())
            .build()
        )
        ds_north.print()

    # ----------------------------------------------------------------------------------------------------------------
    # # # Assignement 2 - vypisovat seznam vlaků s ID (či názvem) jejich poslední hlášené zastávky
    # a časem poslední aktualizace pro každý vlak hlášený od startu aplikace

    if assignment == "2":
        header = ["id", "laststop", "lastupdate"]

        ds_train = ds.filter(lambda line: line["attributes"]["ltype"] == 5)  # 5 = train

        ds_train2 = ds_train.key_by(lambda line: line["attributes"]["id"]).process(
            TrainDict()
        )

        ds_train2.print()

        ds_train2.process(
            saveToFile(
                header=header,
                timeformat="posix",
                translate=True,
                directory_path=output_path,
            )
        )

    # ds_train = ds_train.map(
    #     rowToJson,
    #     output_type=Types.STRING(),
    # )

    # ds_train = ds_train.map(
    #     lambda line: json.dumps(line),
    #     output_type=Types.STRING(),
    # )
    # ds_train.sink_to(
    #     sink=FileSink.for_row_format(
    #         base_path="assignement2_trains", encoder=Encoder.simple_string_encoder()
    #     )
    #     .with_rolling_policy(
    #         RollingPolicy.default_rolling_policy(
    #             rollover_interval=5,
    #             inactivity_interval=5,
    #         )
    #     )
    #     .with_output_file_config(
    #         OutputFileConfig.builder()
    #         .with_part_prefix("trains")
    #         .with_part_suffix(".ext")
    #         .build()
    #     )
    #     .build()
    # )

    # with ds_train.execute_and_collect() as results:
    #     print("--- Assignement 2 ---")
    #     for item in results:
    #         print(item)

    # ----------------------------------------------------------------------------------------------------------------
    # # # Assignement 3 - vypisovat seznam nejvýše 5 zpožděných vozů seřazených sestupně podle
    # jejich posledně hlášeného zpoždění od startu aplikace

    if assignment == "3":
        ds_delay = ds.filter(lambda line: line["attributes"]["delay"] > 0.0)

        # filter 5 most delayed trains
        ds_delay2 = ds_delay.key_by(lambda line: line["attributes"]["id"]).flat_map(
            FiveMostDelayedTrains()
        )

        ds_delay2.print()

        ds_delay2 = ds_delay2.map(
            lambda line: json.dumps(line),
            output_type=Types.STRING(),
        )

        ds_delay2.sink_to(
            sink=FileSink.for_row_format(
                base_path=output_path + "/assignement3_delayed",
                encoder=Encoder.simple_string_encoder(),
            )
            .with_rolling_policy(
                RollingPolicy.default_rolling_policy(
                    rollover_interval=5,
                    inactivity_interval=5,
                )
            )
            .with_output_file_config(
                OutputFileConfig.builder()
                .with_part_prefix("")
                .with_part_suffix(".ext")
                .build()
            )
            .build()
        )

    # ----------------------------------------------------------------------------------------------------------------
    # # # Assignement 4 - vypisovat seznam nejvýše 5 zpožděných vozů hlášených během
    # posledních 3 minut a seřazených setupně podle času jejich poslední aktualizace

    if assignment == "4":
        watermark_strategy = WatermarkStrategy.for_bounded_out_of_orderness(
            Duration.of_seconds(10)
        ).with_timestamp_assigner(MyTimestampAssigner())

        ds_w_timestamp_watermarks = ds.assign_timestamps_and_watermarks(
            watermark_strategy
        )


        ds4 = (
            ds_w_timestamp_watermarks.key_by(lambda line: line["attributes"]["id"])
            .window(
                SlidingProcessingTimeWindows.of(Time.minutes(3), Time.seconds(10))
            )  # minutes 3
            .process(FiveMostDelayedTrainsThreeMinutes())
        )

        ds4 = ds4.map(lambda line: sorted(line, key=lambda x: x[1], reverse=True)[:5])

        ds4.print()

        ds4 = ds4.map(
            lambda line: json.dumps(line),
            output_type=Types.STRING(),
        )

        ds4.sink_to(
            sink=FileSink.for_row_format(
                base_path=output_path + "/assignement4_delayed3minutes",
                encoder=Encoder.simple_string_encoder(),
            )
            .with_rolling_policy(
                RollingPolicy.default_rolling_policy(
                    rollover_interval=5,
                    inactivity_interval=5,
                )
            )
            .with_output_file_config(
                OutputFileConfig.builder()
                .with_part_prefix("")
                .with_part_suffix(".ext")
                .build()
            )
            .build()
        )

    # ----------------------------------------------------------------------------------------------------------------
    # # # Assignement 5 - vypisovat průměrné zpoždění spočítané ze všech vozů (zpožděných i nezpožděných)
    # hlášených během posledních 3 minut

    if assignment == "5":
        watermark_strategy = WatermarkStrategy.for_bounded_out_of_orderness(
            Duration.of_seconds(10)
        ).with_timestamp_assigner(MyTimestampAssigner())

        ds_delay_avg = ds.assign_timestamps_and_watermarks(watermark_strategy)

        # add fake id to all trains so that they can be grouped together
        ds_delay_avg = ds_delay_avg.map(lambda line: (1, line))

        # compute the average delay for all trains - delayed and not delayed - reported in the last 3 minutes
        ds_delay_avg = (
            ds_delay_avg.key_by(lambda line: line[0])
            .window(SlidingProcessingTimeWindows.of(Time.minutes(3), Time.seconds(5)))
            .aggregate(
                AverageAggregate(),
                window_function=AverageWindowFunction(),
                accumulator_type=Types.TUPLE([Types.LONG(), Types.LONG()]),
                output_type=Types.TUPLE([Types.LONG(), Types.DOUBLE()]),
            )
        )

        ds_delay_avg = ds_delay_avg.map(lambda line: line[1])

        ds_delay_avg.print()

        ds_delay_avg = ds_delay_avg.map(
            lambda line: str(line),
            output_type=Types.STRING(),
        )

        ds_delay_avg.sink_to(
            sink=FileSink.for_row_format(
                base_path=output_path + "/assignement5_averagedelay",
                encoder=Encoder.simple_string_encoder(),
            )
            .with_rolling_policy(
                RollingPolicy.default_rolling_policy(
                    rollover_interval=5,
                    inactivity_interval=5,
                )
            )
            .with_output_file_config(
                OutputFileConfig.builder()
                .with_part_prefix("")
                .with_part_suffix(".ext")
                .build()
            )
            .build()
        )

    # ----------------------------------------------------------------------------------------------------------------
    # # # Assignement 6 - vypisovat průměrnou dobu mezi jednotlivými hlášeními se započítáním
    # posledních 10 hlášení

    if assignment == "6":
        watermark_strategy = WatermarkStrategy.for_bounded_out_of_orderness(
            Duration.of_seconds(10)
        ).with_timestamp_assigner(MyTimestampAssigner())

        ds6 = ds.assign_timestamps_and_watermarks(watermark_strategy)

        # add fake id to all trains so that they can be grouped together
        ds6 = ds6.map(lambda line: (1, line))

        ds6 = ds6.key_by(lambda line: line[0]).flat_map(CountTenLastReports())

        ds6 = ds6.map(lambda line: line[1]).map(lambda line: line[1])

        # element is now list of timestamps, converting to datetime
        ds6 = ds6.map(lambda line: [posixtime_to_datetime(x) for x in line])

        # element is now list of timestamps, converting to deltas between timestamps
        ds6 = ds6.map(lambda line: [line[i] - line[i - 1] for i in range(1, len(line))])

        # filter empty lists
        ds6 = ds6.filter(lambda line: len(line) > 0)

        def sumTimeDeltas(deltas):
            return sum(deltas, datetime.timedelta())

        # element is now list of deltas, compute average delta
        ds6 = ds6.map(lambda line: sumTimeDeltas(line) / len(line))

        ds6.print()

        ds6 = ds6.map(
            lambda line: str(line),
            output_type=Types.STRING(),
        )

        ds6.sink_to(
            sink=FileSink.for_row_format(
                base_path=output_path + "/assignement6_last10reports",
                encoder=Encoder.simple_string_encoder(),
            )
            .with_rolling_policy(
                RollingPolicy.default_rolling_policy(
                    rollover_interval=5,
                    inactivity_interval=5,
                )
            )
            .with_output_file_config(
                OutputFileConfig.builder()
                .with_part_prefix("")
                .with_part_suffix(".ext")
                .build()
            )
            .build()
        )

    # submit for execution
    env.execute()


# # # ----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--output", dest="output", required=False, help="Output directory."
    )
    parser.add_argument(
        "-d",
        dest="d",
        required=False,
        default="data",
        help="Directory to save incoming stream data to. Stream will be read from this directory.",
    )
    parser.add_argument(
        "-s",
        dest="s",
        required=False,
        default=False,
        action="store_true",
        help="Whether to start the stream loader in the background.",
    )

    parser.add_argument(
        "-a",
        "--assignment",
        dest="assignment",
        required=True,
        default="1",
        type=str,
        choices=["1", "2", "3", "4", "5", "6"],
        help=(
            "Assignment to run. "
            " 1 - průběžně vypisovat vozidla mířící na sever (s max. odchylkou ± 45 stupnů)"
            " 2 - vypisovat seznam vlaků s ID (či názvem) jejich poslední hlášené zastávky a časem poslední aktualizace pro každý vlak hlášený od startu aplikace"
            " 3 - vypisovat seznam nejvýše 5 zpožděných vozů seřazených sestupně podle jejich posledně hlášeného zpoždění od startu aplikace"
            " 4 - vypisovat seznam nejvýše 5 zpožděných vozů hlášených během posledních 3 minut a seřazených setupně podle času jejich poslední aktualizace"
            " 5 - vypisovat průměrné zpoždění spočítané ze všech vozů (zpožděných i nezpožděných) hlášených během posledních 3 minut"
            " 6 - vypisovat průměrnou dobu mezi jednotlivými hlášeními se započítáním posledních 10 hlášení"
            " Body 2 - 6 - vypisuje do souboru, ktery se neustale prepisuje"
        ),
    )

    argv = sys.argv[1:]
    known_args, _ = parser.parse_known_args(argv)

    # known_args.assignment = "1"
    # known_args.input = (
    #     "/home/jzboril/Documents/VUT/mit/2mit_zimni_s/pdi/FIT_VUT_PDI_projekt/data"
    # )

    # shutil.rmtree(known_args.p, ignore_errors=True)

    # start stream download in background in another thread
    # and continue with data processing
    if known_args.s:
        print("Creating stream loader")
        stream_loader.submit_async(stream_loader.streamDownload(known_args.d))

    # print("sleeping for 10 seconds until the stream loader downloads some data")  # TODO
    # sleep(10)

    print("Starting the computation")
    Process(known_args.d, known_args.assignment, known_args.output)
