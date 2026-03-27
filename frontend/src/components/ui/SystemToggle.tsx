import { motion } from 'motion/react';

interface Option {
  value: string;
  label: string;
}

interface SystemToggleProps {
  options: Option[];
  value: string;
  onChange: (val: string) => void;
}

export const SystemToggle = ({ options, value, onChange }: SystemToggleProps) => {
  return (
    <div className="relative flex p-1 bg-black/40 backdrop-blur-md border border-white/10 rounded-full w-full max-w-[320px] mx-auto">
      {options.map((opt) => {
        const isActive = value === opt.value;
        return (
          <button
            key={opt.value}
            onClick={(e) => {
              e.preventDefault();
              onChange(opt.value);
            }}
            className={`relative flex-1 py-2.5 text-xs uppercase tracking-widest font-bold rounded-full transition-colors z-10 ${
              isActive ? 'text-space-900' : 'text-gray-400 hover:text-white'
            }`}
          >
            {isActive && (
              <motion.div
                layoutId="system-toggle-bg"
                className="absolute inset-0 bg-gold-primary rounded-full shadow-[0_0_12px_rgba(212,168,75,0.4)]"
                transition={{ type: 'spring', bounce: 0.25, duration: 0.5 }}
              />
            )}
            <span className="relative z-20">{opt.label}</span>
          </button>
        );
      })}
    </div>
  );
};