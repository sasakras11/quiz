export default function Button({ 
  children, 
  onClick, 
  type = 'button', 
  disabled = false, 
  variant = 'primary',
  className = ''
}) {
  const baseStyles = 'px-6 py-3 rounded-lg font-medium text-lg transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variants = {
    primary: 'bg-[#2C3E50] text-white hover:bg-[#1a2530] focus:ring-[#2C3E50]',
    secondary: 'bg-gray-500 text-white hover:bg-gray-600 focus:ring-gray-500',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variants[variant]} ${disabled ? 'opacity-70 cursor-not-allowed' : ''} ${className}`}
    >
      {children}
    </button>
  );
} 