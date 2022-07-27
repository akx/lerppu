import argparse
import logging

from lerppu.process import do_process


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--output-dir", default="output")
    ap.add_argument("-c", "--use-cache", default=False, action="store_true")
    args = ap.parse_args()
    output_dir = args.output_dir
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s %(name)-32s [%(levelname)-9s] %(message)s",
    )
    do_process(output_dir, use_cache=args.use_cache)


if __name__ == "__main__":
    main()
