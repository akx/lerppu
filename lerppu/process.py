import io
import logging
import os
import datetime
from itertools import chain

import httpx
import pandas as pd

from lerppu.sources import verk, jimms, proshop

log = logging.getLogger(__name__)

HTML_PRELUDE = """<html>
<head>
<meta charset="utf-8">
<style>
body {
font-family: sans-serif;
table {
max-width: 65em;
}
</style>
</head>
<body>"""

HTML_POSTLUDE = "</body></html>"


def write_html(html_filename, df: pd.DataFrame) -> None:
    sio = io.StringIO()
    df.to_html(sio, render_links=True)
    with open(html_filename, "w") as f:
        f.write(HTML_PRELUDE)
        now = datetime.datetime.utcnow().isoformat()
        f.write(f"Generated {now}; {len(df)} records<hr />")
        f.write(sio.getvalue())
        f.write(HTML_POSTLUDE)


def do_process(output_dir: str) -> None:
    log.info("Downloading information...")
    with httpx.Client() as sess:
        records = list(
            chain(
                verk.get_category_products(sess, category_id="3704c"),
                jimms.get_category_products(sess, category_id="000-0MU"),
                proshop.get_category_products(sess, category_id="Kovalevy"),
            )
        )
    log.info("Creating dataframe...")
    df = pd.DataFrame(records)
    df.set_index("id", inplace=True)
    df.drop(columns=["_original"], inplace=True)
    df["gb_per_eur"] = df["size_mb"] / df["current_price"] / 1024.0
    df.sort_values("gb_per_eur", ascending=False, inplace=True)
    os.makedirs(output_dir, exist_ok=True)
    log.info("Writing output...")
    df.to_csv(os.path.join(output_dir, "data.csv"))
    df.to_json(os.path.join(output_dir, "data.json"), orient="records")
    write_html(os.path.join(output_dir, "index.html"), df)
