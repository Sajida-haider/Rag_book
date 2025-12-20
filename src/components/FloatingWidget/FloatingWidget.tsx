import React, { useState, useEffect } from 'react';
import clsx from 'clsx';
import styles from './FloatingWidget.module.css';

const FloatingWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const toggleWidget = () => {
    setIsOpen(!isOpen);
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
              <div className={styles.message}>
                <div className={styles.botMessage}>
                  Hello! I'm your AI assistant. How can I help you with Physical AI & Humanoid Robotics today?
                </div>
              </div>
            </div>
            <div className={styles.chatInputContainer}>
              <input
                type="text"
                className={styles.chatInput}
                placeholder="Ask a question..."
                disabled
              />
              <button className={styles.sendButton} disabled>
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FloatingWidget;