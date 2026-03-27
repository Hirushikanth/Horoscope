import { type SelectHTMLAttributes, forwardRef } from 'react';
import { ChevronDown } from 'lucide-react';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  options: { value: string; label: string }[];
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, id, options, ...props }, ref) => {
    return (
      <div className="relative w-full group mb-6">
        <select
          id={id}
          ref={ref}
          className="peer w-full appearance-none bg-transparent border-b border-white/20 px-0 py-2 text-white focus:outline-none focus:border-gold-primary transition-colors duration-300 cursor-pointer"
          {...props}
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value} className="bg-space-800 text-white py-2">
              {opt.label}
            </option>
          ))}
        </select>
        
        <label
          htmlFor={id}
          className="absolute left-0 -top-4 text-xs text-gold-primary pointer-events-none transition-all duration-300"
        >
          {label}
        </label>
        
        {/* Animated Bottom Glow */}
        <div className="absolute bottom-0 left-0 h-[2px] w-0 bg-gold-primary transition-all duration-500 ease-out group-focus-within:w-full shadow-[0_0_10px_rgba(212,168,75,0.5)]"></div>
        
        {/* Dropdown Icon */}
        <div className="absolute right-0 top-3 pointer-events-none">
          <ChevronDown className="text-gray-400 w-4 h-4 group-hover:text-gold-light transition-colors" />
        </div>
      </div>
    );
  }
);
Select.displayName = 'Select';