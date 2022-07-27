import logging
import os
from itertools import chain

import httpx
import pandas as pd

from lerppu.html_output import write_html
from lerppu.sources import verk, jimms, proshop
from lerppu.validation import validate_products

log = logging.getLogger(__name__)


def do_process(output_dir: str) -> None:
    log.info("Downloading information...")
    with httpx.Client() as sess:
        products = list(
            validate_products(
                chain(
                    verk.get_category_products(sess, category_id="3704c"),
                    jimms.get_category_products(sess, category_id="000-0MU"),
                    proshop.get_category_products(sess, category_id="Kovalevy"),
                )
            )
        )
    log.info("Creating dataframe...")
    df = pd.DataFrame(products)
    df["gb_per_eur"] = (df["size_mb"] / df["current_price"] / 1024.0).round(3)
    df["discount"] = (df["original_price"] - df["current_price"]).round(2)
    df["size_tb"] = (df["size_mb"] / 1024 / 1024).round(2)
    df["eur_per_tb"] = (df["current_price"] / df["size_tb"]).round(3)
    df.drop(columns=["_original", "size_mb"], inplace=True)
    df.sort_values("gb_per_eur", ascending=False, inplace=True)
    os.makedirs(output_dir, exist_ok=True)
    log.info("Writing data...")
    df.to_csv(os.path.join(output_dir, "data.csv"))
    df.to_json(os.path.join(output_dir, "data.json"), orient="records")
    df.to_html(os.path.join(output_dir, "data.html"), index=False)
    log.info("Writing showy HTML...")
    write_html(os.path.join(output_dir, "index.html"), df)
    log.info("All done here.")
