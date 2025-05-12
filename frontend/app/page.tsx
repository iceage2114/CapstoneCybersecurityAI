import Link from 'next/link';
import { FaShieldAlt, FaComments, FaPuzzlePiece } from 'react-icons/fa';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <div className="text-center mb-12">
        <div className="flex justify-center mb-4">
          <FaShieldAlt className="text-6xl text-primary-600" />
        </div>
        <h1 className="text-4xl font-bold mb-4">Cybersecurity AI Assistant</h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl">
          Your personal cybersecurity analyst at your fingertips. Get expert advice, threat analysis, and security recommendations powered by AI.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl w-full">
        <Link href="/chat" className="group">
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 transition-all hover:shadow-lg hover:border-primary-500 dark:hover:border-primary-500">
            <div className="flex items-center mb-4">
              <FaComments className="text-3xl text-primary-600 mr-3" />
              <h2 className="text-2xl font-semibold">Start a Conversation</h2>
            </div>
            <p className="text-gray-600 dark:text-gray-300">
              Chat with your AI cybersecurity assistant to get answers to your security questions and concerns.
            </p>
          </div>
        </Link>

        <Link href="/plugins" className="group">
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 transition-all hover:shadow-lg hover:border-primary-500 dark:hover:border-primary-500">
            <div className="flex items-center mb-4">
              <FaPuzzlePiece className="text-3xl text-primary-600 mr-3" />
              <h2 className="text-2xl font-semibold">Manage Plugins</h2>
            </div>
            <p className="text-gray-600 dark:text-gray-300">
              Create and manage plugins to extend the capabilities of your cybersecurity assistant.
            </p>
          </div>
        </Link>
      </div>

      <div className="mt-12 max-w-4xl w-full">
        <h2 className="text-2xl font-semibold mb-4">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div className="text-primary-600 font-bold text-xl mb-2">1. Ask a Question</div>
            <p className="text-gray-600 dark:text-gray-300">
              Type your cybersecurity question or concern in the chat interface.
            </p>
          </div>
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div className="text-primary-600 font-bold text-xl mb-2">2. Get AI Analysis</div>
            <p className="text-gray-600 dark:text-gray-300">
              Our AI processes your query and provides expert cybersecurity insights.
            </p>
          </div>
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div className="text-primary-600 font-bold text-xl mb-2">3. Use Plugins</div>
            <p className="text-gray-600 dark:text-gray-300">
              Extend functionality with specialized plugins for specific security tools and services.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
