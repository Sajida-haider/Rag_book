import React from 'react';
import styles from './ChatbotWidget.module.css';

const SimpleChatbotWidget = () => {
  // Simple implementation without state or complex logic
  return (
    <div className={styles.chatbotContainer}>
      <button className={styles.chatButton}>
        Ask the Book
      </button>
    </div>
  );
};

export default SimpleChatbotWidget;