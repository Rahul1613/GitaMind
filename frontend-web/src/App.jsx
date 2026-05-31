import React, { useState, useEffect, useRef } from 'react';
import Auth from './Auth';
import Sidebar from './components/Sidebar';
import ChatInput from './components/ChatInput';
import MessageBubble from './components/MessageBubble';
import { getChats, createChat, getMessages, renameChat, deleteChat, API_URL } from './api';
import './App.css';
import { FiMenu } from 'react-icons/fi';

export default function App() {
    const [userId, setUserId] = useState(() => localStorage.getItem('userId') || null);
    const [username, setUsername] = useState(() => localStorage.getItem('username') || '');
    const [chats, setChats] = useState([]);
    const [activeChatId, setActiveChatId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [isWaiting, setIsWaiting] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [language, setLanguage] = useState('English');

    const messagesEndRef = useRef(null);

    // Auto-scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isWaiting]);

    useEffect(() => {
        if (userId) {
            loadChats();
        }
    }, [userId]);

    const loadChats = async () => {
        try {
            const data = await getChats(userId);
            setChats(data);
        } catch (e) {
            console.error(e);
        }
    };

    const handleLogin = (uid, uname) => {
        setUserId(uid);
        setUsername(uname);
        localStorage.setItem('userId', uid);
        localStorage.setItem('username', uname);
    };

    const handleLogout = () => {
        setUserId(null);
        setUsername('');
        setActiveChatId(null);
        setMessages([]);
        setChats([]);
        localStorage.removeItem('userId');
        localStorage.removeItem('username');
    };

    const handleNewChat = () => {
        setActiveChatId(null);
        setMessages([]);
        if (window.innerWidth <= 768) setSidebarOpen(false);
    };

    const handleSelectChat = async (chatId) => {
        setActiveChatId(chatId);
        try {
            const data = await getMessages(chatId);
            setMessages(data);
        } catch (e) {
            console.error(e);
        }
        if (window.innerWidth <= 768) setSidebarOpen(false);
    };

    const handleDeleteChat = async (chatId) => {
        if (confirm('Delete this chat?')) {
            await deleteChat(chatId);
            if (activeChatId === chatId) handleNewChat();
            loadChats();
        }
    };

    const handleRenameChat = async (chatId) => {
        const newTitle = prompt('Enter new chat title:');
        if (newTitle) {
            await renameChat(chatId, newTitle);
            loadChats();
        }
    };

    const handleSendMessage = async (text) => {
        if (!text.trim() || isWaiting) return;
        setIsWaiting(true);

        let currentChatId = activeChatId;
        if (!currentChatId) {
            // Create new chat
            const title = text.length > 30 ? text.substring(0, 30) + '...' : text;
            try {
                const res = await createChat(userId, title);
                currentChatId = res.chat_id;
                setActiveChatId(currentChatId);
                loadChats();
            } catch (e) {
                console.error(e);
                setIsWaiting(false);
                return;
            }
        }

        // Add user and assistant messages atomically
        setMessages(prev => [
            ...prev,
            { role: 'user', content: text, docs: null },
            { role: 'assistant', content: '', docs: null }
        ]);

        try {
            const response = await fetch(`${API_URL}/chats/${currentChatId}/stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chat_id: currentChatId, user_id: userId, prompt: text, language: language })
            });

            if (!response.ok) throw new Error('Stream failed');

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");

            let done = false;
            let currentAssistantMsg = '';

            while (!done) {
                const { value, done: readerDone } = await reader.read();
                done = readerDone;
                if (value) {
                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split('\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);
                            if (data === '[DONE]') {
                                done = true;
                            } else {
                                try {
                                    if (data.startsWith('[')) {
                                        const docs = JSON.parse(data);
                                        setMessages(prev => {
                                            const newMsgs = [...prev];
                                            if (newMsgs.length > 0) {
                                                newMsgs[newMsgs.length - 1].docs = docs;
                                            }
                                            return newMsgs;
                                        });
                                    } else {
                                        currentAssistantMsg += data;
                                        setMessages(prev => {
                                            const newMsgs = [...prev];
                                            if (newMsgs.length > 0) {
                                                newMsgs[newMsgs.length - 1].content = currentAssistantMsg;
                                            }
                                            return newMsgs;
                                        });
                                    }
                                } catch (e) {
                                    currentAssistantMsg += data;
                                    setMessages(prev => {
                                        const newMsgs = [...prev];
                                        if (newMsgs.length > 0) {
                                            newMsgs[newMsgs.length - 1].content = currentAssistantMsg;
                                        }
                                        return newMsgs;
                                    });
                                }
                            }
                        }
                    }
                }
            }
        } catch (e) {
            console.error(e);
            setMessages(prev => {
                const newMsgs = [...prev];
                if (newMsgs.length > 0) {
                    newMsgs[newMsgs.length - 1].content += "\n\n*(Error connecting to the spiritual guide)*";
                }
                return newMsgs;
            });
        } finally {
            setIsWaiting(false);
        }
    };

    if (!userId) {
        return <Auth onLogin={handleLogin} />;
    }

    return (
        <>
            <Sidebar 
                chats={chats}
                activeChatId={activeChatId}
                onNewChat={handleNewChat}
                onSelectChat={handleSelectChat}
                onDeleteChat={handleDeleteChat}
                onRenameChat={handleRenameChat}
                username={username}
                onLogout={handleLogout}
                isOpen={sidebarOpen}
            />
            
            <div className="main-chat">
                <div className="mobile-header">
                    <FiMenu size={24} onClick={() => setSidebarOpen(!sidebarOpen)} style={{cursor: 'pointer'}} />
                    <span style={{fontWeight: 'bold'}}>GitaMind</span>
                    <div style={{width: 24}}></div>
                </div>

                <div className="chat-window">
                    {messages.length === 0 ? (
                        <div className="hero-screen">
                            <h1>🕉 GitaMind</h1>
                            <p style={{color: '#888'}}>Ask a question to receive timeless wisdom from the Bhagavad Gita.</p>
                        </div>
                    ) : (
                        messages.map((msg, idx) => (
                            <MessageBubble 
                                key={idx} 
                                message={msg} 
                                isTyping={isWaiting && idx === messages.length - 1 && msg.content === ''}
                            />
                        ))
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <ChatInput 
                    onSendMessage={handleSendMessage} 
                    isWaiting={isWaiting} 
                    language={language}
                    onLanguageChange={setLanguage}
                />
            </div>
        </>
    );
}
