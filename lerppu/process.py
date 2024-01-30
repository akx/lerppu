import logging
import os
from collections.abc import Iterable
from itertools import chain
from typing import Any

import diskcache
import httpx
import pandas as pd

from lerppu.caching_http_transport import CachingHTTPTransport
from lerppu.html_output import write_html
from lerppu.models import ConnectionType, MediaType, Product
from lerppu.sources import dustinhome, jimms, proshop, verk
from lerppu.validation import validate_product

log = logging.getLogger(__name__)


def get_sources(sess: httpx.Client) -> Iterable[Iterable[Product]]:
    return [
        verk.get_category_products(
            sess,
            base_filter="category:hard_disk_drives",
            connection_type=ConnectionType.SATA,
            media_type=MediaType.HDD,
        ),
        verk.get_category_products(
            sess,
            base_filter="category:ssd_drives",
            connection_type=ConnectionType.SATA,
            media_type=MediaType.SSD,
        ),
        verk.get_category_products(
            sess,
            base_filter="category:m2_ssd",
            connection_type=ConnectionType.M2,
            media_type=MediaType.SSD,
        ),
        jimms.get_category_products(
            sess,
            category_id="000-0MU",
            connection_type=ConnectionType.SATA,
            media_type=MediaType.HDD,
        ),
        jimms.get_category_products(
            sess,
            category_id="000-0EE",
            connection_type=ConnectionType.SATA,
            media_type=MediaType.SSD,
        ),
        jimms.get_category_products(
            sess,
            category_id="000-1AR",
            connection_type=ConnectionType.M2,
            media_type=MediaType.SSD,
        ),
        proshop.get_category_products(
            sess,
            category_id="Kovalevy",
            media_type=MediaType.HDD,
        ),
        proshop.get_category_products(
            sess,
            category_id="SSD",
            media_type=MediaType.SSD,
        ),
        dustinhome.get_category_products(
            sess,
            category_id="2030994",
            media_type=MediaType.HDD,
        ),
        dustinhome.get_category_products(
            sess,
            category_id="2032014",
            media_type=MediaType.SSD,
        ),
    ]


def get_value(x: Any) -> Any:
    return x.value if x else None


def do_process(output_dir: str, use_cache: bool) -> None:
    log.info("Downloading information...")
    transport = (
        CachingHTTPTransport(cache=diskcache.Cache("./cache", disk_min_file_size=1048576)) if use_cache else None
    )
    headers = {
        "User-Agent": f"{httpx._client.USER_AGENT} (+https://akx.github.io/lerppu/)",
    }
    with httpx.Client(transport=transport, headers=headers) as sess:
        products = [prod for prod in chain(*get_sources(sess)) if validate_product(prod)]

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
    os.makedirs(output_dir, exist_ok=True)
    log.info("Writing data...")
    df.to_csv(os.path.join(output_dir, "data.csv"), index=False)
    df.to_json(os.path.join(output_dir, "data.json"), orient="records")
    log.info("Writing showy HTML...")
    write_html(os.path.join(output_dir, "index.html"), df)
    log.info("All done here.")
