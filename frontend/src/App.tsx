import React from "react";
import useSWR from "swr";
import { HDProduct, HDProductEx } from "./types";
import { connectionTypeNames, mediaTypeNames } from "./consts";

const sortOptions = [
  "current_price",
  "discount",
  "discount_pct",
  "eur_per_tb",
  "original_price",
] as const;
type SortOption = typeof sortOptions[number];

function MultiSelect({
  options,
  selected,
  onChange,
  labels = {},
}: {
  options: string[];
  selected: readonly string[];
  onChange: (selected: string[]) => void;
  labels?: Record<string, string>;
}) {
  return (
    <>
      <select
        multiple
        size={options.length}
        onChange={(event) => {
          onChange(
            Array.from(event.target.selectedOptions, (option) => option.value),
          );
        }}
        value={selected}
      >
        {options.map((value) => (
          <option key={value} value={value}>
            {labels[value] ?? value}
          </option>
        ))}
      </select>
      <br />
      <button onClick={() => onChange([])}>Clear</button>
    </>
  );
}

function useLerppuData(): HDProductEx[] {
  const dataSWR = useSWR<HDProduct[]>("/data.json", (url: string) =>
    fetch(url).then((r) => r.json()),
  );
  const data: HDProductEx[] = React.useMemo(
    () =>
      (dataSWR.data || []).map((p) => ({
        ...p,
        discount_pct: (1.0 - p.current_price / p.original_price) * 100,
      })),
    [dataSWR.data],
  );
  return data;
}

function App() {
  const data = useLerppuData();
  const manufacturers = new Set(
    data.map(({ manufacturer }) => manufacturer).filter((m) => m),
  );
  const sources = new Set(data.map(({ source }) => source).filter((s) => s));
  const connectionTypes = new Set(
    data.map(({ connection_type }) => connection_type).filter((s) => s),
  );
  const mediaTypes = new Set(
    data.map(({ media_type }) => media_type).filter((s) => s),
  );
  // const maxSizeTb = Math.max(...data.map(({ size_tb }) => size_tb)) ?? 40;
  const [selectedManufacturers, setSelectedManufacturers] = React.useState<
    string[]
  >([]);
  const [selectedSources, setSelectedSources] = React.useState<string[]>([]);
  const [selectedConnectionTypes, setSelectedConnectionTypes] = React.useState<
    string[]
  >([]);
  const [selectedMediaTypes, setSelectedMediaTypes] = React.useState<string[]>(
    [],
  );
  const [minSize, setMinSize] = React.useState<number>(0);
  const [maxSize, setMaxSize] = React.useState<number | undefined>();
  const [minPrice, setMinPrice] = React.useState<number>(0);
  const [maxPrice, setMaxPrice] = React.useState<number | undefined>();
  const [sortBy, setSortBy] = React.useState<SortOption>("eur_per_tb");
  const [reverseSort, setReverseSort] = React.useState<boolean>(false);

  const filteredData = React.useMemo(() => {
    return data.filter(
      ({
        manufacturer,
        source,
        connection_type,
        media_type,
        size_tb,
        current_price,
      }) => {
        if (
          selectedManufacturers.length &&
          !selectedManufacturers.includes(manufacturer)
        ) {
          return false;
        }
        if (selectedSources.length && !selectedSources.includes(source)) {
          return false;
        }
        if (
          selectedConnectionTypes.length &&
          !selectedConnectionTypes.includes(connection_type)
        ) {
          return false;
        }
        if (
          selectedMediaTypes.length &&
          !selectedMediaTypes.includes(media_type)
        ) {
          return false;
        }
        if (size_tb < minSize) {
          return false;
        }
        if (maxSize && size_tb > maxSize) {
          return false;
        }
        if (current_price < minPrice) {
          return false;
        }
        if (maxPrice && current_price > maxPrice) {
          return false;
        }
        return true;
      },
    );
  }, [
    data,
    maxPrice,
    maxSize,
    minPrice,
    minSize,
    selectedConnectionTypes,
    selectedManufacturers,
    selectedMediaTypes,
    selectedSources,
  ]);
  const sortedData = React.useMemo(() => {
    const sortFn = (a: HDProductEx, b: HDProductEx) => {
      if (a[sortBy] < b[sortBy]) {
        return -1;
      } else if (a[sortBy] > b[sortBy]) {
        return 1;
      } else {
        return a.id.localeCompare(b.id);
      }
    };
    const sortedData = filteredData.sort(sortFn);
    if (reverseSort) {
      sortedData.reverse();
    }
    return sortedData;
  }, [filteredData, sortBy, reverseSort]);

  return (
    <div className="App">
      <table>
        <tbody>
          <tr>
            <td>
              Manufacturers
              <br />
              <MultiSelect
                options={Array.from(manufacturers).sort()}
                onChange={setSelectedManufacturers}
                selected={selectedManufacturers}
              />
            </td>
            <td>
              Sources
              <br />
              <MultiSelect
                options={Array.from(sources).sort()}
                onChange={setSelectedSources}
                selected={selectedSources}
              />
            </td>
            <td>
              Media Types
              <br />
              <MultiSelect
                options={Array.from(mediaTypes).sort()}
                onChange={setSelectedMediaTypes}
                selected={selectedMediaTypes}
                labels={mediaTypeNames}
              />
            </td>
            <td>
              Connection Types
              <br />
              <MultiSelect
                options={Array.from(connectionTypes).sort()}
                onChange={setSelectedConnectionTypes}
                selected={selectedConnectionTypes}
                labels={connectionTypeNames}
              />
            </td>
            <td>
              Size (TB)
              <br />
              <input
                type="number"
                min="0"
                value={minSize}
                onChange={(e) => setMinSize(e.target.valueAsNumber)}
              />
              to
              <input
                type="number"
                min="0"
                value={maxSize}
                onChange={(e) =>
                  e.target.value
                    ? setMaxSize(e.target.valueAsNumber)
                    : undefined
                }
              />
            </td>
            <td>
              Price
              <br />
              <input
                type="number"
                min="0"
                size={5}
                value={minPrice}
                onChange={(e) => setMinPrice(e.target.valueAsNumber)}
              />
              to
              <input
                type="number"
                min="0"
                size={5}
                value={maxPrice}
                onChange={(e) =>
                  setMaxPrice(
                    e.target.value ? e.target.valueAsNumber : undefined,
                  )
                }
              />
            </td>
            <td>
              Sort by
              <br />
              <select
                size={sortOptions.length}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                value={sortBy}
              >
                {sortOptions.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
              <br />
              <label>
                <input
                  type="checkbox"
                  checked={reverseSort}
                  onChange={(e) => setReverseSort(e.target.checked)}
                />
                Reverse
              </label>
            </td>
          </tr>
        </tbody>
      </table>
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
          {sortedData.map(
            ({
              connection_type,
              current_price,
              discount,
              discount_pct,
              eur_per_tb,
              gb_per_eur,
              id,
              manufacturer,
              media_type,
              name,
              original_price,
              size_tb,
              url,
              vendor_sku,
            }) => (
              <tr key={id}>
                <td>{manufacturer}</td>
                <td>{vendor_sku}</td>
                <td>{name}</td>
                <td>
                  {connectionTypeNames[connection_type] ?? connection_type}
                </td>
                <td>{mediaTypeNames[media_type] ?? media_type}</td>
                <td className="num">{size_tb}</td>
                <td className="num">{current_price.toFixed(2)}</td>
                <td className="num">{original_price.toFixed(2)}</td>
                <td className="num">{discount != 0 ? discount : ""}</td>
                <td className="num">
                  {discount != 0 ? discount_pct.toFixed(2) + "%" : ""}
                </td>
                <td className="num">{eur_per_tb.toFixed(3)}</td>
                <td className="num">{gb_per_eur.toFixed(3)}</td>
                <td>
                  <a href={url}>{url}</a>
                </td>
              </tr>
            ),
          )}
        </tbody>
      </table>
    </div>
  );
}

export default App;
