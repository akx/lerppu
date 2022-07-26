import argparse
import logging

from lerppu.process import do_process


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--output-dir", default="output")
    args = ap.parse_args()
    output_dir = args.output_dir
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s %(name)-24s [%(levelname)-9s] %(message)s",
    )
    do_process(output_dir)


if __name__ == "__main__":
    main()
