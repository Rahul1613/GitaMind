import React from 'react';
import ReactMarkdown from 'react-markdown';
import { FiCopy, FiThumbsUp, FiThumbsDown } from 'react-icons/fi';

export default function MessageBubble({ message, isTyping }) {
    const isUser = message.role === 'user';

    const handleCopy = () => {
        navigator.clipboard.writeText(message.content);
    };

    return (
        <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
            <div className="message-content">
                <div className={`avatar ${isUser ? 'user' : 'assistant'}`}>
                    {isUser ? '👤' : '🕉'}
                </div>
                
                <div className="markdown-body" style={{flex: 1}}>
                    {isTyping ? (
                        <div className="typing-container">
                            <span style={{ fontSize: '0.9rem', color: '#888', fontStyle: 'italic', marginRight: '10px' }}>
                                The Sage is contemplating the verses...
                            </span>
                            <div className="typing-indicator">
                                <div className="typing-dot"></div>
                                <div className="typing-dot"></div>
                                <div className="typing-dot"></div>
                            </div>
                        </div>
                    ) : isUser ? (
                        <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
                    ) : (
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                    )}
                    
                    {!isTyping && message.docs && message.docs.length > 0 && (
                        <details className="docs-expander">
                            <summary>Explore the Sacred References</summary>
                            {message.docs.map((doc, idx) => (
                                <blockquote key={idx}>{doc}</blockquote>
                            ))}
                        </details>
                    )}

                    {!isUser && !isTyping && (
                        <div style={{display: 'flex', gap: '1rem', marginTop: '1rem', color: '#888'}}>
                            <FiCopy style={{cursor: 'pointer'}} onClick={handleCopy} title="Copy" />
                            <FiThumbsUp style={{cursor: 'pointer'}} title="Helpful" />
                            <FiThumbsDown style={{cursor: 'pointer'}} title="Not helpful" />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
