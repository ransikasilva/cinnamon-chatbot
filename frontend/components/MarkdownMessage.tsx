import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface MarkdownMessageProps {
  content: string
}

export default function MarkdownMessage({ content }: MarkdownMessageProps) {
  return (
    <div className="font-inter text-neutral-800 leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
        // Paragraph
        p: ({ children }) => <p className="mb-2.5 text-[13px] last:mb-0">{children}</p>,

        // Headers
        h1: ({ children }) => <h1 className="text-lg font-bold text-purple-secondary my-3 mb-2 font-poppins">{children}</h1>,
        h2: ({ children }) => <h2 className="text-base font-bold text-purple-secondary my-2.5 mb-1.5 font-poppins">{children}</h2>,
        h3: ({ children }) => <h3 className="text-sm font-semibold text-purple-secondary my-2 mb-1 font-poppins">{children}</h3>,

        // Lists
        ul: ({ children }) => <ul className="my-2 pl-5">{children}</ul>,
        ol: ({ children }) => <ol className="my-2 pl-5">{children}</ol>,
        li: ({ children }) => <li className="my-1 text-[13px]">{children}</li>,

        // Links
        a: ({ href, children }) => (
          <a href={href} className="text-purple-secondary underline transition-colors duration-200 hover:text-purple-dark" target="_blank" rel="noopener noreferrer">
            {children}
          </a>
        ),

        // Code
        code: ({ children, className }) => {
          const isInline = !className
          return isInline ? (
            <code className="bg-neutral-100 border border-neutral-200 rounded px-1.5 py-0.5 font-mono text-xs text-pink-600">{children}</code>
          ) : (
            <code className="block bg-neutral-100 border border-neutral-200 rounded p-2.5 font-mono text-xs overflow-x-auto my-2">{children}</code>
          )
        },

        // Blockquote
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-purple-secondary pl-3 my-2 text-neutral-600 italic">{children}</blockquote>
        ),

        // Strong/Bold
        strong: ({ children }) => <strong className="font-bold text-neutral-800">{children}</strong>,

        // Emphasis/Italic
        em: ({ children }) => <em className="italic text-neutral-700">{children}</em>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
