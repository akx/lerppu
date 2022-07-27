import datetime
import io

import plotly.express as px
import pandas as pd

HTML_PRELUDE = """<html>
<head>
<meta charset="utf-8">
<style>
body, td, th {
font: 10pt sans-serif;
}
table {
  border-collapse: collapse;
}
td, th {
    border: 1px solid #ddd;
}
tr:nth-child(even) td {
    background-color: #eff;
}
tr:hover td {
    background-color: #dee !important;
}
</style>
</head>
<body>"""
HTML_POSTLUDE = "</body></html>"


def get_plot_html(df) -> str:
    df["size_tb"] = (df["size_mb"] / 1024 / 1024).round(2)
    # Don't plot products that are clearly way out of the usual price range
    culled_df = df[df["current_price"] < df["current_price"].median() * 3]
    fig = px.scatter(
        culled_df, x="current_price", y="size_tb", hover_name="id", color="manufacturer"
    )
    return fig.to_html(full_html=False, default_width="50%", default_height="50%")


def get_table_html(df) -> str:
    sio = io.StringIO()
    df.to_html(sio, render_links=True, border=0)
    return sio.getvalue()


def write_html(html_filename, df: pd.DataFrame) -> None:
    table_html = get_table_html(df)
    plot_html = get_plot_html(df)

    with open(html_filename, "w") as f:
        f.write(HTML_PRELUDE)
        now = datetime.datetime.utcnow().isoformat()
        f.write(
            f"Generated {now}; {len(df)} records. "
            f'Also see <a href="data.csv">data.csv</a> '
            f'and <a href="data.json">data.json</a>'
        )
        f.write("<hr />")
        f.write(plot_html)
        f.write(f"<hr />")
        f.write(table_html)
        f.write(HTML_POSTLUDE)