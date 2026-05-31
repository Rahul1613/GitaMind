import { useState } from 'react';
import { loginUser, signupUser } from './api';

export default function Auth({ onLogin }) {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            if (isLogin) {
                const res = await loginUser(username, password);
                onLogin(res.user_id, res.username);
            } else {
                await signupUser(username, password);
                setIsLogin(true);
                setError('Account created! Please log in.');
            }
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-box">
                <h1>🕉 GitaMind</h1>
                <p>{isLogin ? 'Login to continue' : 'Create an account'}</p>
                {error && <div className="error-msg" style={{color: error.includes('created') ? '#10A37F' : '#ff6b6b'}}>{error}</div>}
                
                <form onSubmit={handleSubmit}>
                    <input 
                        type="text" 
                        placeholder="Username" 
                        className="auth-input"
                        value={username}
                        onChange={e => setUsername(e.target.value)}
                        required
                    />
                    <input 
                        type="password" 
                        placeholder="Password" 
                        className="auth-input"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        required
                    />
                    <button type="submit" className="auth-btn">
                        {isLogin ? 'Login' : 'Sign Up'}
                    </button>
                </form>

                <div className="auth-toggle" onClick={() => setIsLogin(!isLogin)}>
                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                    <span>{isLogin ? 'Sign Up' : 'Login'}</span>
                </div>
            </div>
        </div>
    );
}
