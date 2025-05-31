import React from 'react';
import { operatorLabels } from '../data/variableMetadata';

interface OperatorSelectorProps {
  value: string;
  onChange: (operator: string) => void;
  availableOperators: string[];
  className?: string;
}

export function OperatorSelector({ value, onChange, availableOperators, className }: OperatorSelectorProps) {
  const operators = availableOperators || ['equals'];
  
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={className || "input-field"}
    >
      <option value="">Select operator</option>
      {operators.map((operator) => (
        <option key={operator} value={operator}>
          {operatorLabels[operator] || operator}
        </option>
      ))}
    </select>
  );
}