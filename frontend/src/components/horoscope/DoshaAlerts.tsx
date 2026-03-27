import { useAppStore } from '../../store/appStore';
import { AlertOctagon } from 'lucide-react';
import { motion } from 'motion/react';

export const DoshaAlerts = () => {
  const { matchingData } = useAppStore();
  if (!matchingData) return null;

  const { vedha, manglik_dosha, kootas } = matchingData;
  const alerts: { title: string; desc: string }[] = [];

  // Vedha Dosha (Mutual Repulsion)
  if (vedha.has_vedha) {
    alerts.push({
      title: 'Vedha Dosha Detected',
      desc: vedha.description,
    });
  }

  // Papasamyam (Dosha Samyam Balance)
  if (matchingData.papasamyam && !matchingData.papasamyam.compatibility.is_compatible) {
    alerts.push({
      title: 'Papasamyam Mismatch',
      desc: matchingData.papasamyam.compatibility.description,
    });
  }

  // Manglik Dosha (Mars Affliction)
  if (!manglik_dosha.both_manglik_cancellation) {
    if (manglik_dosha.bride.is_manglik && !manglik_dosha.bride.is_cancelled) {
      alerts.push({
        title: 'Bride: Manglik Dosha',
        desc: manglik_dosha.bride.description,
      });
    }
    if (manglik_dosha.groom.is_manglik && !manglik_dosha.groom.is_cancelled) {
      alerts.push({
        title: 'Groom: Manglik Dosha',
        desc: manglik_dosha.groom.description,
      });
    }
  }

  // Bhakoot Dosha (Emotional Disharmony)
  if (kootas?.bhakoot?.dosha_present && !kootas?.bhakoot?.dosha_cancelled) {
    alerts.push({
      title: 'Bhakoot Dosha',
      desc: kootas.bhakoot.description,
    });
  }

  // Nadi Dosha (Genetic/Health Risk)
  if (kootas?.nadi?.dosha_present && !kootas?.nadi?.dosha_cancelled) {
    alerts.push({
      title: 'Nadi Dosha',
      desc: kootas.nadi.description,
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