import { motion } from 'motion/react';
import { useAppStore } from '../../store/appStore';
import { MatchingHero } from './MatchingHero';
import { DoshaAlerts } from './DoshaAlerts';
import { PoruthamsGrid } from './PoruthamsGrid';

export const MatchingDashboard = () => {
  const { matchingData } = useAppStore();
  if (!matchingData) return null;

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        visible: { transition: { staggerChildren: 0.15 } }
      }}
      className="w-full max-w-6xl mx-auto space-y-8"
    >
      {/* ---------------- LAYER 1: THE VERDICT RING ---------------- */}
      <motion.div variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}>
        <MatchingHero />
      </motion.div>

      {/* ---------------- LAYER 2: DOSHA ALERTS (Red Warnings) ---------------- */}
      <motion.div variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}>
        <DoshaAlerts />
      </motion.div>

      {/* ---------------- LAYER 3: KALYANA PORUTHAM GRID ---------------- */}
      <motion.div variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}>
        <PoruthamsGrid />
      </motion.div>

    </motion.div>
  );
};
