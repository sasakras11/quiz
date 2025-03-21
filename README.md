# Viral Tech Video Script Generator

A web application that automates the creation of viral tech video scripts by matching users with influencers based on personality quizzes and generating custom scripts.

## Features

- Personality quiz to match users with tech influencers
- Company data scraping to gather relevant information
- AI-generated video ideas based on the user's company and matched influencer
- Custom scripts written in the influencer's tone
- Clean, responsive UI for both desktop and mobile

## Tech Stack

- **Backend**: FastAPI (Python), SQLite with SQLAlchemy
- **Frontend**: Next.js with Tailwind CSS
- **AI**: DeepSeek API for script generation and data scraping
- **Deployment**: Vercel

## Project Structure

```
project/
├── app/                      # Frontend (Next.js)
│   ├── components/           # React components
│   ├── pages/                # Next.js pages/routes
│   ├── styles/               # CSS styles
│   └── utils/                # Utility functions
├── backend/                  # Backend (FastAPI)
│   ├── models/               # Database models
│   ├── routers/              # API routes
│   ├── services/             # Business logic
│   ├── database.py           # Database connection
│   └── main.py               # Main API application
└── README.md                 # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- DeepSeek API key

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   DATABASE_URL=sqlite:///./quiz_app.db
   ```

5. Run the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the app directory:
   ```
   cd app
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env.local` file:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. Run the development server:
   ```
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Deployment

The application is designed to be deployed on Vercel:

1. Deploy the backend as a serverless function
2. Deploy the frontend to Vercel
3. Set up the environment variables in the Vercel dashboard

## License

This project is licensed under the MIT License - see the LICENSE file for details. 