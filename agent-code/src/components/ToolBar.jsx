// ToolBar.jsx
import React from 'react';

const Toolbar = ({ onRun, onRevert }) => {
  return (
    <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
      <button onClick={onRun}>Run</button>
      <button onClick={onRevert}>Revert</button>
    </div>
  );
};

export default Toolbar;
