// src/App.jsx
import { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [sliders, setSliders] = useState(null);
  const [loading, setLoading] = useState(false);

  const upload = async (returnXmp = false) => {
    if (!file) return;
    setLoading(true);

    const form = new FormData();
    form.append('image', file);

    const url = new URL('/predict', import.meta.env.VITE_API_URL);
    if (returnXmp) url.searchParams.set('return_xmp', '1');

    const res = await fetch(url, {
      method: 'POST',
      body: form
    });

    if (!res.ok) {
      alert(`Error: ${res.statusText}`);
      setLoading(false);
      return;
    }

    if (returnXmp) {
      const blob = await res.blob();
      const href = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = href;
      a.download = 'prediction.xmp';
      a.click();
    } else {
      const data = await res.json();
      setSliders(data);
    }

    setLoading(false);
  };

  return (
    <div className="app">
      <h1>LR-AI-Editor</h1>
      <input
        type="file"
        accept="image/*"
        onChange={e => setFile(e.target.files[0])}
      />

      <div className="buttons">
        <button onClick={() => upload(false)} disabled={!file || loading}>
          Predict JSON
        </button>
        <button onClick={() => upload(true)} disabled={!file || loading}>
          Download XMP
        </button>
      </div>

      {loading && <p>Processing…</p>}

      {sliders && (
        <pre className="sliders">
          {JSON.stringify(sliders, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default App;