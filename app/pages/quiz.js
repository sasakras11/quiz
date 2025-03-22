import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import LoadingSpinner from '../components/LoadingSpinner';
import Layout from '../components/Layout';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

export default function Quiz() {
  const router = useRouter();
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [selectedOption, setSelectedOption] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [userInfo, setUserInfo] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [loadingStatus, setLoadingStatus] = useState('Initializing...');
  const [retryCount, setRetryCount] = useState(0);

  const fetchQuestions = async () => {
    try {
      setLoadingStatus('Connecting to server...');
      const response = await fetch(`${API_URL}/api/quiz-questions`);
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      setLoadingStatus('Processing questions...');
      const data = await response.json();
      
      if (!data.questions || !Array.isArray(data.questions) || data.questions.length === 0) {
        throw new Error('Invalid question format received');
      }
      
      setQuestions(data.questions);
      setIsLoading(false);
      setError(null);
    } catch (error) {
      console.error('Error fetching questions:', error);
      setError(error.message || 'Failed to load questions. Please try again.');
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    setIsLoading(true);
    setError(null);
    setRetryCount(prev => prev + 1);
    fetchQuestions();
  };

  useEffect(() => {
    // Get user info from local storage
    const storedUserInfo = localStorage.getItem('userInfo');
    if (!storedUserInfo) {
      router.push('/');
      return;
    }
    
    try {
      const parsedUserInfo = JSON.parse(storedUserInfo);
      if (!parsedUserInfo.name || !parsedUserInfo.companyName || !parsedUserInfo.websiteUrl) {
        throw new Error('Missing required user information');
      }
      setUserInfo(parsedUserInfo);
      setLoadingStatus('Loading questions...');
      fetchQuestions();
    } catch (e) {
      setError('Invalid user data. Please try again.');
      router.push('/');
      return;
    }
  }, [router]);

  const handleOptionSelect = (option) => {
    setSelectedOption(option);
  };

  const handleNext = () => {
    if (!selectedOption) return;

    // Save answer
    setAnswers({
      ...answers,
      [questions[currentQuestionIndex].id]: selectedOption
    });

    // Move to next question or submit if last
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setSelectedOption(null);
    } else {
      handleSubmit();
    }
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      setLoadingStatus('Submitting answers...');
      
      // Transform userInfo to match backend expectations
      const formattedUserInfo = {
        company_name: userInfo.companyName,
        website_url: userInfo.websiteUrl,
        name: userInfo.name,
        role: userInfo.role || null
      };
      
      const response = await fetch(`${API_URL}/api/submit-quiz`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_info: formattedUserInfo,
          answers: Object.entries(answers).map(([id, answer]) => ({
            question_id: parseInt(id),
            answer
          }))
        })
      });

      const data = await response.json();
      console.log('Quiz submission response:', data);

      if (!data.success) {
        throw new Error(data.error || 'Submission failed');
      }

      // Store results in localStorage
      localStorage.setItem('quizResults', JSON.stringify(data));
      console.log('Stored quiz results:', data);

      // Navigate to results page
      router.push('/results');
    } catch (error) {
      console.error('Submission error:', error);
      setError(error.message);
    } finally {
      setSubmitting(false);
    }
  };
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex flex-col justify-center items-center">
        <LoadingSpinner />
        <div className="text-[#2C3E50] text-xl mt-4 mb-4">{loadingStatus}</div>
        {error && retryCount < 3 && (
          <div className="text-red-500 text-center max-w-md px-4">
            <p className="mb-4">{error}</p>
            <button
              onClick={handleRetry}
              className="bg-[#2C3E50] text-white px-6 py-2 rounded-lg hover:bg-[#1a2530] mr-4"
            >
              Try Again
            </button>
            <button
              onClick={() => router.push('/')}
              className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600"
            >
              Return to Home
            </button>
          </div>
        )}
        {error && retryCount >= 3 && (
          <div className="text-red-500 text-center max-w-md px-4">
            <p className="mb-4">Unable to load the quiz. Please try again later.</p>
            <button
              onClick={() => router.push('/')}
              className="bg-[#2C3E50] text-white px-6 py-2 rounded-lg hover:bg-[#1a2530]"
            >
              Return to Home
            </button>
          </div>
        )}
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white flex flex-col justify-center items-center">
        <div className="text-red-500 text-center max-w-md px-4">
          <p className="text-xl mb-4">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="bg-[#2C3E50] text-white px-6 py-2 rounded-lg hover:bg-[#1a2530]"
          >
            Return to Home
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <div className="min-h-screen bg-white">
      <Head>
        <title>Quiz | Viral Tech Video Script Generator</title>
        <meta name="description" content="Take our personality quiz to find your perfect influencer match" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </Head>

      <main className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <div className="text-[#2C3E50] mb-4">
            Question {currentQuestionIndex + 1} of {questions.length}
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className="bg-[#2C3E50] h-2.5 rounded-full" 
              style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8 max-w-2xl mx-auto">
          <h2 className="text-2xl font-semibold text-[#2C3E50] mb-8">
            {currentQuestion.text}
          </h2>
          
          <div className="space-y-4 mb-8">
            {currentQuestion.options.map((option) => (
              <button
                key={option.value}
                onClick={() => handleOptionSelect(option.value)}
                className={`w-full text-left px-6 py-4 rounded-lg transition-colors duration-200 focus:outline-none ${
                  selectedOption === option.value 
                    ? 'bg-[#2C3E50] text-white' 
                    : 'bg-[#E5E7EB] text-[#2C3E50] hover:bg-gray-300'
                }`}
              >
                <div className="flex items-center">
                  <div className="mr-3 flex items-center justify-center w-6 h-6 rounded-full border-2 border-current">
                    {selectedOption === option.value && (
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                        <path fillRule="evenodd" d="M19.916 4.626a.75.75 0 01.208 1.04l-9 13.5a.75.75 0 01-1.154.114l-6-6a.75.75 0 011.06-1.06l5.353 5.353 8.493-12.739a.75.75 0 011.04-.208z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                  <span>{option.text}</span>
                </div>
              </button>
            ))}
          </div>
          
          <button
            onClick={handleNext}
            disabled={!selectedOption || submitting}
            className="w-full bg-[#2C3E50] text-white py-3 rounded-lg font-medium text-lg hover:bg-[#1a2530] transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#2C3E50] disabled:opacity-50"
          >
            {currentQuestionIndex < questions.length - 1 ? 'Next' : 'Submit'}
          </button>
        </div>
      </main>
    </div>
  );
}