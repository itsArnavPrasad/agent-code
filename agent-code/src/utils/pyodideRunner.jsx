let pyodide = null;

export async function loadPyodideInstance() {
  if (!pyodide) {
    pyodide = await window.loadPyodide();
  }
}

export async function runPythonCode(code) {
  if (!pyodide) return 'Pyodide not loaded yet';

  try {
    // Redirect stdout
    let output = '';
    pyodide.setStdout({
      batched: (data) => {
        output += data + '\n';
      },
    });
    pyodide.setStderr({
      batched: (err) => {
        output += 'Error: ' + err + '\n';
      },
    });

    await pyodide.runPythonAsync(code);
    return output.trim(); // send stdout (including print) back
  } catch (err) {
    return `Exception: ${err.message}`;
  }
}
