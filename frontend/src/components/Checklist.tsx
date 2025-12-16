import React from 'react';

interface ChecklistProps {
  items: string[];
  title: string;
  checked?: boolean[];
  onToggle?: (index: number) => void;
}

const Checklist: React.FC<ChecklistProps> = ({ items, title, checked, onToggle }) => {
  return (
    <div className="checklist">
      <h3>{title}</h3>
      <ul className="checklist-items">
        {items.map((item, index) => (
          <li key={index} className="checklist-item">
            {onToggle ? (
              <label>
                <input
                  type="checkbox"
                  checked={checked?.[index] || false}
                  onChange={() => onToggle(index)}
                />
                <span>{item}</span>
              </label>
            ) : (
              <span>• {item}</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Checklist;
