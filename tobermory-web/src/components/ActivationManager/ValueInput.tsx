import React from 'react';
import { Calendar } from 'lucide-react';
import { VariableMetadata } from './data/variableMetadata';

interface ValueInputProps {
  value: any;
  onChange: (value: any) => void;
  variable: VariableMetadata | null;
  operator: string;
  className?: string;
}

export function ValueInput({ value, onChange, variable, operator, className }: ValueInputProps) {
  if (!variable) {
    return (
      <input
        type="text"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        className={className || "input-field"}
        placeholder="Select a variable first"
        disabled
      />
    );
  }

  // Handle 'between' operator - needs two values
  if (operator === 'between') {
    const [min, max] = Array.isArray(value) ? value : ['', ''];
    return (
      <div className="flex gap-2 items-center">
        <input
          type={variable.dataType === 'number' ? 'number' : 'text'}
          value={min}
          onChange={(e) => onChange([e.target.value, max])}
          className={className || "input-field"}
          placeholder="Min"
        />
        <span className="text-gray-500">to</span>
        <input
          type={variable.dataType === 'number' ? 'number' : 'text'}
          value={max}
          onChange={(e) => onChange([min, e.target.value])}
          className={className || "input-field"}
          placeholder="Max"
        />
      </div>
    );
  }

  // Handle 'in' or 'not_in' operators - multiple values
  if (operator === 'in' || operator === 'not_in' || operator === 'contains' || operator === 'not_contains') {
    const values = Array.isArray(value) ? value : [];
    
    // If variable has examples, show as checkboxes
    if (variable.examples && variable.examples.length > 0) {
      return (
        <div className="space-y-2">
          {variable.examples.map((example) => (
            <label key={example} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={values.includes(example)}
                onChange={(e) => {
                  if (e.target.checked) {
                    onChange([...values, example]);
                  } else {
                    onChange(values.filter(v => v !== example));
                  }
                }}
                className="w-4 h-4 text-primary rounded focus:ring-primary"
              />
              <span className="text-sm text-gray-700">{example}</span>
            </label>
          ))}
        </div>
      );
    }

    // Otherwise show as comma-separated input
    return (
      <input
        type="text"
        value={values.join(', ')}
        onChange={(e) => onChange(e.target.value.split(',').map(v => v.trim()).filter(Boolean))}
        className={className || "input-field"}
        placeholder="Enter values separated by commas"
      />
    );
  }

  // Handle boolean type
  if (variable.dataType === 'boolean') {
    return (
      <select
        value={value || ''}
        onChange={(e) => onChange(e.target.value === 'true')}
        className={className || "input-field"}
      >
        <option value="">Select value</option>
        <option value="true">True</option>
        <option value="false">False</option>
      </select>
    );
  }

  // Handle date type
  if (variable.dataType === 'date') {
    return (
      <div className="relative">
        <input
          type="date"
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          className={className || "input-field pr-10"}
        />
        <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none" size={20} />
      </div>
    );
  }

  // Handle string type with examples
  if (variable.dataType === 'string' && variable.examples && variable.examples.length > 0) {
    return (
      <select
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        className={className || "input-field"}
      >
        <option value="">Select value</option>
        {variable.examples.map((example) => (
          <option key={example} value={example}>
            {example}
          </option>
        ))}
        <option value="__custom__">Other (Custom)</option>
      </select>
    );
  }

  // Default: text or number input
  return (
    <input
      type={variable.dataType === 'number' ? 'number' : 'text'}
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      className={className || "input-field"}
      placeholder={`Enter ${variable.dataType === 'number' ? 'number' : 'value'}`}
    />
  );
}