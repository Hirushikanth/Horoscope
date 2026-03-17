import { motion, type HTMLMotionProps } from 'motion/react';
import type { ReactNode } from 'react';

interface GlowButtonProps extends Omit<HTMLMotionProps<'button'>, 'ref' | 'children'> {
  children: ReactNode;
  isLoading?: boolean;
}

export const GlowButton = ({ children, isLoading, ...props }: GlowButtonProps) => {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="relative w-full py-3 rounded-lg overflow-hidden bg-gold-primary/10 border border-gold-primary/30 text-gold-light font-cinematic text-lg tracking-wider uppercase backdrop-blur-sm group"
      disabled={isLoading}
      {...props}
    >
      {/* Shine effect */}
      <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-gold-primary/30 to-transparent group-hover:animate-[shine_1.5s_infinite]"></div>
      
      <span className="relative z-10 flex items-center justify-center gap-2">
        {isLoading ? (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
            className="w-5 h-5 border-2 border-gold-primary border-t-transparent rounded-full"
          />
        ) : (
          children
        )}
      </span>
    </motion.button>
  );
};