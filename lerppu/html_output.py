import datetime
import io

import pandas as pd
import plotly.express as px

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@100..900&display=swap');

:root {
    --color-neon-carrot-50: #fff8ed;
    --color-neon-carrot-100: #ffefd5;
    --color-neon-carrot-200: #fedaaa;
    --color-neon-carrot-300: #fcbf75;
    --color-neon-carrot-400: #fa983a;
    --color-neon-carrot-500: #f87c17;
    --color-neon-carrot-600: #e9610d;
    --color-neon-carrot-700: #c1480d;
    --color-neon-carrot-800: #993913;
    --color-neon-carrot-900: #7b3113;
    --color-neon-carrot-950: #431607;
}

body, td, th {
    font: 10pt Geist, sans-serif;
}

body {
    margin: 0;
}

header {
    background-color: var(--color-neon-carrot-200);
    border-bottom: 1px solid var(--color-neon-carrot-400);
    padding: 0.5em;
    text-align: center;
}

main {
    margin: 1em;
}

details {
    margin-bottom: 1em;
    border: 1px solid var(--color-neon-carrot-200);
    padding: 0.5em;
}

details summary {
    font-weight: bold;
    cursor: pointer;
}

#plot {
    max-width: 800px;
    max-height: 600px;
}

table {
    border-collapse: collapse;
}

td, th {
    border: 1px solid #ddd;
}

tbody tr:nth-child(even) td {
    background-color: var(--color-neon-carrot-50) !important;
}

tr td {
    padding: 2px 4px !important;
}

tbody tr:hover td {
    background-color: var(--color-neon-carrot-100) !important;
}
"""

JS = """
new DataTable('#data', {paging: false, columnControl: {
    target: 1,
    content: ['search']
}});
"""

HTML_PRELUDE = f"""<html>
<head>
<meta charset="utf-8">
<style>{CSS.strip()}</style>
<link href="https://cdn.datatables.net/v/dt/jq-3.7.0/dt-2.3.3/cc-1.0.7/datatables.min.css" rel="stylesheet" integrity="sha384-irWStpildAd5P04Z1UAYGgYW54WanodOP8m5M7rvGNlztlz5/mD1E5Qq7Rww3mol" crossorigin="anonymous">
<script src="https://cdn.datatables.net/v/dt/jq-3.7.0/dt-2.3.3/cc-1.0.7/datatables.min.js" integrity="sha384-k0qOqleC3UpZBpt4N0rSCMnK6IG8eznW2RLUB73y4zcvyDKjouzOr7HXENiS5aK+" crossorigin="anonymous"></script>
<body>"""  # noqa: E501
HTML_POSTLUDE = f"""<script>{JS.strip()}</script></body></html>"""


def get_plot_html(df: pd.DataFrame) -> str:
    # Don't plot products that are clearly way out of the usual price range
    culled_df = df[df["current_price"] < df["current_price"].median() * 3]
    fig = px.scatter(culled_df, x="current_price", y="size_tb", hover_name="id", color="manufacturer")
    return fig.to_html(
        full_html=False,
        default_width="",
        default_height="",
        include_plotlyjs="cdn",
    )


def get_table_html(df: pd.DataFrame) -> str:
    sio = io.StringIO()
    df.to_html(
        sio,
        table_id="data",
        render_links=True,
        index=False,
        border=0,
        columns=[
            "id",
            "vendor_sku",
            "manufacturer",
            "name",
            "size_tb",
            "connection_type",
            "media_type",
            "url",
            "original_price",
            "current_price",
            "discount",
            "gb_per_eur",
            "eur_per_tb",
        ],
    )
    return sio.getvalue()


def write_html(html_filename: str, df: pd.DataFrame, *, warnings: list[str]) -> None:
    table_html = get_table_html(df)
    plot_html = get_plot_html(df)

    with open(html_filename, "w") as f:
        f.write(HTML_PRELUDE)
        now = datetime.datetime.now(datetime.UTC).isoformat()
        f.write(
            f"<header>"
            f"Generated {now}; {len(df)} records. "
            f'Also see <a href="data.csv">data.csv</a> / '
            f'<a href="data.json">data.json</a>'
        )
        if warnings:
            f.write("<div class='warnings'>Warnings:<ul>")
            for warning in warnings:
                f.write(f"<li>{warning}</li>")
            f.write("</ul></div>")
        f.write("</header>")
        f.write("<main>")
        f.write("<details><summary>Price/size plot</summary>")
        f.write(f'<div id="plot">{plot_html}</div>')
        f.write("</details>")
        f.write(table_html)
        f.write("</main>")
        f.write(HTML_POSTLUDE)
