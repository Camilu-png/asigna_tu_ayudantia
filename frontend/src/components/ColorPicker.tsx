import { useState } from 'react';
import { DEFAULT_COURSE_COLOR } from '../context/constants';

interface ColorPickerProps {
  value: string;
  onChange: (color: string) => void;
}

const PRESET_COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
  '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
  '#BB8FCE', '#85C1E9', '#F8B500', '#82E0AA',
  '#E74C3C', '#3498DB', '#2ECC71', '#9B59B6',
  '#E67E22', '#1ABC9C', '#34495E', '#E91E63'
];

export default function ColorPicker({ value, onChange }: ColorPickerProps) {
  const [customColor, setCustomColor] = useState(value || DEFAULT_COURSE_COLOR);
  const [showCustom, setShowCustom] = useState(false);

  const handlePresetClick = (color: string) => {
    onChange(color);
    setCustomColor(color);
  };

  const handleCustomChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const color = e.target.value;
    setCustomColor(color);
    onChange(color);
  };

  return (
    <div className="color-picker">
      <div className="color-presets">
        {PRESET_COLORS.map((color) => (
          <button
            key={color}
            type="button"
            className={`color-swatch ${value === color ? 'selected' : ''}`}
            style={{ backgroundColor: color }}
            onClick={() => handlePresetClick(color)}
            aria-label={`Select color ${color}`}
          />
        ))}
      </div>
      <div className="color-custom">
        <button
          type="button"
          className="color-custom-toggle"
          onClick={() => setShowCustom(!showCustom)}
        >
          {showCustom ? 'Ocultar' : 'Color personalizado'}
        </button>
        {showCustom && (
          <div className="color-custom-input">
            <input
              type="color"
              value={customColor}
              onChange={handleCustomChange}
            />
            <input
              type="text"
              value={customColor}
              onChange={(e) => {
                const val = e.target.value;
                if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
                  setCustomColor(val);
                  onChange(val);
                }
              }}
              placeholder="#000000"
            />
          </div>
        )}
      </div>
    </div>
  );
}
