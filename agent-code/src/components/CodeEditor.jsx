import React from 'react';
import Editor from '@monaco-editor/react';

const CodeEditor = ({ code, setCode }) => {
  return (
    <Editor
      height="300px"
      defaultLanguage="python"
      value={code}
      onChange={(value) => setCode(value)}
      theme="vs-dark"
    />
  );
};

export default CodeEditor;
