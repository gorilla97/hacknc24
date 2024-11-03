'use client'

import { Button } from '@/components/ui/button';
import { useState } from 'react';

interface Message {
  text: string;
  sender: 'You' | 'Bot';
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleSendMessage = async () => {
    if (input.trim() === '') return;

    // Add the user's message to the chat
    setMessages([...messages, { text: input, sender: 'You' }]);
    const userMessage = input;
    setInput(''); // Clear the input field

    // Call OpenAI API to get a response
    setLoading(true);
    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${process.env.NEXT_PUBLIC_OPENAI_API_KEY}`,
        },
        body: JSON.stringify({
          model: 'gpt-3.5-turbo',
          messages: [{ role: 'user', content: userMessage }],
        }),
      });

      const data = await response.json();
      const botMessage = data.choices[0]?.message?.content || "I'm not sure how to respond to that.";

      // Add the bot's response to the chat
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: botMessage, sender: 'Bot' }
      ]);
    } catch (error) {
      console.error('Error fetching OpenAI API:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: 'Failed to fetch response from OpenAI.', sender: 'Bot' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col max-w-md mx-auto h-[70vh] bg-white shadow-md rounded-lg transition-all hover:shadow-lg">
      {/* Chat Messages Window */}
      <div className="flex-1 p-4 overflow-y-auto border-b  hover:bg-gray-100">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`my-2 ${message.sender === 'You' ? 'text-right' : 'text-left'}`}
          >
            <div
              className={`inline-block px-4 py-2 rounded-lg ${
                message.sender === 'You' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'
              }`}
            >
              <span className="font-medium">{message.sender}: </span>{message.text}
            </div>
          </div>
        ))}
      </div>

      {/* Input Area */}
      <div className="flex items-center p-4 border-t space-x-2">
        <textarea
          value={input}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
          placeholder="Type a message..."
          className="flex-1 resize-none px-4 py-2 border rounded-md focus:outline-none focus:ring focus:ring-blue-500 focus:ring-opacity-50"
          rows={1}
          disabled={loading}
        />
        <Button onClick={handleSendMessage} disabled={loading}>
          {loading ? 'Sending...' : 'Send'}
        </Button>
      </div>
    </div>
  );
}
