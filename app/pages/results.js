import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Image from 'next/image';

const influencerInfo = {
  "Hormozi": {
    name: "Alex Hormozi",
    image: "/images/eov911dsc81vaj73li2pag9pt7.jpg",
    description: "The strategist—direct, no fluff. Known for clear, actionable business advice that cuts through the noise.",
    style: "Direct, strategic, value-focused"
  },
  "MrBeast": {
    name: "MrBeast",
    image: "/images/beast.jpeg",
    description: "The showman—big, bold, action-first. Famous for challenge-based content with dramatic reveals.",
    style: "High-energy, challenge-based, dramatic"
  },
  "Gary": {  // Note: frontend expects "Gary", not "Gary Vee"
    name: "Gary Vaynerchuk",
    image: "/images/gary.jpeg",
    description: "The hustler—direct, motivational, no-nonsense...",
    style: "Motivational, raw, unfiltered"
  },
  "Casey": {
    name: "Casey Neistat",
    image: "/images/casey.jpeg",
    description: "The storyteller—visual, personal, wandering. Master of visual narrative and authentic storytelling.",
    style: "Narrative-driven, visual, personal"
  },
  "Emma": {
    name: "Emma Chamberlain",
    image: "/images/emma.webp",
    description: "The friend—loose, quirky, real. Known for relatable, authentic content with a personal touch.",
    style: "Casual, authentic, relatable"
  },
  "Lilly": {
    name: "Lilly Singh",
    image: "/images/lily.jpg",
    description: "The comedian—sharp, fun, uplifting. Specializes in entertaining educational content.",
    style: "Comedic, energetic, entertaining"
  }
};

export default function Results() {
  const router = useRouter();
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [shareUrl, setShareUrl] = useState('');

  useEffect(() => {
    // Get results from local storage
    const storedResults = localStorage.getItem('quizResults');
    console.log('Stored results:', storedResults); // Debug log
    
    if (!storedResults) {
      console.log('No results found in localStorage'); // Debug log
      router.push('/');
      return;
    }
    
    try {
      const parsedResults = JSON.parse(storedResults);
      console.log('Parsed results:', parsedResults); // Debug log
      console.log('Available influencers:', Object.keys(influencerInfo)); // Debug log
      
      if (!parsedResults || !parsedResults.influencer || !influencerInfo[parsedResults.influencer]) {
        console.error('Invalid results structure:', parsedResults); // Debug log
        throw new Error('Invalid results format');
      }
      
      setResults(parsedResults);
      setIsLoading(false);
      
      // Set share URL
      setShareUrl(window.location.href);
    } catch (error) {
      console.error('Error processing results:', error); // Debug log
      router.push('/');
    }
  }, [router]);

  const handleShare = (platform) => {
    const text = `I got matched with ${results.influencer} for my tech videos! Take the quiz to find your match:`;
    const url = shareUrl;
    
    switch (platform) {
      case 'twitter':
        window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank');
        break;
      case 'linkedin':
        window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`, '_blank');
        break;
      case 'facebook':
        window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, '_blank');
        break;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex justify-center items-center">
        <div className="text-[#2C3E50] text-xl">Loading results...</div>
      </div>
    );
  }

  if (!results || !results.influencer || !influencerInfo[results.influencer]) {
    return (
      <div className="min-h-screen bg-white flex justify-center items-center">
        <div className="text-[#2C3E50] text-xl">
          Error: Invalid results. Please <button 
            onClick={() => {
              localStorage.clear();
              router.push('/');
            }}
            className="text-blue-600 underline"
          >
            start over
          </button>
        </div>
      </div>
    );
  }

  const influencerData = influencerInfo[results.influencer];

  return (
    <div className="min-h-screen bg-white">
      <Head>
        <title>Your Match | Viral Tech Video Script Generator</title>
        <meta name="description" content="Your personalized influencer match" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </Head>

      <main className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-[#2C3E50] mb-4">
            Your Match
          </h1>
          <p className="text-xl text-[#2C3E50]">
            You've been matched with the perfect influencer for your tech videos!
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-semibold text-[#2C3E50] mb-2">
              You've been matched with
            </h2>
            <div className="text-3xl font-bold text-[#2C3E50]">
              {influencerData.name}
            </div>
            <div className="text-[#2C3E50] italic">
              {influencerData.style}
            </div>
          </div>

          <div className="flex items-center justify-center mb-8">
            <div className="relative w-48 h-48">
              <Image
                src={influencerData.image}
                alt={influencerData.name}
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                className="rounded-full object-cover"
                priority
              />
            </div>
          </div>

          <div className="flex flex-col gap-4">
            <button
              onClick={() => router.push('/scripts')}
              className="w-full bg-[#2C3E50] text-white py-3 px-6 rounded-lg font-medium text-lg hover:bg-[#1a2530] transition-colors duration-300"
            >
              Show My Video Scripts
            </button>

            <div className="text-center text-[#2C3E50] font-semibold mb-2">
              Share your match
            </div>
            
            <div className="flex justify-center gap-4">
              <button
                onClick={() => handleShare('twitter')}
                className="bg-[#1DA1F2] text-white p-3 rounded-full hover:bg-[#1a90d9]"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                </svg>
              </button>
              
              <button
                onClick={() => handleShare('linkedin')}
                className="bg-[#0A66C2] text-white p-3 rounded-full hover:bg-[#095196]"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </button>
              
              <button
                onClick={() => handleShare('facebook')}
                className="bg-[#1877F2] text-white p-3 rounded-full hover:bg-[#166fe5]"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </button>
            </div>
          </div>
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