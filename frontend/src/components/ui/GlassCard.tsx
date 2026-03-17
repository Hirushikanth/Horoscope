import { motion } from "motion/react";
import type { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  delay?: number;
  hoverEffect?: boolean;
}

export const GlassCard = ({ children, className = "", delay = 0, hoverEffect = true }: GlassCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30, filter: "blur(10px)" }}
      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      transition={{ 
        duration: 0.8, 
        delay, 
        ease: [0.16, 1, 0.3, 1] 
      }}
      whileHover={hoverEffect ? { 
        y: -4, 
        scale: 1.01,
        boxShadow: "0 20px 40px rgba(212, 168, 75, 0.08)"
      } : {}}
      className={`glass-card ${className}`}
    >
      <div className="relative z-10 w-full h-full text-white">
        {children}
      </div>
    </motion.div>
  );
};