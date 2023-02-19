import { connectionTypeNames, mediaTypeNames } from "../consts";
import React from "react";
import { HDProductEx } from "../types";

const DataTableRow = React.memo(function DataTableRow({
  product,
}: {
  product: HDProductEx;
}) {
  const {
    connection_type,
    current_price,
    discount,
    discount_pct,
    eur_per_tb,
    gb_per_eur,
    manufacturer,
    media_type,
    name,
    original_price,
    size_tb,
    url,
    vendor_sku,
  } = product;
  return (
    <tr>
      <td>{manufacturer}</td>
      <td>{vendor_sku}</td>
      <td>{name}</td>
      <td>{connectionTypeNames[connection_type] ?? connection_type}</td>
      <td>{mediaTypeNames[media_type] ?? media_type}</td>
      <td className="num">{size_tb}</td>
      <td className="num">{current_price.toFixed(2)}</td>
      <td className="num">{original_price.toFixed(2)}</td>
      <td className="num">{discount != 0 ? discount : ""}</td>
      <td className="num">
        {discount != 0 ? discount_pct.toFixed(2) + "%" : ""}
      </td>
      <td className="num">{eur_per_tb ? eur_per_tb.toFixed(3) : ""}</td>
      <td className="num">{gb_per_eur.toFixed(3)}</td>
      <td>
        <a href={url}>{url}</a>
      </td>
    </tr>
  );
});

export default function DataTable({
  sortedData,
}: {
  sortedData: readonly HDProductEx[];
}) {
  return (
    <table className="data">
      <thead>
        <tr>
          <th>Manufacturer</th>
          <th>SKU</th>
          <th>Name</th>
          <th>Conn. Type</th>
          <th>Media Type</th>
          <th>Size (TB)</th>
          <th>Current Price</th>
          <th>Original Price</th>
          <th>Discount</th>
          <th>Discount%</th>
          <th>EUR per TB</th>
          <th>GB per EUR</th>
          <th>URL</th>
        </tr>
      </thead>
      <tbody>
        {sortedData.map((product) => (
          <DataTableRow product={product} key={product.id} />
        ))}
      </tbody>
    </table>
  );
}
