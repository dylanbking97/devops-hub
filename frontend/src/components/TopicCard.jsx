import { Link } from 'react-router-dom'

export default function TopicCard({ topic, visited, completed }) {
  const status = completed ? 'completed' : visited ? 'visited' : 'new'

  return (
    <Link to={`/topics/${topic.slug}`} className={`topic-card topic-card--${status}`}>
      <div className="topic-card__icon">{topic.icon}</div>
      <div className="topic-card__body">
        <h2>{topic.title}</h2>
        <p>{topic.summary}</p>
      </div>
      <div className="topic-card__badge">
        {completed ? '✓ Completed' : visited ? '⏳ In Progress' : 'Start →'}
      </div>
    </Link>
  )
}
