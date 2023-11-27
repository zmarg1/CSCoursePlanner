import React, { useState } from 'react';
import { SmallerStyledButton } from '../Button/styles';

// Define a type for the props
type RenamePlanModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onRename: (newName: string) => void;
};

const RenamePlanModal: React.FC<RenamePlanModalProps> = ({ isOpen, onClose, onRename }) => {
  const [newPlanName, setNewPlanName] = useState<string>('');

  const handleRename = () => {
    onRename(newPlanName); // Pass the new name to the parent component for processing
    setNewPlanName(''); // Reset the input field
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <img src="/img/Retriever_clipart.png" alt="Left Side" className="modal-side-image" />
        <div className="modal-content">
          <p>Enter new plan name:</p>
          <input 
            type="text"
            placeholder="New plan name"
            value={newPlanName}
            onChange={(e) => setNewPlanName(e.target.value)}
          />
          <SmallerStyledButton color="#fdb515" onClick={handleRename}>Confirm</SmallerStyledButton>
          <SmallerStyledButton color="#fdb515" onClick={onClose}>Cancel</SmallerStyledButton>
        </div>
        <img src="/img/Retriever_clipart.png" alt="Right Side" className="modal-side-image" />
      </div>
    </div>
  );
};

export default RenamePlanModal;
