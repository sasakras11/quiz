import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

export default function Results() {
  const router = useRouter();
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeScriptIndex, setActiveScriptIndex] = useState(0);
  const [copyStatus, setCopyStatus] = useState('');
  const [email, setEmail] = useState('');
  const [emailSent, setEmailSent] = useState(false);

  useEffect(() => {
    // Get results from local storage
    const storedResults = localStorage.getItem('quizResults');
    if (!storedResults) {
      router.push('/');
      return;
    }
    
    setResults(JSON.parse(storedResults));
    setIsLoading(false);
  }, [router]);

  const handleCopyScript = () => {
    const scriptText = `
CONTENT:
${results.scripts[activeScriptIndex].content}

DELIVERY NOTES:
${results.scripts[activeScriptIndex].delivery_notes}

EDITING NOTES:
${results.scripts[activeScriptIndex].editing_notes}
`;

    navigator.clipboard.writeText(scriptText)
      .then(() => {
        setCopyStatus('Script copied to clipboard!');
        setTimeout(() => setCopyStatus(''), 3000);
      })
      .catch(() => {
        setCopyStatus('Failed to copy. Please try again.');
        setTimeout(() => setCopyStatus(''), 3000);
      });
  };

  const handleEmailSubmit = (e) => {
    e.preventDefault();
    
    if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setCopyStatus('Please enter a valid email address.');
      setTimeout(() => setCopyStatus(''), 3000);
      return;
    }
    
    // In a real app, this would send an email
    // For now, just simulate success
    setEmailSent(true);
    setCopyStatus('Scripts sent to your email!');
    setTimeout(() => setCopyStatus(''), 3000);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex justify-center items-center">
        <div className="text-[#2C3E50] text-xl">Loading results...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Head>
        <title>Your Results | Viral Tech Video Script Generator</title>
        <meta name="description" content="Your personalized video scripts in an influencer's style" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </Head>

      <main className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-[#2C3E50] mb-4">
            Your Results
          </h1>
          <p className="text-xl text-[#2C3E50]">
            Here are your personalized video scripts created just for you!
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-semibold text-[#2C3E50] mb-2">
              You've been matched with
            </h2>
            <div className="text-3xl font-bold text-[#2C3E50]">
              {results.influencer}
            </div>
            <div className="text-[#2C3E50] italic">
              {results.influencer_style}
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-xl font-semibold text-[#2C3E50] mb-3">
              Company Information
            </h3>
            <ul className="space-y-2 text-[#2C3E50]">
              {results.company_summary.map((item, index) => (
                <li key={index} className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-xl font-semibold text-[#2C3E50] mb-3">
              Video Ideas
            </h3>
            <div className="grid gap-4 md:grid-cols-3">
              {results.ideas.map((idea, index) => (
                <div
                  key={index}
                  onClick={() => setActiveScriptIndex(index)}
                  className={`cursor-pointer p-4 rounded-lg border-2 transition-all ${
                    activeScriptIndex === index
                      ? 'border-[#2C3E50] bg-[#2C3E50] text-white'
                      : 'border-gray-200 hover:border-[#2C3E50] text-[#2C3E50]'
                  }`}
                >
                  <h4 className="font-semibold mb-2">{idea.title}</h4>
                  <p className={`text-sm ${activeScriptIndex === index ? 'text-gray-200' : 'text-gray-600'}`}>
                    {idea.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h3 className="text-2xl font-semibold text-[#2C3E50] mb-6">
            Your Script
          </h3>
          
          <div className="mb-6">
            <h4 className="text-xl font-semibold text-[#2C3E50] mb-2">
              {results.ideas[activeScriptIndex].title}
            </h4>
            <p className="text-gray-600 mb-4">
              {results.ideas[activeScriptIndex].description}
            </p>
          </div>
          
          <div className="mb-6">
            <h5 className="font-semibold text-[#2C3E50] mb-2">Script Content:</h5>
            <div className="bg-[#F8F9FA] p-4 rounded-lg text-[#2C3E50] mb-4 whitespace-pre-wrap">
              {results.scripts[activeScriptIndex].content}
            </div>
          </div>
          
          <div className="mb-6">
            <h5 className="font-semibold text-[#2C3E50] mb-2">Delivery Notes:</h5>
            <div className="bg-[#F8F9FA] p-4 rounded-lg text-[#2C3E50] mb-4">
              {results.scripts[activeScriptIndex].delivery_notes}
            </div>
          </div>
          
          <div className="mb-8">
            <h5 className="font-semibold text-[#2C3E50] mb-2">Editing Notes:</h5>
            <div className="bg-[#F8F9FA] p-4 rounded-lg text-[#2C3E50]">
              {results.scripts[activeScriptIndex].editing_notes}
            </div>
          </div>
          
          <button
            onClick={handleCopyScript}
            className="w-full bg-[#2C3E50] text-white py-3 px-6 rounded-lg font-medium text-lg hover:bg-[#1a2530] transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#2C3E50] mb-4"
          >
            Copy Script to Clipboard
          </button>
          
          {copyStatus && (
            <div className="text-center text-green-600 mb-4">
              {copyStatus}
            </div>
          )}
          
          {!emailSent ? (
            <form onSubmit={handleEmailSubmit} className="flex flex-col sm:flex-row gap-2">
              <input
                type="email"
                placeholder="Enter your email to receive scripts"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-grow px-4 py-3 rounded-lg bg-[#E5E7EB] text-[#2C3E50] focus:outline-none focus:ring-2 focus:ring-[#2C3E50]"
              />
              <button
                type="submit"
                className="bg-[#2C3E50] text-white py-3 px-6 rounded-lg font-medium hover:bg-[#1a2530] transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#2C3E50]"
              >
                Email Scripts
              </button>
            </form>
          ) : (
            <div className="text-center text-[#2C3E50]">
              Thanks! Your scripts have been sent to your email.
            </div>
          )}
        </div>
        
        <div className="text-center">
          <button
            onClick={() => {
              localStorage.removeItem('userInfo');
              localStorage.removeItem('quizAnswers');
              localStorage.removeItem('quizResults');
              router.push('/');
            }}
            className="text-[#2C3E50] font-medium hover:underline focus:outline-none"
          >
            Start Over
          </button>
        </div>
      </main>
      
      <footer className="max-w-4xl mx-auto px-4 py-8 text-center text-[#2C3E50]">
        <p>© {new Date().getFullYear()} Viral Tech Video Script Generator. All rights reserved.</p>
      </footer>
    </div>
  );
} 