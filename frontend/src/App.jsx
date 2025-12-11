import { useState, useEffect, useRef } from 'react'
import Sidebar from './components/Sidebar'
import ChatMessage from './components/ChatMessage'
import './App.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [sessionId, setSessionId] = useState(null)
  const [chat, setChat] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessions, setSessions] = useState([])
  const [selectedTag, setSelectedTag] = useState('')
  const chatEndRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chat])

  useEffect(() => {
    fetchSessions()
  }, [])

  const fetchSessions = async () => {
    try {
      const res = await fetch(`${API_URL}/sessions`)
      if (res.ok) {
        const data = await res.json()
        setSessions(data.sessions || [])
      }
    } catch (err) {
      console.error('Failed to fetch sessions', err)
    }
  }

  const createNewSession = async () => {
    try {
      const res = await fetch(`${API_URL}/sessions`, { method: 'POST' })
      if (res.ok) {
        const session = await res.json()
        setSessionId(session.id)
        setChat([])
        fetchSessions()
      }
    } catch (err) {
      console.error('Failed to create session', err)
    }
  }

  const loadSession = async (id) => {
    try {
      const res = await fetch(`${API_URL}/sessions/${id}`)
      if (res.ok) {
        const session = await res.json()
        setSessionId(session.id)
        // convert messages to chat format
        const chatMessages = []
        for (const msg of session.messages || []) {
          chatMessages.push({ role: 'user', text: msg.question, id: Date.now() + Math.random() })
          chatMessages.push({
            role: 'assistant',
            text: msg.answer,
            question: msg.question,
            sources: msg.sources || [],
            id: Date.now() + Math.random()
          })
        }
        setChat(chatMessages)
      }
    } catch (err) {
      console.error('Failed to load session', err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    // create session if none exists
    let currentSessionId = sessionId
    if (!currentSessionId) {
      try {
        const res = await fetch(`${API_URL}/sessions`, { method: 'POST' })
        if (res.ok) {
          const session = await res.json()
          currentSessionId = session.id
          setSessionId(session.id)
          fetchSessions()
        }
      } catch (err) {
        console.error('Failed to create session', err)
        return
      }
    }

    const question = input.trim()
    setInput('')

    const userMsg = { role: 'user', text: question, id: Date.now() }
    setChat(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const body = {
        question,
        session_id: currentSessionId
      }

      // add filter if tag is selected
      if (selectedTag) {
        body.filter = { tag: selectedTag }
      }

      const res = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      if (res.ok) {
        const data = await res.json()
        const assistantMsg = {
          role: 'assistant',
          text: data.answer,
          sources: data.sources,
          question,
          id: Date.now()
        }
        setChat(prev => [...prev, assistantMsg])
        fetchSessions() // refresh session list to update message count
      } else {
        setChat(prev => [...prev, { role: 'assistant', text: 'Something went wrong', id: Date.now() }])
      }
    } catch (err) {
      setChat(prev => [...prev, { role: 'assistant', text: 'Failed to connect to server', id: Date.now() }])
    }

    setLoading(false)
  }

  const handleFeedback = async (msg, feedback) => {
    try {
      await fetch(`${API_URL}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: msg.question,
          answer: msg.text,
          feedback
        })
      })
    } catch (err) {
      console.error('Feedback failed', err)
    }
  }

  return (
    <div className="app">
      <Sidebar
        apiUrl={API_URL}
        sessions={sessions}
        currentSessionId={sessionId}
        onNewSession={createNewSession}
        onSelectSession={loadSession}
        selectedTag={selectedTag}
        onTagChange={setSelectedTag}
      />

      <main className="chat-container">
        <h1>Document Q&A</h1>
        {selectedTag && (
          <div className="filter-badge">
            Filtering: {selectedTag}
          </div>
        )}

        <div className="chat-messages">
          {chat.length === 0 && (
            <div className="empty-chat">
              Start a conversation by typing a question below
            </div>
          )}
          {chat.map(msg => (
            <ChatMessage
              key={msg.id}
              message={msg}
              onFeedback={handleFeedback}
            />
          ))}
          {loading && (
            <div className="message assistant">
              <div className="message-content">Thinking...</div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <form className="chat-input" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask something..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </main>
    </div>
  )
}

export default App
