import React from 'react';
import OriginalLayout from '@theme-original/Layout';
import BrowserOnly from '@docusaurus/BrowserOnly';
import ChatbotWidget from '../components/ChatbotWidget/ChatbotWidget';

export default function Layout(props) {
  return (
    <OriginalLayout {...props}>
      {props.children}
      <BrowserOnly>
        {() => <ChatbotWidget />}
      </BrowserOnly>
    </OriginalLayout>
  );
}