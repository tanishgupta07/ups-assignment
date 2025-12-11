import { useState, useEffect } from 'react'

const TAGS = ["Finance Document", "Business Document", "Public Document"]

function Sidebar({ apiUrl, sessions, currentSessionId, onNewSession, onSelectSession, selectedTag, onTagChange }) {
  const [documents, setDocuments] = useState([])
  const [file, setFile] = useState(null)
  const [uploadTag, setUploadTag] = useState("Public Document")
  const [uploading, setUploading] = useState(false)
  const [confirmReembed, setConfirmReembed] = useState(null)

  const fetchDocuments = async () => {
    try {
      const res = await fetch(`${apiUrl}/ingest/documents`)
      if (res.ok) {
        const data = await res.json()
        setDocuments(data.documents || [])
      }
    } catch (err) {
      console.error('Failed to fetch documents', err)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [apiUrl])

  const handleUpload = async (force = false) => {
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const params = new URLSearchParams()
      params.append('tag', uploadTag)
      if (force) params.append('force', 'true')

      const res = await fetch(`${apiUrl}/ingest/upload?${params}`, {
        method: 'POST',
        body: formData
      })

      if (res.ok) {
        const data = await res.json()
        if (data.message === 'exists' && !force) {
          setConfirmReembed(file.name)
        } else {
          setFile(null)
          setConfirmReembed(null)
          fetchDocuments()
        }
      }
    } catch (err) {
      console.error('Upload failed', err)
    }

    setUploading(false)
  }

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setConfirmReembed(null)
  }

  const formatDate = (isoString) => {
    const date = new Date(isoString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <aside className="sidebar">
      {/* Sessions Section */}
      <div className="sessions-section">
        <div className="section-header">
          <h2>Chat Sessions</h2>
          <button className="new-session-btn" onClick={onNewSession}>+ New</button>
        </div>

        <div className="sessions-list">
          {sessions.length === 0 ? (
            <p className="no-items">No sessions yet</p>
          ) : (
            sessions.map(session => (
              <div
                key={session.id}
                className={`session-item ${currentSessionId === session.id ? 'active' : ''}`}
                onClick={() => onSelectSession(session.id)}
              >
                <div className="session-info">
                  <span className="session-date">{formatDate(session.created_at)}</span>
                  <span className="session-msgs">{session.message_count} messages</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <hr />

      {/* Filter Section */}
      <h2>Filter by Tag</h2>
      <select
        className="tag-select"
        value={selectedTag}
        onChange={(e) => onTagChange(e.target.value)}
      >
        <option value="">All Documents</option>
        {TAGS.map(tag => (
          <option key={tag} value={tag}>{tag}</option>
        ))}
      </select>

      <hr />

      {/* Documents Section */}
      <h2>Documents</h2>

      <div className="upload-section">
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={handleFileChange}
          disabled={uploading}
        />

        <select
          className="tag-select"
          value={uploadTag}
          onChange={(e) => setUploadTag(e.target.value)}
          disabled={uploading}
        >
          {TAGS.map(tag => (
            <option key={tag} value={tag}>{tag}</option>
          ))}
        </select>

        {confirmReembed ? (
          <div className="confirm-reembed">
            <p>'{confirmReembed}' already exists. Re-embed it?</p>
            <div className="confirm-buttons">
              <button onClick={() => handleUpload(true)} disabled={uploading}>
                Yes
              </button>
              <button onClick={() => setConfirmReembed(null)} disabled={uploading}>
                No
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => handleUpload(false)}
            disabled={!file || uploading}
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        )}
      </div>

      <div className="documents-list">
        {documents.length === 0 ? (
          <p className="no-items">No documents yet</p>
        ) : (
          documents.map(doc => (
            <div key={doc.id} className="document-item">
              <span>{doc.filename}</span>
              {doc.tag && <span className="doc-tag">{doc.tag}</span>}
            </div>
          ))
        )}
      </div>
    </aside>
  )
}

export default Sidebar
