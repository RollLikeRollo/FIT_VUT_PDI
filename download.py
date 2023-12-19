import stream_loader
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
import os
import json

if __name__ == "__main__":
    print("Starting stream download")

    argparse = argparse.ArgumentParser()
    argparse.add_argument("-p", "--path", type=str, default="data")
    args, _ = argparse.parse_known_args()

    stream_loader.submit_async(stream_loader.streamDownload(args.path))

    while True:
        pass
