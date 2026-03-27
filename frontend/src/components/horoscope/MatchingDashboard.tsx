import { motion } from 'motion/react';
import { useAppStore } from '../../store/appStore';
import { MatchingHero } from './MatchingHero';
import { DoshaAlerts } from './DoshaAlerts';
import { AshtaKootaGrid } from './AshtaKootaGrid';
import { MatchingDeepDive } from './MatchingDeepDive';

export const MatchingDashboard = () => {
  const { matchingData, matchingInput } = useAppStore();
  if (!matchingData) return null;

  // We only show Ashta Koota grid if system is 'north_indian' or 'both'
  const showAshtaKoota = matchingInput?.system === 'north_indian' || matchingInput?.system === 'both';

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

      {/* ---------------- LAYER 3: 8-FOLD GRID (North Indian) ---------------- */}
      {showAshtaKoota && (
        <motion.div variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}>
          <AshtaKootaGrid />
        </motion.div>
      )}

      {/* ---------------- LAYER 4: DEEP DIVE ACCORDIONS ---------------- */}
      <motion.div variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}>
        <MatchingDeepDive />
      </motion.div>

    </motion.div>
  );
};