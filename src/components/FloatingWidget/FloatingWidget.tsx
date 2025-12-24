import React, { useState, useEffect } from 'react';
import clsx from 'clsx';
import styles from './FloatingWidget.module.css';

const FloatingWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI assistant. How can I help you with Physical AI & Humanoid Robotics today?",
      sender: 'bot'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState({ total_chunks: 0, total_documents: 0 });

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8001/stats');
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

  useEffect(() => {
    setIsMounted(true);
    // Fetch stats when component mounts
    fetchStats();
  }, []);

  const toggleWidget = () => {
    setIsOpen(!isOpen);
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  const handleSend = async () => {
    if (inputValue.trim() !== '' && !isLoading) {
      // Add user message to chat
      const userMessage = { id: Date.now(), text: inputValue, sender: 'user' };
      setMessages(prev => [...prev, userMessage]);

      // Log to console
      console?.log?.('User asked:', inputValue);

      // Clear input and set loading state
      setInputValue('');
      setIsLoading(true);

      try {
        // Call the backend RAG API
        const response = await fetch('http://localhost:8001/query', {
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
            sources: data.sources
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
          text: "Sorry, I'm having trouble connecting to the RAG service. Please try again later.",
          sender: 'bot'
        };
        setMessages(prev => [...prev, errorResponse]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  if (!isMounted) {
    return null;
  }

  return (
    <div className={clsx(styles.floatingWidget, isOpen && styles.open)}>
      {!isOpen ? (
        <button
          className={clsx(styles.floatingButton, styles.bottomLeft)}
          onClick={toggleWidget}
          aria-label="Open chatbot"
        >
          <svg
            className={styles.widgetIcon}
            viewBox="0 0 24 24"
            width="24"
            height="24"
          >
            <path
              fill="currentColor"
              d="M12 2C6.48 2 2 6.48 2 12c0 1.54.36 3.01.99 4.32L1 23l6.68-2.01C9.24 21.62 10.56 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"
            />
            <circle cx="9" cy="11" r="1" fill="currentColor" />
            <circle cx="15" cy="11" r="1" fill="currentColor" />
            <path
              fill="currentColor"
              d="M9.5 15c.28 0 .5-.22.5-.5s-.22-.5-.5-.5-.5.22-.5.5.22.5.5.5zm5 0c.28 0 .5-.22.5-.5s-.22-.5-.5-.5-.5.22-.5.5.22.5.5.5z"
            />
          </svg>
        </button>
      ) : (
        <div className={styles.widgetContainer}>
          <div className={styles.widgetHeader}>
            <h3 className={styles.widgetTitle}>AI Assistant</h3>
            <div className={styles.stats}>
              <span title="Total chunks in knowledge base">📚 {stats.total_chunks} chunks</span>
            </div>
            <button
              className={styles.closeButton}
              onClick={toggleWidget}
              aria-label="Close chatbot"
            >
              ×
            </button>
          </div>
          <div className={styles.widgetContent}>
            <div className={styles.chatMessages}>
              {messages.map((message) => (
                <div key={message.id} className={`${styles.message} ${styles[message.sender]}`}>
                  <div className={styles[`${message.sender}Message`]}>
                    {message.text}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className={styles.message}>
                  <div className={styles.botMessage}>
                    Thinking...
                  </div>
                </div>
              )}
            </div>
            <div className={styles.chatInputContainer}>
              <input
                type="text"
                className={styles.chatInput}
                value={inputValue}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question..."
                disabled={isLoading}
              />
              <button
                className={styles.sendButton}
                onClick={handleSend}
                disabled={isLoading}
              >
                {isLoading ? '...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FloatingWidget;