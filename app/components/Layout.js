import Head from 'next/head';

export default function Layout({ children, title, description }) {
  return (
    <div className="min-h-screen bg-white">
      <Head>
        <title>{title || 'Viral Tech Video Script Generator'}</title>
        <meta name="description" content={description || 'Create viral tech videos with your perfect influencer match'} />
        <link rel="icon" href="/favicon.ico" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </Head>

      <main className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {children}
      </main>

      <footer className="max-w-4xl mx-auto px-4 py-8 text-center text-[#2C3E50]">
        <p>© {new Date().getFullYear()} Viral Tech Video Script Generator. All rights reserved.</p>
      </footer>
    </div>
  );
} 