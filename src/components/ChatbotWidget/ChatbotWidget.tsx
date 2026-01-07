import React, { useState, useEffect } from 'react';
import styles from './ChatbotWidget.module.css';

const ChatbotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [stats, setStats] = useState({ total_chunks: 0, total_documents: 0 });
  const [isLoading, setIsLoading] = useState(false);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleSend = async () => {
    if (inputValue.trim() !== '' && !isLoading) {
      // Add user message to chat
      const userMessage = { id: Date.now(), text: inputValue, sender: 'user' };
      setMessages(prev => [...prev, userMessage]);

      // Log to console as per requirements
      console?.log?.('User asked:', inputValue);

      // Clear input and set loading state
      setInputValue('');
      setIsLoading(true);

      try {
        // Call the backend RAG API
        const response = await fetch('http://localhost:8002/query', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question: inputValue,
            max_sources: 3
          })
        });

        if (response.ok) {
          const data = await response.json();
          const botResponse = {
            id: Date.now() + 1,
            text: data.answer,
            sender: 'bot',
            sources: data.sources // Store sources if needed for display
          };
          setMessages(prev => [...prev, botResponse]);
        } else {
          // Handle error response from backend
          const errorResponse = {
            id: Date.now() + 1,
            text: 'Sorry, I encountered an issue processing your question. Please try again.',
            sender: 'bot'
          };
          setMessages(prev => [...prev, errorResponse]);
        }
      } catch (error) {
        // Handle network or other errors
        console.error('Error calling RAG API:', error);
        const errorResponse = {
          id: Date.now() + 1,
          text: 'Sorry, I\'m having trouble connecting to the RAG service. Please try again later.',
          sender: 'bot'
        };
        setMessages(prev => [...prev, errorResponse]);
      } finally {
        // Reset loading state
        setIsLoading(false);
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8002/stats');
      if (response.ok) {
        const data = await response.json();
        setStats({
          total_chunks: data.total_chunks,
          total_documents: data.total_documents
        });
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // Client-side only rendering using useEffect
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    // Fetch stats when component mounts
    fetchStats();
  }, []);

  if (!isMounted) {
    // Render a minimal placeholder during SSR/hydration
    return <div style={{ display: 'none' }} />;
  }

  return (
    <div className={styles.chatbotContainer}>
      {isOpen ? (
        <div className={styles.chatbotPanel}>
          <div className={styles.chatHeader}>
            <h4>Ask the Book</h4>
            <div className={styles.stats}>
              <span title="Total chunks in knowledge base">📚 {stats.total_chunks} chunks</span>
            </div>
            <button
              className={styles.closeButton}
              onClick={toggleChat}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>
          <div className={styles.chatMessages}>
            {messages.length === 0 ? (
              <div className={styles.welcomeMessage}>
                Hello! I'm your RAG chatbot. Ask me questions about the book content and I'll find relevant information for you!
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`${styles.message} ${styles[message.sender]}`}
                  >
                    {message.text}
                  </div>
                ))}
                {isLoading && (
                  <div className={`${styles.message} ${styles.bot}`}>
                    Thinking...
                  </div>
                )}
              </>
            )}
          </div>
          <div className={styles.chatInputContainer}>
            <input
              type="text"
              className={styles.chatInput}
              value={inputValue}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about the book..."
              aria-label="Chat input"
              disabled={isLoading}
            />
            <button
              className={styles.sendButton}
              onClick={handleSend}
              aria-label="Send message"
              disabled={isLoading}
            >
              {isLoading ? '...' : 'Send'}
            </button>
          </div>
        </div>
      ) : (
        <button
          className={styles.chatButton}
          onClick={toggleChat}
          aria-label="Open chat"
        >
          Ask the Book
        </button>
      )}
    </div>
  );
};

export default ChatbotWidget;