import React from 'react';
import type { PresetParameter } from './types';

interface Props {
  parameter: PresetParameter;
  value: boolean | number | string;
  onChange: (id: string, v: boolean | number | string) => void;
}

export default function ParameterInput({ parameter, value, onChange }: Props) {
  const currentValue = value ?? parameter.default;

  if (parameter.type === 'boolean') {
    return (
      <label className="toggle-row">
        <span>{parameter.label}</span>
        <input
          checked={Boolean(currentValue)}
          onChange={(event) => onChange(parameter.id, event.target.checked)}
          type="checkbox"
        />
      </label>
    );
  }

  if (parameter.type === 'select') {
    return (
      <select value={String(currentValue)} onChange={(event) => onChange(parameter.id, event.target.value)}>
        {parameter.options?.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    );
  }

  if (parameter.type === 'color') {
    return (
      <input type="color" value={String(currentValue)} onChange={(event) => onChange(parameter.id, event.target.value)} />
    );
  }

  const min = parameter.min ?? 0;
  const max = parameter.max ?? 100;
  const step = parameter.step ?? (parameter.type === 'float' ? 0.1 : 1);

  return (
    <>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={Number(currentValue)}
        onChange={(event) => onChange(parameter.id, Number(event.target.value))}
      />
      <span className="range-value">{currentValue}</span>
    </>
  );
}
