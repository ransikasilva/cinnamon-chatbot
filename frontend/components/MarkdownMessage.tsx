import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import styles from './MarkdownMessage.module.css'

interface MarkdownMessageProps {
  content: string
}

export default function MarkdownMessage({ content }: MarkdownMessageProps) {
  return (
    <div className={styles.markdown}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
        // Paragraph
        p: ({ children }) => <p className={styles.paragraph}>{children}</p>,

        // Headers
        h1: ({ children }) => <h1 className={styles.h1}>{children}</h1>,
        h2: ({ children }) => <h2 className={styles.h2}>{children}</h2>,
        h3: ({ children }) => <h3 className={styles.h3}>{children}</h3>,

        // Lists
        ul: ({ children }) => <ul className={styles.ul}>{children}</ul>,
        ol: ({ children }) => <ol className={styles.ol}>{children}</ol>,
        li: ({ children }) => <li className={styles.li}>{children}</li>,

        // Links
        a: ({ href, children }) => (
          <a href={href} className={styles.link} target="_blank" rel="noopener noreferrer">
            {children}
          </a>
        ),

        // Code
        code: ({ children, className }) => {
          const isInline = !className
          return isInline ? (
            <code className={styles.inlineCode}>{children}</code>
          ) : (
            <code className={styles.codeBlock}>{children}</code>
          )
        },

        // Blockquote
        blockquote: ({ children }) => (
          <blockquote className={styles.blockquote}>{children}</blockquote>
        ),

        // Strong/Bold
        strong: ({ children }) => <strong className={styles.strong}>{children}</strong>,

        // Emphasis/Italic
        em: ({ children }) => <em className={styles.em}>{children}</em>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
