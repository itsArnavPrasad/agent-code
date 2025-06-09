import React from 'react';

const Toolbar = ({ onRun }) => {
  return (
    <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
      <button onClick={onRun}>Run</button>
      <button disabled>Agent (Coming soon)</button>
    </div>
  );
};

export default Toolbar;
