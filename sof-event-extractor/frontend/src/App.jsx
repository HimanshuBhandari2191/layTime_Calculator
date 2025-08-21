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
      const res = await fetch('/api/upload', { method: 'POST', body: form })
      if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 640, margin: '2rem auto', fontFamily: 'system-ui' }}>
      <h2>SoF Event Extractor</h2>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <input type="file" accept=".pdf,.doc,.docx" onChange={onFileChange} />
        <button onClick={onUpload} disabled={!file || loading}>
          {loading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {result && (
        <pre style={{ background: '#f6f8fa', padding: 12, borderRadius: 8, marginTop: 16 }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  )
}

export default App
