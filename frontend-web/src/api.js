export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const loginUser = async (username, password) => {
    const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Login failed");
    }
    return res.json();
};

export const signupUser = async (username, password) => {
    const res = await fetch(`${API_URL}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Signup failed");
    }
    return res.json();
};

export const getChats = async (userId) => {
    const res = await fetch(`${API_URL}/users/${userId}/chats`);
    return res.json();
};

export const createChat = async (userId, title) => {
    const res = await fetch(`${API_URL}/chats`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, title })
    });
    return res.json();
};

export const getMessages = async (chatId) => {
    const res = await fetch(`${API_URL}/chats/${chatId}/messages`);
    return res.json();
};

export const renameChat = async (chatId, title) => {
    const res = await fetch(`${API_URL}/chats/${chatId}/rename`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title })
    });
    return res.json();
};

export const deleteChat = async (chatId) => {
    const res = await fetch(`${API_URL}/chats/${chatId}`, {
        method: "DELETE"
    });
    return res.json();
};
