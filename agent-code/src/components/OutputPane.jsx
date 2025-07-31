// OutputPane.jsx
import React from 'react';

const OutputPane = ({ output }) => {
  return (
    <div
      style={{
        backgroundColor: '#1e1e1e',
        color: 'white',
        padding: '1rem',
        marginTop: '1rem',
        height: '200px',
        overflowY: 'auto',
        fontFamily: 'monospace',
        borderRadius: '8px'
      }}
    >
      <pre>{output}</pre> 
    </div>
  );
};

export default OutputPane;
