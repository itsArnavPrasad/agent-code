// components/FolderStructure.jsx
import React, { useState } from 'react';

const FolderStructure = ({ onFileSelect, currentFile }) => {
  const [directory, setDirectory] = useState('');
  const [structure, setStructure] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGetStructure = async () => {
    if (!directory.trim()) return;
    
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/get-folder-structure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory })
      });
      
      const data = await res.json();
      setStructure(data.structure);
    } catch (err) {
      console.error('Failed to get folder structure:', err);
      setStructure('Error loading folder structure');
    }
    setLoading(false);
  };

  const parseFilesFromStructure = (structureText) => {
    if (!structureText) return [];
    
    const lines = structureText.split('\n');
    const files = [];
    
    lines.forEach(line => {
      // Look for lines that contain file paths (with extensions)
      const match = line.match(/^([^\s].*\.(py|js|jsx|ts|tsx|java|cpp|c|h|txt|md|json|html|css))\s+/);
      if (match) {
        const filePath = match[1].trim();
        files.push(filePath);
      }
    });
    
    return files;
  };

  const handleFileClick = async (fileName) => {
    const fullPath = directory.endsWith('/') ? directory + fileName : directory + '/' + fileName;
    
    try {
      const res = await fetch('http://localhost:8000/get-file-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: fullPath })
      });
      
      const data = await res.json();
      
      // Extract just the code content (remove the header and formatting)
      const content = data.content;
      const lines = content.split('\n');
      
      // Find where the actual code starts (after the === line)
      let codeStartIndex = 0;
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes('===')) {
          codeStartIndex = i + 1;
          break;
        }
      }
      
      // Extract code lines (remove line numbers)
      const codeLines = lines.slice(codeStartIndex).map(line => {
        // Remove line numbers (pattern: "   1: " or "  10: " etc.)
        return line.replace(/^\s*\d+:\s/, '');
      });
      
      const cleanCode = codeLines.join('\n');
      
      onFileSelect(cleanCode, fullPath);
    } catch (err) {
      console.error('Failed to load file:', err);
    }
  };

  const files = parseFilesFromStructure(structure);

  return (
    <div style={{ 
      backgroundColor: '#2d2d2d', 
      padding: '1rem', 
      borderRadius: '8px', 
      marginBottom: '1rem',
      color: 'white'
    }}>
      <h3>Folder Structure</h3>
      
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <input
          type="text"
          value={directory}
          placeholder="Enter directory path (e.g., ./my-project)"
          onChange={(e) => setDirectory(e.target.value)}
          style={{ 
            flexGrow: 1, 
            padding: '0.5rem', 
            borderRadius: '4px', 
            border: '1px solid #555',
            backgroundColor: '#1e1e1e',
            color: 'white'
          }}
        />
        <button 
          onClick={handleGetStructure}
          disabled={loading}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            border: 'none',
            backgroundColor: '#007acc',
            color: 'white',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Loading...' : 'Load'}
        </button>
      </div>

      {files.length > 0 && (
        <div>
          <h4>Files:</h4>
          <div style={{ 
            maxHeight: '200px', 
            overflowY: 'auto',
            backgroundColor: '#1e1e1e',
            padding: '0.5rem',
            borderRadius: '4px'
          }}>
            {files.map((file, idx) => (
              <div 
                key={idx}
                onClick={() => handleFileClick(file)}
                style={{
                  padding: '0.25rem 0.5rem',
                  cursor: 'pointer',
                  borderRadius: '3px',
                  marginBottom: '2px',
                  backgroundColor: currentFile === (directory + '/' + file) ? '#007acc' : 'transparent',
                  ':hover': { backgroundColor: '#404040' }
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = currentFile === (directory + '/' + file) ? '#007acc' : '#404040'}
                onMouseLeave={(e) => e.target.style.backgroundColor = currentFile === (directory + '/' + file) ? '#007acc' : 'transparent'}
              >
                📄 {file}
              </div>
            ))}
          </div>
        </div>
      )}

      {structure && files.length === 0 && (
        <div style={{ 
          fontSize: '0.9rem', 
          color: '#888',
          backgroundColor: '#1e1e1e',
          padding: '0.5rem',
          borderRadius: '4px',
          maxHeight: '150px',
          overflowY: 'auto'
        }}>
          <pre>{structure}</pre>
        </div>
      )}
    </div>
  );
};

export default FolderStructure;