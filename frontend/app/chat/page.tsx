"use client";

import { useState, useRef, useEffect } from "react";
import { FaPaperPlane, FaRobot, FaUser, FaSpinner, FaPuzzlePiece } from "react-icons/fa";
import ReactMarkdown from "react-markdown";

// Message type
interface Message {
  id: string;
  content: string;
  role: "user" | "assistant" | "system";
  stepInfo?: {
    id: number;
    name: string;
  };
  plugin_used?: string | null;
  timestamp: Date;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamedResponse, setStreamedResponse] = useState("");
  const [processingSteps, setProcessingSteps] = useState<{ [id: number]: boolean }>({});
  const [availablePlugins, setAvailablePlugins] = useState<any[]>([]);
  const [selectedPlugin, setSelectedPlugin] = useState<number | null | 'auto'>(null);
  const [autoPluginMode, setAutoPluginMode] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch plugins on mount
  useEffect(() => {
    const fetchPlugins = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/plugins`);
        if (res.ok) {
          const data = await res.json();
          setAvailablePlugins(data);
        }
      } catch (e) {
        console.error("Failed to fetch plugins", e);
      }
    };
    fetchPlugins();
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming, streamedResponse]);

  // Handle chat form submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: "user",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setIsStreaming(true);
    setStreamedResponse("");

    try {
      const response = await fetch("/api/query/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: input,
          plugin_id: selectedPlugin === 'auto' ? null : selectedPlugin,
          auto_select_plugin: selectedPlugin === 'auto'
        }),
      });
      if (!response.body) throw new Error("No response body");
      const reader = response.body.getReader();
      let fullResponse = "";
      let autoSelectedPlugin: string | null = null;
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = new TextDecoder().decode(value);

        // Process each line (could be multiple chunks in one read)
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            if (data.text) {
              // Check if this is a step message
              if (data.step) {
                // Add a new message for this step
                const stepId = data.step.id;
                const stepName = data.step.name;
                const role = data.step.role || 'system';

                // Only add the step message if we haven't processed this step ID before
                if (!processingSteps[stepId]) {
                  setProcessingSteps(prev => ({ ...prev, [stepId]: true }));

                  // Format the content to include reasoning if available
                  let content = data.text;
                  if (data.reasoning) {
                    // Add the reasoning in a collapsible details element
                    content = `${data.text}\n\n<details>
                    <summary>**Why this decision was made**</summary>
                    ${data.reasoning}
                    </details>`;
                  }

                  const stepMessage: Message = {
                    id: `step-${Date.now()}-${stepId}`,
                    content: content,
                    role: role as 'user' | 'assistant' | 'system',
                    stepInfo: {
                      id: stepId,
                      name: stepName
                    },
                    timestamp: new Date()
                  };

                  setMessages(prev => [...prev, stepMessage]);
                }
              } else {
                // Regular message without step info
                fullResponse += data.text;
                setStreamedResponse(fullResponse);
              }
            } else if (data.plugin_used) {
              // Store the auto-selected plugin name
              autoSelectedPlugin = data.plugin_used;
              console.log(`Auto-selected plugin: ${autoSelectedPlugin}`);
            } else if (data.error) {
              console.error('Stream error:', data.error);
              throw new Error(data.error);
            }
          } catch (e) {
            console.warn('Error parsing JSON from stream:', e);
            // If it's not valid JSON, just append it as is
            if (line.trim()) {
              fullResponse += line;
              setStreamedResponse(fullResponse);
            }
          }
        }
      }
      // Add the assistant's response to messages if it's not empty and not already handled as steps
      if (fullResponse.trim() && Object.keys(processingSteps).length === 0) {
        setMessages(prev => [...prev, {
          id: `assistant-${Date.now()}`,
          content: fullResponse,
          role: 'assistant',
          timestamp: new Date()
        }]);
      }

      // Reset the processing steps for the next query
      setProcessingSteps({});

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: fullResponse,
        role: "assistant",
        plugin_used: autoSelectedPlugin || (selectedPlugin && selectedPlugin !== 'auto' ? availablePlugins.find((p) => p.id === selectedPlugin)?.name : null),
        timestamp: new Date(),
      };

      // If a plugin was auto-selected, show a notification in the UI
      if (selectedPlugin === 'auto' && autoSelectedPlugin) {
        const autoSelectMessage: Message = {
          id: Date.now().toString(),
          content: `I've automatically selected the "${autoSelectedPlugin}" plugin to help answer your query.`,
          role: "system",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, autoSelectMessage]);
      }
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `Sorry, there was an error processing your request: ${error instanceof Error ? error.message : String(error)}`,
        role: "assistant",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
      setInput("");
      setStreamedResponse("");
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-primary-600 text-white p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center text-xl font-bold">
            <FaRobot className="mr-2" /> Cybersecurity AI Assistant
          </div>
          <div>
            <select
              className="bg-primary-700 text-white p-2 rounded"
              value={selectedPlugin === 'auto' ? 'auto' : (selectedPlugin || "")}
              onChange={(e) => {
                const value = e.target.value;
                if (value === 'auto') {
                  setSelectedPlugin('auto');
                } else {
                  setSelectedPlugin(value ? Number(value) : null);
                }
              }}
            >
              <option value="">No Plugin</option>
              <option value="auto">Auto (LLM decides)</option>
              {availablePlugins.map((plugin) => (
                <option key={plugin.id} value={plugin.id}>
                  {plugin.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        {/* Plugin Information Panel */}
        <div className="bg-primary-700 rounded p-3 mt-2">
          <h3 className="text-lg font-semibold mb-2 flex items-center">
            <FaPuzzlePiece className="mr-2" /> Available Plugins
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {availablePlugins.length === 0 ? (
              <div className="text-gray-300">No plugins available</div>
            ) : (
              availablePlugins.map((plugin) => (
                <div 
                  key={plugin.id} 
                  className={`border border-gray-600 rounded p-2 cursor-pointer transition-colors ${selectedPlugin === plugin.id ? 'bg-primary-500 border-white' : 'hover:bg-primary-600'}`}
                  onClick={() => setSelectedPlugin(plugin.id)}
                >
                  <div className="font-medium">{plugin.name}</div>
                  <div className="text-xs text-gray-300 mt-1">{plugin.description}</div>
                </div>
              ))
            )}
            <div 
              className={`border border-gray-600 rounded p-2 cursor-pointer transition-colors ${selectedPlugin === 'auto' ? 'bg-primary-500 border-white' : 'hover:bg-primary-600'}`}
              onClick={() => setSelectedPlugin('auto')}
            >
              <div className="font-medium">Auto-select</div>
              <div className="text-xs text-gray-300 mt-1">Let the AI decide which plugin to use based on your query</div>
            </div>
            <div 
              className={`border border-gray-600 rounded p-2 cursor-pointer transition-colors ${selectedPlugin === null ? 'bg-primary-500 border-white' : 'hover:bg-primary-600'}`}
              onClick={() => setSelectedPlugin(null)}
            >
              <div className="font-medium">No Plugin</div>
              <div className="text-xs text-gray-300 mt-1">Direct AI response without using any tools</div>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Messages */}
      <main className="flex-1 overflow-y-auto p-4">
        <div className="max-w-2xl mx-auto">
          {messages.length === 0 ? (
            <div className="text-center py-10">
              <FaRobot className="text-5xl mx-auto mb-4 text-gray-400" />
              <h2 className="text-2xl font-semibold mb-2">How can I help with cybersecurity today?</h2>
              <p className="text-gray-500">
                Ask me about threats, vulnerabilities, best practices, or any cybersecurity concerns.
              </p>
            </div>
          ) : (
            <div className="flex flex-col">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} mb-4`}
                >
                  <div className={`flex ${message.role === "user" ? "chat-message-user" : "chat-message-assistant"}`}>
                    <div className="mr-2 mt-1">
                      {message.role === "user" ? (
                        <FaUser className="text-blue-600 dark:text-blue-400" />
                      ) : (
                        <FaRobot className="text-gray-600 dark:text-gray-400" />
                      )}
                    </div>
                    <div>
                      {message.plugin_used && (
                        <div className="text-xs text-gray-500 mb-1">
                          Using plugin: {message.plugin_used}
                        </div>
                      )}
                      <div className="markdown-content">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {isStreaming && streamedResponse && (
                <div className="flex justify-start mb-4">
                  <div className="chat-message-assistant">
                    <div className="mr-2 mt-1">
                      <FaRobot className="text-gray-600 dark:text-gray-400" />
                    </div>
                    <div>
                      <div className="markdown-content">
                        <ReactMarkdown>{streamedResponse}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              {isLoading && !streamedResponse && (
                <div className="flex justify-start mb-4">
                  <div className="chat-message-assistant">
                    <div className="flex items-center">
                      <FaSpinner className="animate-spin mr-2" />
                      <span>Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </main>

      {/* Input Form */}
      <footer className="border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800">
        <form onSubmit={handleSubmit} className="flex max-w-2xl mx-auto">
          <input
            type="text"
            className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded-l focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
            placeholder="Type your cybersecurity question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
          />
          <button
            type="submit"
            className="bg-primary-600 text-white p-2 rounded-r hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-gray-400"
            disabled={isLoading || !input.trim()}
          >
            {isLoading ? <FaSpinner className="animate-spin" /> : <FaPaperPlane />}
          </button>
        </form>
      </footer>
    </div>
  );
}
