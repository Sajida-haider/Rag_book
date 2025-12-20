import React, { useState, useEffect } from 'react';
import styles from './ChatbotWidget.module.css';

const ChatbotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleSend = () => {
    if (inputValue.trim() !== '') {
      // Add user message to chat
      const userMessage = { id: Date.now(), text: inputValue, sender: 'user' };
      setMessages(prev => [...prev, userMessage]);

      // Log to console as per requirements
      console?.log?.('User asked:', inputValue);

      // Clear input
      setInputValue('');

      // Add placeholder response after a short delay
      setTimeout(() => {
        const placeholderResponse = {
          id: Date.now() + 1,
          text: 'This is a placeholder for the future RAG chatbot. Coming soon!',
          sender: 'bot'
        };
        setMessages(prev => [...prev, placeholderResponse]);
      }, 500);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  // Client-side only rendering using useEffect
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
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
                Hello! This is a placeholder for the future RAG chatbot.
                Ask questions about the book content and we'll have answers soon!
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`${styles.message} ${styles[message.sender]}`}
                >
                  {message.text}
                </div>
              ))
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
            />
            <button
              className={styles.sendButton}
              onClick={handleSend}
              aria-label="Send message"
            >
              Send
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