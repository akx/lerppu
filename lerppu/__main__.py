import argparse
import logging

from rich.logging import RichHandler

from lerppu.process import do_process


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--output-dir", default="output")
    ap.add_argument("-c", "--use-cache", default=False, action="store_true")
    args = ap.parse_args()
    output_dir = args.output_dir
    logging.basicConfig(
        level=logging.INFO,
        datefmt="[%X]",
        format="%(message)s",
        handlers=[RichHandler()],
    )
    do_process(output_dir, use_cache=args.use_cache)


if __name__ == "__main__":
    main()
