import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

export default function Quiz() {
  const router = useRouter();
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [selectedOption, setSelectedOption] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [userInfo, setUserInfo] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    // Get user info from local storage
    const storedUserInfo = localStorage.getItem('userInfo');
    if (!storedUserInfo) {
      router.push('/');
      return;
    }
    
    setUserInfo(JSON.parse(storedUserInfo));
    
    // Fetch quiz questions
    const fetchQuestions = async () => {
      try {
        // In a real app, this would be fetched from the API
        // const response = await fetch('http://localhost:8000/api/quiz-questions');
        // const data = await response.json();
        // setQuestions(data.questions);
        
        // Using mock data for now
        setQuestions([
          {
            id: 1,
            text: "What's your industry?",
            options: [
              { value: "A", text: "Tech" },
              { value: "B", text: "SaaS" },
              { value: "C", text: "E-commerce" },
              { value: "D", text: "Finance" },
              { value: "E", text: "Healthcare" },
              { value: "F", text: "Education" },
              { value: "G", text: "Other" }
            ]
          },
          {
            id: 2,
            text: "How would you describe your communication style?",
            options: [
              { value: "A", text: "Direct and bold" },
              { value: "B", text: "Analytical and methodical" },
              { value: "C", text: "Storytelling and relatable" },
              { value: "D", text: "Humorous and entertaining" },
              { value: "E", text: "Casual and conversational" }
            ]
          },
          {
            id: 3,
            text: "What's your approach to content creation?",
            options: [
              { value: "A", text: "High-energy and attention-grabbing" },
              { value: "B", text: "Educational and informative" },
              { value: "C", text: "Thought-provoking and insightful" },
              { value: "D", text: "Authentic and personal" },
              { value: "E", text: "Quick and to-the-point" }
            ]
          },
          {
            id: 4,
            text: "What do you value most in content?",
            options: [
              { value: "A", text: "Entertainment value" },
              { value: "B", text: "Practical usefulness" },
              { value: "C", text: "Emotional connection" },
              { value: "D", text: "Unique perspective" },
              { value: "E", text: "Clear communication" }
            ]
          },
          {
            id: 5,
            text: "How would you handle talking about technical details?",
            options: [
              { value: "A", text: "Simplify with analogies and examples" },
              { value: "B", text: "Deep dive into the specifics" },
              { value: "C", text: "Focus on benefits and outcomes" },
              { value: "D", text: "Use humor to make it digestible" },
              { value: "E", text: "Compare with familiar concepts" }
            ]
          },
          {
            id: 6,
            text: "What would your video thumbnail style be?",
            options: [
              { value: "A", text: "Shocked expression with bold text" },
              { value: "B", text: "Clean product shot with minimal text" },
              { value: "C", text: "You in action with a clear value prop" },
              { value: "D", text: "Humorous scene or meme format" },
              { value: "E", text: "Before/after demonstration" }
            ]
          },
          {
            id: 7,
            text: "What's your preferred video pacing?",
            options: [
              { value: "A", text: "Fast-paced with lots of cuts" },
              { value: "B", text: "Methodical and measured" },
              { value: "C", text: "Dynamic with storytelling arcs" },
              { value: "D", text: "Unpredictable with pattern interrupts" },
              { value: "E", text: "Conversational with natural flow" }
            ]
          },
          {
            id: 8,
            text: "How would you handle criticism or competition?",
            options: [
              { value: "A", text: "Turn it into a challenge or contest" },
              { value: "B", text: "Analyze it objectively with data" },
              { value: "C", text: "Share the journey and lessons learned" },
              { value: "D", text: "Use humor and self-awareness" },
              { value: "E", text: "Focus on differentiation and unique value" }
            ]
          },
          {
            id: 9,
            text: "What would your call-to-action style be?",
            options: [
              { value: "A", text: "High-energy challenge or dare" },
              { value: "B", text: "Data-backed recommendation" },
              { value: "C", text: "Authentic invitation to connect" },
              { value: "D", text: "Unexpected or humorous twist" },
              { value: "E", text: "Clear and direct value proposition" }
            ]
          },
          {
            id: 10,
            text: "You just went viral! What's your first thought?",
            options: [
              { value: "A", text: "How can I double down on this success?" },
              { value: "B", text: "What metrics can I analyze to understand why?" },
              { value: "C", text: "My authentic story really resonated!" },
              { value: "D", text: "The humor and hook really worked!" },
              { value: "E", text: "Time to make another similar video!" }
            ]
          }
        ]);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching questions:', error);
        setIsLoading(false);
      }
    };

    fetchQuestions();
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
    setSubmitting(true);
    
    try {
      // Prepare the answers in the format the API expects
      const finalAnswers = {
        ...answers,
        [questions[currentQuestionIndex].id]: selectedOption
      };
      
      const quizAnswers = Object.keys(finalAnswers).map(questionId => ({
        question_id: parseInt(questionId),
        answer: finalAnswers[questionId]
      }));
      
      // Prepare the payload
      const payload = {
        user_info: {
          name: userInfo.name,
          company_name: userInfo.companyName,
          website_url: userInfo.websiteUrl,
          role: userInfo.role || null
        },
        answers: quizAnswers
      };
      
      // Store the answers in localStorage (in a real app, this would be sent to the API)
      localStorage.setItem('quizAnswers', JSON.stringify(payload));
      
      // In a real app, this would be sent to the API
      // const response = await fetch('http://localhost:8000/api/submit-quiz', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify(payload),
      // });
      
      // For now, create some mock results
      const mockResults = {
        influencer: "MrBeast",
        influencer_style: "High-energy, bold, challenge-driven",
        company_summary: [
          `${userInfo.companyName} recently launched a new AI-powered feature that increases productivity by 30%`,
          `The company focuses on solving pain points in the enterprise software market with innovative technology`,
          `A recent case study showed how ${userInfo.companyName} helped a client reduce costs by 25% while improving results`
        ],
        ideas: [
          {
            title: "I Challenged My Team to 10X Our Conversion Rate",
            description: "A challenge-based video showing the extreme tactics used to dramatically improve conversion rates, with a surprising twist at the end."
          },
          {
            title: "We Built a Game-Changing Feature in Just 24 Hours",
            description: "A time-pressured challenge to create something innovative and record-breaking with your team."
          },
          {
            title: "Giving Away Our Product to Anyone Who Can Beat Me",
            description: "A competition-style video where you challenge users to complete tasks with your product for a reward."
          }
        ],
        scripts: [
          {
            content: `What's up guys! Today we're doing something INSANE! I Challenged My Team to 10X Our Conversion Rate! That's right - we're pushing the limits and seeing just how far we can go. I've challenged my entire team to work non-stop on this, and we're putting $10,000 on the line to make it happen! You won't BELIEVE the results we got. We literally changed the game overnight!`,
            delivery_notes: "Ultra high energy throughout. Wide eyes, big gestures. Emphasize key words with volume changes. Speak faster than normal conversation.",
            editing_notes: "Fast cuts, no clip longer than 3 seconds. Use dramatic zoom effects on key points. Add impact sound effects. Include countdown timer on screen."
          },
          {
            content: `What's up guys! Today we're doing something CRAZY! We Built a Game-Changing Feature in Just 24 Hours! I gave my team exactly 24 hours to create something that would completely revolutionize our product. If they succeeded, I'd give them $5,000 each! If they failed... well, let's just say failure wasn't an option! You have to see what they came up with - it's MIND-BLOWING!`,
            delivery_notes: "Start with extremely high energy and maintain it throughout. Use dramatic pauses before revealing results. Wide-eyed reactions to progress updates.",
            editing_notes: "Use a prominent countdown timer. Quick cuts between team members working. Dramatic music building up to the reveal. Slow motion for the final unveiling."
          },
          {
            content: `Hey everyone! Today I'm doing something I've NEVER done before. I'm Giving Away Our Product to Anyone Who Can Beat Me! That's right - if you can complete these IMPOSSIBLE challenges faster than me, you'll get our premium plan absolutely FREE for LIFE! I've set up three insane challenges that push our product to its limits. First person to beat all three wins! This is going to be EPIC!`,
            delivery_notes: "Extremely high energy and enthusiasm. Act genuinely excited about the challenge. Use big gestures and animated expressions throughout.",
            editing_notes: "Fast-paced editing with quick transitions. Use on-screen graphics for challenge rules and timers. Add sound effects for wins/losses. Include reaction shots from participants."
          }
        ]
      };
      
      // Store the results in localStorage
      localStorage.setItem('quizResults', JSON.stringify(mockResults));
      
      // Navigate to results page
      router.push('/results');
    } catch (error) {
      console.error('Error submitting quiz:', error);
      setSubmitting(false);
    }
  };
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex justify-center items-center">
        <div className="text-[#2C3E50] text-xl">Loading quiz...</div>
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