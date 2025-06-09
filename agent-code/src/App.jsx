import React, { useState } from 'react';
import CodeEditor from './components/CodeEditor';
import OutputPane from './components/OutputPane';
import Toolbar from './components/ToolBar';
import { runPythonCode, loadPyodideInstance } from './utils/pyodideRunner';

const App = () => {
  const [code, setCode] = useState('# Write your Python code here');
  const [output, setOutput] = useState('');

  // Remove useEffect that loads Pyodide on mount

  const handleRun = async () => {
    // Ensure Pyodide is loaded before running code
    await loadPyodideInstance(); 
    const result = await runPythonCode(code);
    setOutput(result); 
  };  

  return (
    <div>
      <Toolbar onRun={handleRun} />
      <CodeEditor code={code} setCode={setCode} />
      <OutputPane output={output} /> 
    </div>
  );
};

export default App;
