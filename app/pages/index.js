import { useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

export default function Home() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    companyName: '',
    websiteUrl: '',
    role: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user types
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.companyName.trim()) newErrors.companyName = 'Company name is required';
    
    // More flexible URL validation
    if (!formData.websiteUrl.trim()) {
      newErrors.websiteUrl = 'Website URL is required';
    } else {
      // Clean up the URL
      let url = formData.websiteUrl.trim().toLowerCase();
      
      // Remove any trailing slashes
      url = url.replace(/\/+$/, '');
      
      // If it's just a domain, add https://
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
      }
      
      try {
        const urlObj = new URL(url);
        // Make sure there's a valid domain with at least one dot
        if (!urlObj.hostname.includes('.')) {
          throw new Error('Invalid domain');
        }
        // Update the URL in the form data with the cleaned version
        setFormData(prev => ({
          ...prev,
          websiteUrl: url
        }));
      } catch (e) {
        newErrors.websiteUrl = 'Please enter a valid domain (e.g., company.com)';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    
    // Store form data in local storage to access in quiz
    localStorage.setItem('userInfo', JSON.stringify(formData));
    
    // Navigate to quiz page
    router.push('/quiz');
  };

  return (
    <div className="min-h-screen bg-white">
      <Head>
        <title>Viral Tech Video Script Generator</title>
        <meta name="description" content="Create viral tech videos with your perfect influencer match" />
        <link rel="icon" href="/favicon.ico" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </Head>

      <main className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-[#2C3E50] mb-4">
            Create Viral Tech Videos with Your Perfect Influencer Match!
          </h1>
          <p className="text-xl text-[#2C3E50] mb-8">
            Take our fun quiz to get matched with an influencer and receive 3 custom video scripts for your company.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8 max-w-2xl mx-auto">
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label htmlFor="name" className="block text-[#2C3E50] font-medium mb-2">Name</label>
              <input
                type="text"
                id="name"
                name="name"
                className={`w-full px-4 py-3 rounded-lg bg-[#E5E7EB] text-[#2C3E50] focus:outline-none focus:ring-2 focus:ring-[#2C3E50] ${errors.name ? 'border-2 border-red-500' : ''}`}
                placeholder="Your name"
                value={formData.name}
                onChange={handleChange}
              />
              {errors.name && <p className="mt-1 text-red-500 text-sm">{errors.name}</p>}
            </div>

            <div className="mb-6">
              <label htmlFor="companyName" className="block text-[#2C3E50] font-medium mb-2">Company Name</label>
              <input
                type="text"
                id="companyName"
                name="companyName"
                className={`w-full px-4 py-3 rounded-lg bg-[#E5E7EB] text-[#2C3E50] focus:outline-none focus:ring-2 focus:ring-[#2C3E50] ${errors.companyName ? 'border-2 border-red-500' : ''}`}
                placeholder="Your company name"
                value={formData.companyName}
                onChange={handleChange}
              />
              {errors.companyName && <p className="mt-1 text-red-500 text-sm">{errors.companyName}</p>}
            </div>

            <div className="mb-6">
              <label htmlFor="websiteUrl" className="block text-[#2C3E50] font-medium mb-2">Website URL</label>
              <input
                type="text"
                id="websiteUrl"
                name="websiteUrl"
                className={`w-full px-4 py-3 rounded-lg bg-[#E5E7EB] text-[#2C3E50] focus:outline-none focus:ring-2 focus:ring-[#2C3E50] ${errors.websiteUrl ? 'border-2 border-red-500' : ''}`}
                placeholder="https://yourcompany.com"
                value={formData.websiteUrl}
                onChange={handleChange}
              />
              {errors.websiteUrl && <p className="mt-1 text-red-500 text-sm">{errors.websiteUrl}</p>}
            </div>

            <div className="mb-8">
              <label htmlFor="role" className="block text-[#2C3E50] font-medium mb-2">Role (Optional)</label>
              <input
                type="text"
                id="role"
                name="role"
                className="w-full px-4 py-3 rounded-lg bg-[#E5E7EB] text-[#2C3E50] focus:outline-none focus:ring-2 focus:ring-[#2C3E50]"
                placeholder="Your role at the company"
                value={formData.role}
                onChange={handleChange}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-[#2C3E50] text-white py-3 px-6 rounded-lg font-medium text-lg hover:bg-[#1a2530] transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#2C3E50] disabled:opacity-70"
            >
              {isLoading ? 'Loading...' : 'Start Quiz'}
            </button>
          </form>
        </div>
      </main>

      <footer className="max-w-4xl mx-auto px-4 py-8 text-center text-[#2C3E50]">
        <p>© {new Date().getFullYear()} Viral Tech Video Script Generator. All rights reserved.</p>
      </footer>
    </div>
  );
} 