import { HDProduct, HDProductEx } from "./types";
import useSWR from "swr";
import React from "react";

export function useLerppuData(): HDProductEx[] {
  const dataSWR = useSWR<HDProduct[]>("/data.json", (url: string) =>
    fetch(url).then((r) => r.json()),
  );
  const data: HDProductEx[] = React.useMemo(
    () =>
      (dataSWR.data || [])
        .filter((p) => p.size_tb)
        .map((p) => ({
          ...p,
          discount_pct: (1.0 - p.current_price / p.original_price) * 100,
        })),
    [dataSWR.data],
  );
  return data;
}
