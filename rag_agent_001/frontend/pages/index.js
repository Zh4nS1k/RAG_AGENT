import { useState, useEffect } from 'react';
import Head from 'next/head';
import { Send, Bot, User, Database, Table } from 'lucide-react';

export default function Home() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Привет! Я юридический ассистент по законодательству РК. Чем могу помочь? 🇰🇿' }
  ]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat'); // chat, postgres, vector
  const [dbData, setDbData] = useState([]);
  const [vectorData, setVectorData] = useState({ ids: [], documents: [], metadatas: [] });

  const handleSend = async () => {
    if (!question.trim()) return;
    
    const userMsg = { role: 'user', content: question };
    setMessages(prev => [...prev, userMsg]);
    setQuestion('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: '❌ Ошибка подключения к серверу.' }]);
    } finally {
      setLoading(false);
    }
  };

  const fetchPostgres = async () => {
    try {
      const res = await fetch('http://localhost:8000/db/articles');
      const data = await res.json();
      setDbData(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchVector = async () => {
    try {
      const res = await fetch('http://localhost:8000/db/vector');
      const data = await res.json();
      setVectorData(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (activeTab === 'postgres') fetchPostgres();
    if (activeTab === 'vector') fetchVector();
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-gray-900 text-white font-sans">
      <Head>
        <title>RAG Agent 001 🇰🇿</title>
      </Head>

      {/* Sidebar */}
      <div className="flex">
        <div className="w-64 bg-gray-800 h-screen p-4 flex flex-col border-r border-gray-700">
          <h1 className="text-xl font-bold mb-8 flex items-center gap-2">
            <Bot size={28} className="text-blue-400" /> RAG Agent 001
          </h1>
          
          <nav className="flex flex-col gap-2">
            <button 
              onClick={() => setActiveTab('chat')}
              className={`p-3 rounded-lg flex items-center gap-3 transition ${activeTab === 'chat' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
            >
              <Send size={18} /> Чат
            </button>
            <button 
              onClick={() => setActiveTab('postgres')}
              className={`p-3 rounded-lg flex items-center gap-3 transition ${activeTab === 'postgres' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
            >
              <Database size={18} /> Postgres DB
            </button>
            <button 
              onClick={() => setActiveTab('vector')}
              className={`p-3 rounded-lg flex items-center gap-3 transition ${activeTab === 'vector' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
            >
              <Table size={18} /> Vector DB
            </button>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 h-screen flex flex-col">
          {activeTab === 'chat' && (
            <>
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-2xl p-4 rounded-2xl flex gap-3 ${msg.role === 'user' ? 'bg-blue-700 text-white' : 'bg-gray-800 text-gray-200'}`}>
                      {msg.role === 'assistant' ? <Bot size={20} className="mt-1 flex-shrink-0" /> : <User size={20} className="mt-1 flex-shrink-0" />}
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start italic text-gray-400 animate-pulse">
                    Ассистент думает...
                  </div>
                )}
              </div>

              <div className="p-4 border-t border-gray-700">
                <div className="max-w-4xl mx-auto relative">
                  <input 
                    type="text" 
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Задайте вопрос по законам РК..."
                    className="w-full bg-gray-800 border border-gray-600 rounded-xl p-4 pr-12 focus:outline-none focus:border-blue-500"
                  />
                  <button 
                    onClick={handleSend}
                    disabled={loading}
                    className="absolute right-3 top-3 text-blue-500 hover:text-blue-400 disabled:text-gray-600"
                  >
                    <Send size={24} />
                  </button>
                </div>
              </div>
            </>
          )}

          {activeTab === 'postgres' && (
            <div className="flex-1 overflow-auto p-6">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Database className="text-blue-400" /> PostgreSQL: Последние статьи
              </h2>
              <table className="w-full text-left border-collapse bg-gray-800 rounded-lg overflow-hidden">
                <thead className="bg-gray-700">
                  <tr>
                    <th className="p-3">ID</th>
                    <th className="p-3">Название</th>
                    <th className="p-3">Источник</th>
                    <th className="p-3">Действие</th>
                  </tr>
                </thead>
                <tbody>
                  {dbData.map((a) => (
                    <tr key={a.id} className="border-b border-gray-700 hover:bg-gray-750">
                      <td className="p-3">{a.id}</td>
                      <td className="p-3 truncate max-w-xs">{a.title}</td>
                      <td className="p-3">{a.source_url}</td>
                      <td className="p-3">
                        <button className="text-blue-400 hover:underline" onClick={() => alert(a.content)}>Просмотр</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'vector' && (
            <div className="flex-1 overflow-auto p-6">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Table className="text-blue-400" /> ChromaDB: Последние векторы
              </h2>
              <div className="grid grid-cols-1 gap-4">
                {vectorData.ids.map((id, i) => (
                  <div key={id} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-blue-400 font-mono text-xs">{id}</span>
                      <span className="text-gray-500 text-xs">{vectorData.metadatas[i]?.source}</span>
                    </div>
                    <p className="text-sm text-gray-300">{vectorData.documents[i].substring(0, 300)}...</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
