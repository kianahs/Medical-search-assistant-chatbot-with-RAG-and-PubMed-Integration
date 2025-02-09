import React from 'react'
import { beforeRead } from './../node_modules/@popperjs/core/dist/esm/enums';

const Heading = () => {
  return (
    
      <div className="text-center mb-4">
      <h1 className="display-4 text-primary">
        Welcome to the Medical Assistant
      </h1>
      <p className="lead text-muted">
        Ask questions about medical or health topics and get instant responses. Our
        chatbot is here to help you. 
        Our bot has access to medical news, PubMed publications, and our database articles.
      </p>
      <p className="text-muted">
        Type your question and hit "Send" to receive an answer from our AI
        assistant.
      </p>
      </div>
  )
}

export default Heading

