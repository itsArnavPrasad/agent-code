// App.jsx
import React, { useState } from 'react';
import CodeEditor from './components/CodeEditor';
import OutputPane from './components/OutputPane';
import Toolbar from './components/ToolBar';
import { runPythonCode, loadPyodideInstance } from './utils/pyodideRunner';
import ChatInterface from './components/ChatInterface';

const App = () => {
  const [code, setCode] = useState('# Write your Python code here');
  const [previousCode, setPreviousCode] = useState('');
  const [output, setOutput] = useState('');
  const [messages, setMessages] = useState([]); // NEW

  const handleRun = async () => {
    await loadPyodideInstance();
    const result = await runPythonCode(code);
    setOutput(result);
  };

  const handleAgentSend = async (task, updatedMessages) => {
    try {
      setPreviousCode(code);

      const res = await fetch('http://localhost:8000/run-developer-agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_code: code, task })
      });

      const data = await res.json();
      setCode(data.new_code);

      // Add agent logs as message(s)
      const logText = data.logs.join('\n');
      const newAgentMsg = { role: "agent", content: logText };
      setMessages([...updatedMessages, newAgentMsg]);

    } catch (err) {
      console.error('Agent call failed:', err);
    }
  };

  return (
    <div>
      <Toolbar onRun={handleRun} onRevert={() => setCode(previousCode)} />
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
