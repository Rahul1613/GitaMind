import React, { useState, useRef, useEffect } from 'react';
import { FiSend, FiPaperclip, FiMic } from 'react-icons/fi';

export default function ChatInput({ onSendMessage, isWaiting, language, onLanguageChange }) {
    const [text, setText] = useState('');
    const textareaRef = useRef(null);

    const handleInput = (e) => {
        setText(e.target.value);
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            send();
        }
    };

    const send = () => {
        if (text.trim() && !isWaiting) {
            onSendMessage(text.trim());
            setText('');
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
            }
        }
    };

    return (
        <div className="input-container">
            <div style={{ display: 'flex', flexDirection: 'column', width: '100%', maxWidth: '768px', gap: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'flex-end', fontSize: '0.85rem', color: '#888', alignItems: 'center', gap: '8px' }}>
                    <span>Response Language:</span>
                    <select 
                        value={language} 
                        onChange={(e) => onLanguageChange(e.target.value)}
                        style={{
                            background: 'var(--input-bg)',
                            color: 'var(--text-color)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '6px',
                            padding: '4px 8px',
                            outline: 'none',
                            cursor: 'pointer',
                            fontSize: '0.85rem'
                        }}
                    >
                        <option value="English">English</option>
                        <option value="Hindi">Hindi (हिन्दी)</option>
                        <option value="Sanskrit">Sanskrit (संस्कृत)</option>
                        <option value="Bengali">Bengali (বাংলা)</option>
                        <option value="Gujarati">Gujarati (ગુજરાતી)</option>
                        <option value="Marathi">Marathi (મરાठी)</option>
                        <option value="Tamil">Tamil (தமிழ்)</option>
                        <option value="Spanish">Spanish (Español)</option>
                        <option value="French">French (Français)</option>
                    </select>
                </div>
                <div className="input-box">
                <button type="button" disabled title="Attach File">
                    <FiPaperclip size={18} />
                </button>
                <textarea
                    ref={textareaRef}
                    value={text}
                    onChange={handleInput}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask for spiritual guidance..."
                    rows={1}
                    disabled={isWaiting}
                />
                <button type="button" disabled title="Voice Input">
                    <FiMic size={18} />
                </button>
                <button type="button" onClick={send} disabled={!text.trim() || isWaiting} style={{background: text.trim() ? '#10A37F' : 'transparent'}}>
                    <FiSend size={18} color={text.trim() ? '#fff' : 'inherit'} />
                </button>
            </div>
        </div>
    </div>
    );
}
