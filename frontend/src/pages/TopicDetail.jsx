import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { fetchTopic, visitTopic, completeTopic, ensureSession } from '../api'

export default function TopicDetail() {
  const { slug } = useParams()
  const [topic, setTopic] = useState(null)
  const [session, setSession] = useState(null)So 

  useEffect(() => {
    Promise.all([fetchTopic(slug), ensureSession()]).then(([t, s]) => {
      setTopic(t)
      setSession(s)
      // Record the visit after we have a session
      visitTopic(slug).then(updated => updated && setSession(updated))
    })
  }, [slug])

  const handleComplete = async () => {
    const updated = await completeTopic(slug)
    if (updated) setSession(updated)
  }

  if (!topic) return <div className="loading">Loading...</div>

  const isCompleted = session?.completed.includes(slug)

  return (
    <div className="topic-detail">
      <Link to="/" className="back-link">← All Topics</Link>
      <div className="topic-header">
        <span className="topic-icon">{topic.icon}</span>
        <h1>{topic.title}</h1>
      </div>
      <div className="topic-content">
        <ReactMarkdown>{topic.content}</ReactMarkdown>
      </div>
      <div className="topic-actions">
        {isCompleted ? (
          <span className="completed-badge">✓ Completed</span>
        ) : (
          <button className="complete-btn" onClick={handleComplete}>
            Mark as Complete
          </button>
        )}
      </div>
    </div>
  )
}
