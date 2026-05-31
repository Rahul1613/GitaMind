import React from 'react';
import { FiPlus, FiMessageSquare, FiTrash2, FiEdit2 } from 'react-icons/fi';

export default function Sidebar({ 
    chats, 
    activeChatId, 
    onNewChat, 
    onSelectChat, 
    onDeleteChat, 
    onRenameChat,
    username,
    onLogout,
    isOpen 
}) {
    return (
        <div className={`sidebar ${isOpen ? 'open' : ''}`}>
            <button className="new-chat-btn" onClick={onNewChat}>
                <FiPlus /> New chat
            </button>
            
            <div className="chat-history">
                {chats.map(chat => (
                    <div 
                        key={chat.id} 
                        className={`chat-item ${chat.id === activeChatId ? 'active' : ''}`}
                        onClick={() => onSelectChat(chat.id)}
                    >
                        <FiMessageSquare />
                        <span style={{flex: 1, overflow: 'hidden', textOverflow: 'ellipsis'}}>{chat.title}</span>
                        {chat.id === activeChatId && (
                            <div className="chat-item-actions">
                                <FiEdit2 onClick={(e) => { e.stopPropagation(); onRenameChat(chat.id); }} />
                                <FiTrash2 onClick={(e) => { e.stopPropagation(); onDeleteChat(chat.id); }} />
                            </div>
                        )}
                    </div>
                ))}
            </div>

            <div className="user-profile" onClick={onLogout}>
                <div className="avatar user">👤</div>
                <div style={{flex: 1}}>{username}</div>
                <div style={{fontSize: '0.8rem', color: '#888'}}>Logout</div>
            </div>
        </div>
    );
}
