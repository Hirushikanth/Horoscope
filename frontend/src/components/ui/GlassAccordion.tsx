import { useState, type ReactNode } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ChevronDown } from 'lucide-react';

interface GlassAccordionProps {
  title: ReactNode;
  subtitle?: ReactNode;
  badges?: ReactNode;
  children: ReactNode;
  delay?: number;
}

export const GlassAccordion = ({ title, subtitle, badges, children, delay = 0 }: GlassAccordionProps) => {
  const[isOpen, setIsOpen] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay, ease:[0.16, 1, 0.3, 1] }}
      className="glass-card w-full mb-3 rounded-xl overflow-hidden"
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 md:p-5 text-left bg-transparent hover:bg-white/5 transition-colors group"
      >
        <div className="flex items-center gap-4 flex-1">
          <div className="flex-1">
            <div className="font-cinematic text-xl text-white group-hover:text-gold-light transition-colors">
              {title}
            </div>
            {subtitle && <div className="text-xs text-gray-400 mt-1 uppercase tracking-widest">{subtitle}</div>}
          </div>
          <div className="flex gap-2 mr-4">
            {badges}
          </div>
        </div>
        <motion.div animate={{ rotate: isOpen ? 180 : 0 }} transition={{ duration: 0.3 }}>
          <ChevronDown className="text-gold-primary w-5 h-5 opacity-70" />
        </motion.div>
      </button>

      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="p-4 md:p-5 border-t border-white/10 bg-black/20 text-sm text-gray-300">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};