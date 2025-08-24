import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const onFileChange = (e) => {
    setFile(e.target.files?.[0] ?? null)
  }

  const onUpload = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch('http://127.0.0.1:5000/api/upload', { method: 'POST', body: form })
      if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  // ✅ Export JSON
  const downloadJSON = async () => {
    if (!result) return
    const res = await fetch('http://127.0.0.1:5000/api/export/json', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result),
    })
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'sof_export.json'
    a.click()
  }

  // ✅ Export CSV
  const downloadCSV = async () => {
    if (!result) return
    const res = await fetch('http://127.0.0.1:5000/api/export/csv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result),
    })
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'sof_export.csv'
    a.click()
  }

  return (
    <div style={{ maxWidth: 640, margin: '2rem auto', fontFamily: 'system-ui' }}>
      <h2>SoF Event Extractor</h2>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={onFileChange} />
        <button onClick={onUpload} disabled={!file || loading}>
          {loading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {result && (
        <>
          <pre
  style={{
    background: '#1e1e1e',
    color: '#f8f8f2',
    padding: 12,
    borderRadius: 8,
    marginTop: 16,
    maxHeight: 300,
    overflow: 'auto',
    fontSize: '14px'
  }}
>
  {JSON.stringify(result, null, 2)}
</pre>

          <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
            <button onClick={downloadJSON}>Download JSON</button>
            <button onClick={downloadCSV}>Download CSV</button>
          </div>
        </>
      )}
    </div>
  )
}

export default App
