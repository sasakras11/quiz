export default function Input({
  id,
  name,
  type = 'text',
  label,
  value,
  onChange,
  placeholder,
  error,
  required = false,
  className = ''
}) {
  return (
    <div className={`mb-6 ${className}`}>
      <label htmlFor={id} className="block text-[#2C3E50] font-medium mb-2">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input
        type={type}
        id={id}
        name={name}
        className={`w-full px-4 py-3 rounded-lg bg-[#E5E7EB] text-[#2C3E50] focus:outline-none focus:ring-2 focus:ring-[#2C3E50] ${error ? 'border-2 border-red-500' : ''}`}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        required={required}
      />
      {error && <p className="mt-1 text-red-500 text-sm">{error}</p>}
    </div>
  );
} 