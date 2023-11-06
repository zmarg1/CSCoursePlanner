// src/components/PlanHeader.tsx
import React, { useState } from 'react';

interface PlanHeaderProps {
  onAddClass: (className: string) => void; // A callback to handle adding the class
}

const PlanHeader: React.FC<PlanHeaderProps> = ({ onAddClass }) => {
  const [className, setClassName] = useState('');

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onAddClass(className);
    setClassName(''); // Clear the input field after submission
  };

  return (
    <div className="plan-header">
      <h2>Plan Your Schedule</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={className}
          onChange={(e) => setClassName(e.target.value)}
          placeholder="Enter a class name"
          required
        />
        <button type="submit">Add Class</button>
      </form>
    </div>
  );
};

export default PlanHeader;
