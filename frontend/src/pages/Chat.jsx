import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCurrentUser, askQuestion, getElement, analyzeMedia } from '../api/api';

function Chat() {
  const [user, setUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [elementSearch, setElementSearch] = useState('');
  const [elementInfo, setElementInfo] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
        setMessages([{
          role: 'assistant',
          content: `Welcome! I'm your Periodic Table Facts Bot. Ask me anything about chemical elements, such as:\n\n- "Tell me about Carbon"\n- "What's the electron configuration of Iron?"\n- "Why are noble gases unreactive?"\n- "Give me a fun fact about Gold"`
        }]);
      } catch (err) {
        navigate('/login');
      }
    };
    checkAuth();
  }, [navigate]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await askQuestion(userMessage);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.answer,
        elementContext: response.element_context,
        imageUrl: response.image_url
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: err.response?.data?.detail || 'Sorry, I encountered an error. Please try again.',
        isError: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleElementSearch = async (e) => {
    e.preventDefault();
    if (!elementSearch.trim()) return;

    try {
      const element = await getElement(elementSearch.trim());
      setElementInfo(element);
    } catch (err) {
      setElementInfo({ error: 'Element not found. Try a symbol (like Fe) or name (like Iron).' });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!uploadedFile || loading) return;

    const fileName = uploadedFile.name;
    setMessages(prev => [...prev, { role: 'user', content: `📤 Uploaded: ${fileName}` }]);
    setUploadedFile(null);
    setLoading(true);

    try {
      const result = await analyzeMedia(uploadedFile);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: result.analysis
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: err.response?.data?.detail || 'Sorry, I could not analyze the file. Please try again.',
        isError: true
      }]);
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  if (!user) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>Periodic Table Facts Bot</h1>
        <div className="header-right">
          <span className="user-email">{user.email}</span>
          <button onClick={handleLogout} className="logout-button">Logout</button>
        </div>
      </header>

      <div className="chat-layout">
        <aside className="sidebar">
          <div className="element-lookup">
            <h3>Quick Element Lookup</h3>
            <form onSubmit={handleElementSearch}>
              <input
                type="text"
                value={elementSearch}
                onChange={(e) => setElementSearch(e.target.value)}
                placeholder="Symbol or name (e.g., Fe)"
              />
              <button type="submit">Search</button>
            </form>

            {elementInfo && (
              <div className="element-card">
                {elementInfo.error ? (
                  <p className="error">{elementInfo.error}</p>
                ) : (
                  <>
                    <div className="element-symbol">{elementInfo.symbol}</div>
                    <div className="element-name">{elementInfo.name}</div>
                    <div className="element-details">
                      <p><strong>Atomic #:</strong> {elementInfo.atomic_number}</p>
                      <p><strong>Weight:</strong> {elementInfo.atomic_weight}</p>
                      <p><strong>Group:</strong> {elementInfo.group || 'N/A'}</p>
                      <p><strong>Period:</strong> {elementInfo.period}</p>
                      <p><strong>State:</strong> {elementInfo.state}</p>
                      <p><strong>Config:</strong> {elementInfo.electron_configuration}</p>
                      <p><strong>Density:</strong> {elementInfo.density ? `${elementInfo.density} g/cm³` : 'N/A'}</p>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </aside>

        <main className="chat-main">
          <div className="messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role} ${msg.isError ? 'error' : ''}`}>
                <div className="message-content">
                  {msg.content.split('\n').map((line, i) => (
                    <p key={i}>{line}</p>
                  ))}
                  {msg.imageUrl && (
                    <div className="image-link-container">
                      <button 
                        className="periodic-table-link"
                        onClick={() => window.open(msg.imageUrl, '_blank')}
                      >
                        📊 Elements of Periodic Table
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="message assistant loading">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="chat-input-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about any element or chemistry topic..."
              disabled={loading}
            />
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,video/*"
              onChange={handleFileChange}
              disabled={loading}
              style={{ display: 'none' }}
            />
            <button 
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
              className="file-upload-btn"
              title="Upload image or video for analysis"
            >
              📁
            </button>
            {uploadedFile && (
              <button 
                type="button"
                onClick={handleFileUpload}
                disabled={loading}
                className="send-file-btn"
              >
                Analyze {uploadedFile.name.split('.').pop().toUpperCase()}
              </button>
            )}
            {!uploadedFile && (
              <button type="submit" disabled={loading || !input.trim()}>
                Send
              </button>
            )}
          </form>
        </main>
      </div>

    </div>
  );
}

export default Chat;
