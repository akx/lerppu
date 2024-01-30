import logging
import os
from typing import Any

import pandas as pd

from lerppu.download import download_product_info
from lerppu.html_output import write_html
from lerppu.models import Product

log = logging.getLogger(__name__)


def get_value(x: Any) -> Any:
    return x.value if x else None


def create_dataframe(products: list[Product]) -> pd.DataFrame:
    log.info("Creating dataframe...")
    df = pd.DataFrame(products)
    df["gb_per_eur"] = (df["size_mb"] / df["current_price"] / 1024.0).round(3)
    df["discount"] = (df["original_price"] - df["current_price"]).round(2)
    df["size_tb"] = (df["size_mb"] / 1024 / 1024).round(2)
    df["eur_per_tb"] = (df["current_price"] / df["size_tb"]).round(3)
    df["connection_type"] = df["connection_type"].apply(get_value)
    df["media_type"] = df["media_type"].apply(get_value)
    df.drop(columns=["_original", "size_mb"], inplace=True)
    df.drop_duplicates(subset="id", keep="first", inplace=True)
    df.sort_values("gb_per_eur", ascending=False, inplace=True)
    return df


def do_process(output_dir: str, use_cache: bool) -> None:
    products, warnings = download_product_info(use_cache=use_cache)
    df = create_dataframe(products)
    os.makedirs(output_dir, exist_ok=True)
    log.info("Writing data...")
    df.to_csv(os.path.join(output_dir, "data.csv"), index=False)
    df.to_json(os.path.join(output_dir, "data.json"), orient="records")
    log.info("Writing showy HTML...")
    write_html(os.path.join(output_dir, "index.html"), df, warnings=warnings)
    log.info("All done here.")
