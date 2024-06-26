import logging
from collections.abc import Iterable
from itertools import count

import bs4
import httpx

from lerppu.inference.size import get_mb_size_from_name
from lerppu.inference.sku import infer_sku_from_name
from lerppu.inference.type import get_connection_type_from_data
from lerppu.inference.vendor import infer_vendor_from_name
from lerppu.models import ConnectionType, MediaType, Product

log = logging.getLogger(__name__)


def parse_eur(text: str) -> float:
    if text.endswith("€"):
        text = text[:-1]
    text = text.strip().replace(",", ".").replace("\xa0", "")
    return float(text)


def massage_proshop(
    prod_li: bs4.Tag,
    *,
    media_type: MediaType,
) -> Product:
    prod_a = prod_li.select_one("a")
    url = "https://proshop.fi" + prod_a.get("href")
    pid = prod_li.select_one("input[name=productId]")["value"]
    name = prod_li.select_one("h2").text
    description = prod_li.select_one(".truncate-overflow").text
    pre_div = prod_li.select_one("div.site-currency-pre")
    current_price = parse_eur(prod_li.select_one("span.site-currency-lg").text)
    original_price = parse_eur(pre_div.text) if pre_div else current_price
    vendor_sku = infer_sku_from_name(name) or ""
    manufacturer = infer_vendor_from_name(name)
    size = get_mb_size_from_name(name) or get_mb_size_from_name(description)
    connection_type = get_connection_type_from_data([name, description]) or ConnectionType.UNKNOWN
    return Product(
        media_type=media_type,
        connection_type=connection_type,
        id=f"proshop:{pid}",
        source="proshop",
        name=name,
        size_mb=size,
        original_price=original_price,
        current_price=current_price,
        url=url,
        vendor_sku=vendor_sku,
        manufacturer=manufacturer,
        _original={"html": prod_li.prettify()},
    )


def get_category_products(
    cli: httpx.Client,
    *,
    category_id: str,
    media_type: MediaType,
) -> Iterable[Product]:
    for page_no in count(1):
        log.info(f"Fetching page {page_no} of category {category_id}")
        resp = cli.get(
            url=f"https://www.proshop.fi/{category_id}?o=1028",
            params={
                "o": "1152",  # alpha order
                "pn": page_no,
            },
        )
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            if "Enable JavaScript and cookies to continue" in resp.text:
                e.add_note("(Smells like a Cloudflare challenge.)")
            raise
        soup = bs4.BeautifulSoup(resp.content, "html.parser")
        product_lis = list(soup.select("ul#products > li"))
        if not product_lis:
            break
        for prod in product_lis:
            yield massage_proshop(prod, media_type=media_type)
