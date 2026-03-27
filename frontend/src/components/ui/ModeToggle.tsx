import { motion } from 'motion/react';
import { useAppStore } from '../../store/appStore';

const tabs = [
  { id: 'horoscope', label: 'Individual Chart' },
  { id: 'matching', label: 'Kundali Matching' },
] as const;

export const ModeToggle = () => {
  const { mode, setMode } = useAppStore();

  return (
    <div className="relative flex space-x-1 bg-white/5 backdrop-blur-md border border-white/10 p-1 rounded-full max-w-xs mx-auto mb-8">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => setMode(tab.id)}
          className={`relative w-full py-2.5 text-xs font-medium uppercase tracking-widest rounded-full transition-colors duration-300 z-10 ${
            mode === tab.id ? 'text-space-900 font-bold' : 'text-gray-400 hover:text-white'
          }`}
        >
          {mode === tab.id && (
            <motion.div
              layoutId="active-pill"
              className="absolute inset-0 bg-gold-primary rounded-full shadow-[0_0_15px_rgba(212,168,75,0.4)]"
              transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
            />
          )}
          <span className="relative z-20">{tab.label}</span>
        </button>
      ))}
    </div>
  );
};