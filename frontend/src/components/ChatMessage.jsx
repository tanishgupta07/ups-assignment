import { useState } from 'react'

function ChatMessage({ message, onFeedback }) {
  const [showSources, setShowSources] = useState(false)
  const [feedbackGiven, setFeedbackGiven] = useState(null)

  const handleFeedback = (type) => {
    if (feedbackGiven) return
    setFeedbackGiven(type)
    onFeedback(message, type)
  }

  const hasSources = message.sources && message.sources.length > 0

  return (
    <div className={`message ${message.role}`}>
      <div className="message-content">{message.text}</div>

      {message.role === 'assistant' && (
        <>
          <div className="feedback-buttons">
            <button
              onClick={() => handleFeedback('positive')}
              className={feedbackGiven === 'positive' ? 'active' : ''}
              disabled={feedbackGiven}
            >
              👍
            </button>
            <button
              onClick={() => handleFeedback('negative')}
              className={feedbackGiven === 'negative' ? 'active' : ''}
              disabled={feedbackGiven}
            >
              👎
            </button>
          </div>

          {hasSources && (
            <>
              <button
                className="sources-toggle"
                onClick={() => setShowSources(!showSources)}
              >
                {showSources ? 'Hide Sources' : 'Show Sources'}
              </button>

              {showSources && (
                <div className="sources">
                  {message.sources.map((source, i) => (
                    <div key={i} className="source-item">
                      <div className="source-filename">
                        [{i + 1}] {source.metadata?.filename || 'unknown'}
                      </div>
                      <div className="source-content">
                        {source.content?.slice(0, 200)}...
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  )
}

export default ChatMessage
