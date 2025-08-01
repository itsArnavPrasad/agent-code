// App.jsx
import React, { useState } from 'react';
import CodeEditor from './components/CodeEditor';
import OutputPane from './components/OutputPane';
import Toolbar from './components/ToolBar';
import FolderStructure from './components/FolderStructure';
import { runPythonCode, loadPyodideInstance } from './utils/pyodideRunner';
import ChatInterface from './components/ChatInterface';

const App = () => {
  const [code, setCode] = useState('# Write your Python code here');
  const [previousCode, setPreviousCode] = useState('');
  const [output, setOutput] = useState('');
  const [messages, setMessages] = useState([]);
  const [currentFile, setCurrentFile] = useState('');
  const [codebaseDir, setCodebaseDir] = useState('');

  const handleRun = async () => {
    await loadPyodideInstance();
    const result = await runPythonCode(code);
    setOutput(result);
  };

  const handleFileSelect = (fileContent, filePath) => {
    setPreviousCode(code); // Save current code before switching
    setCode(fileContent);
    setCurrentFile(filePath);
    
    // Extract directory from file path
    const dir = filePath.substring(0, filePath.lastIndexOf('/'));
    setCodebaseDir(dir);
  };

  const handleSave = async () => {
    if (!currentFile) {
      alert('No file selected to save');
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/save-file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          file_path: currentFile,
          content: code
        })
      });

      const data = await res.json();
      if (res.ok) {
        setOutput(`${data.message}`);
      } else {
        setOutput(`Error: ${data.detail}`);
      }
    } catch (err) {
      console.error('Save failed:', err);
      setOutput(`Save failed: ${err.message}`);
    }
  };

  const handleAgentSend = async (task, updatedMessages) => {
    try {
      setPreviousCode(code);

      const res = await fetch('http://localhost:8000/run-developer-agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          current_code: code, 
          task,
          current_file: currentFile,
          codebase_dir: codebaseDir
        })
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }

      const data = await res.json();
      console.log('Agent response:', data); // Debug log
      
      setCode(data.new_code || code); // Fallback to current code if new_code is undefined

      // Add agent logs as message(s) - ensure logs is an array
      const logs = Array.isArray(data.logs) ? data.logs : (data.logs ? [data.logs] : ["Task completed"]);
      const logText = logs.join('\n');
      const newAgentMsg = { role: "agent", content: logText };
      setMessages([...updatedMessages, newAgentMsg]);

    } catch (err) {
      console.error('Agent call failed:', err);
      const errorMsg = { role: "agent", content: `Error: ${err.message}` };
      setMessages([...updatedMessages, errorMsg]);
    }
  };

  return (
    <div style={{ padding: '5rem 8rem', margin: '0 auto', background: 'black'}}>
      <h1 style={{ color: 'white'}}>AgentCode</h1>
      
      <FolderStructure 
        onFileSelect={handleFileSelect}
        currentFile={currentFile}
      />
      
      <Toolbar 
        onRun={handleRun} 
        onRevert={() => setCode(previousCode)}
        onSave={handleSave}
        currentFile={currentFile}
      />
      
      <CodeEditor code={code} setCode={setCode} />
      <OutputPane output={output} />
      
      <ChatInterface
        onSend={handleAgentSend}
        messages={messages}
        setMessages={setMessages}
      />
    </div>
  );
};

export default App;