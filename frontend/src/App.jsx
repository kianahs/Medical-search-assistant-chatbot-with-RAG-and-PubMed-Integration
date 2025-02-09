import { useState } from "react";
import "./App.css";
import Chatbot from "./Chatbot";
import Heading from "./Heading";
function App() {
  return (
    <div className="d-flex flex-column align-items-center justify-content-center min-vh-100 bg-gradient">
      <Heading />

      {/* Chatbot Component */}
      <div className="chatbot-container w-100 w-md-75 w-lg-50">
        <Chatbot />
      </div>
    </div>
  );
}

export default App;
