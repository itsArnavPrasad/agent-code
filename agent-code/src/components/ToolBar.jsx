// components/ToolBar.jsx
import React from 'react';

const Toolbar = ({ onRun, onRevert, onSave, currentFile }) => {
  return (
    <div style={{ 
      display: 'flex', 
      gap: '1rem', 
      marginBottom: '1rem',
      alignItems: 'center',
      padding: '0.5rem',
      backgroundColor: '#2d2d2d',
      borderRadius: '8px'
    }}>
      <button 
        onClick={onRun}
        style={{
          padding: '0.5rem 1rem',
          borderRadius: '4px',
          border: 'none',
          backgroundColor: '#4CAF50',
          color: 'white',
          cursor: 'pointer'
        }}
      >
        Run
      </button>
      
      <button 
        onClick={onRevert}
        style={{
          padding: '0.5rem 1rem',
          borderRadius: '4px',
          border: 'none',
          backgroundColor: '#ff9800',
          color: 'white',
          cursor: 'pointer'
        }}
      >
        Revert
      </button>

      <button 
        onClick={onSave}
        disabled={!currentFile}
        style={{
          padding: '0.5rem 1rem',
          borderRadius: '4px',
          border: 'none',
          backgroundColor: currentFile ? '#2196F3' : '#666',
          color: 'white',
          cursor: currentFile ? 'pointer' : 'not-allowed'
        }}
      >
        Save
      </button>
      
      {currentFile && (
        <div style={{ 
          marginLeft: 'auto',
          color: '#ccc',
          fontSize: '0.9rem',
          fontFamily: 'monospace'
        }}>
          📁 {currentFile}
        </div>
      )}
    </div>
  );
};

export default Toolbar;