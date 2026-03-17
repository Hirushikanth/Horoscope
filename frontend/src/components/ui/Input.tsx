import { type InputHTMLAttributes, forwardRef } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, id, ...props }, ref) => {
    return (
      <div className="relative w-full group mb-6">
        <input
          id={id}
          ref={ref}
          className="peer w-full bg-transparent border-b border-white/20 px-0 py-2 text-white placeholder-transparent focus:outline-none focus:border-gold-primary transition-colors duration-300"
          placeholder={label}
          {...props}
        />
        <label
          htmlFor={id}
          className="absolute left-0 top-2 text-white/50 text-sm transition-all duration-300 peer-placeholder-shown:text-base peer-placeholder-shown:top-2 peer-focus:-top-4 peer-focus:text-xs peer-focus:text-gold-primary peer-valid:-top-4 peer-valid:text-xs pointer-events-none"
        >
          {label}
        </label>
        {/* Animated Bottom Glow */}
        <div className="absolute bottom-0 left-0 h-[2px] w-0 bg-gold-primary transition-all duration-500 ease-out group-focus-within:w-full shadow-[0_0_10px_rgba(212,168,75,0.5)]"></div>
      </div>
    );
  }
);
Input.displayName = 'Input';