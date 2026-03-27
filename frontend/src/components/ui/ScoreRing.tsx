import { motion } from 'motion/react';
import { useEffect, useState } from 'react';

interface ScoreRingProps {
  score: number;
  maxScore: number;
  size?: number;
  strokeWidth?: number;
}

export const ScoreRing = ({ score, maxScore, size = 200, strokeWidth = 8 }: ScoreRingProps) => {
  const [animatedScore, setAnimatedScore] = useState(0);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const percentage = (score / maxScore) * 100;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  // Determine color based on score tier
  const colorClass = 
    percentage >= 80 ? 'text-green-400' :
    percentage >= 50 ? 'text-gold-primary' :
    'text-red-400';

  // Number counter animation effect
  useEffect(() => {
    let startTime: number;
    const duration = 1500; // 1.5 seconds

    const animateNumber = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      
      // Easing function (easeOutQuart)
      const easeProgress = 1 - Math.pow(1 - progress, 4);
      setAnimatedScore(Number((easeProgress * score).toFixed(1)));

      if (progress < 1) {
        requestAnimationFrame(animateNumber);
      } else {
        setAnimatedScore(score);
      }
    };

    requestAnimationFrame(animateNumber);
  }, [score]);

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          className="text-white/10"
        />
        {/* Animated progress ring */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1] }}
          strokeLinecap="round"
          className={`drop-shadow-[0_0_8px_currentColor] ${colorClass}`}
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className="font-cinematic text-5xl font-bold text-white drop-shadow-lg">
          {animatedScore}
        </span>
        <span className="text-gray-400 text-sm tracking-widest uppercase mt-1">
          out of {maxScore}
        </span>
      </div>
    </div>
  );
};