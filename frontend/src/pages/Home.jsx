import { useEffect, useState } from 'react'
import { ensureSession, fetchTopics } from '../api'
import TopicCard from '../components/TopicCard'

export default function Home() {
  const [topics, setTopics] = useState([])
  const [session, setSession] = useState(null)

  useEffect(() => {
    Promise.all([fetchTopics(), ensureSession()]).then(([t, s]) => {
      setTopics(t)
      setSession(s)
    })
  }, [])

  const completed = session?.completed.length ?? 0

  return (
    <div>
      <div className="hero">
        <h1>DevOps Learning Hub</h1>
        <p>
          A hands-on reference project covering containerization, monitoring, IaC, and GitOps —
          with every concept demonstrated in the stack actually running it.
        </p>
      </div>
      {session && (
        <p className="progress-summary">
          {completed}/{topics.length} topics completed
          {completed === topics.length && topics.length > 0 && ' — nice work!'}
        </p>
      )}
      <div className="topic-grid">
        {topics.map(topic => (
          <TopicCard
            key={topic.slug}
            topic={topic}
            visited={session?.visited.includes(topic.slug)}
            completed={session?.completed.includes(topic.slug)}
          />
        ))}
      </div>
    </div>
  )
}
