import { useAppStore } from '../../store/appStore';
import { AlertOctagon } from 'lucide-react';
import { motion } from 'motion/react';

export const DoshaAlerts = () => {
  const { matchingData } = useAppStore();
  if (!matchingData) return null;

  const { chevvai_cross_check, verdict } = matchingData;
  const alerts: { title: string; desc: string }[] = [];

  // Failed Rajju / Vedha gates
  const failedGates = Object.entries(verdict.gates).filter(([, status]) => status !== 'ok');
  failedGates.forEach(([gate]) => {
    alerts.push({
      title: `${gate === 'rajju' ? 'Rajju' : 'Vedha'} Gate Failed`,
      desc: `The ${gate === 'rajju' ? 'Rajju' : 'Vedha'} porutham gate has failed, overriding the total score.`,
    });
  });

  // Non-negotiables that failed
  Object.entries(verdict.non_negotiables).forEach(([name, ok]) => {
    if (!ok) {
      alerts.push({
        title: `${name === 'gana' ? 'Gana' : name} Non-negotiable Failed`,
        desc: 'A non-negotiable porutham failed for this match.',
      });
    }
  });

  // Chevvai Dosham mismatch
  if (!chevvai_cross_check.compatible) {
    alerts.push({
      title: 'Chevvai Dosham Mismatch',
      desc: chevvai_cross_check.note,
    });
  }

  if (alerts.length === 0) return null;

  return (
    <div className="w-full space-y-4">
      {alerts.map((alert, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.1 }}
          className="flex items-start gap-4 p-4 rounded-xl border border-red-500/30 bg-red-500/10 backdrop-blur-md relative overflow-hidden"
        >
          {/* Subtle pulse effect */}
          <div className="absolute top-0 left-0 w-2 h-full bg-red-500/50"></div>
          
          <AlertOctagon className="text-red-400 mt-1 flex-shrink-0" size={24} />
          <div>
            <h4 className="text-red-300 font-bold uppercase tracking-widest text-sm mb-1">{alert.title}</h4>
            <p className="text-red-200/80 text-sm leading-relaxed">{alert.desc}</p>
          </div>
        </motion.div>
      ))}
    </div>
  );
};
