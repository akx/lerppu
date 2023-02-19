import React from "react";

export function MultiSelect({
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
