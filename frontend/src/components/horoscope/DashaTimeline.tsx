import { useState } from 'react';
import { useAppStore } from '../../store/appStore';
import { motion, AnimatePresence } from 'motion/react';
import { ChevronDown, Clock } from 'lucide-react';
import type { DashaPeriodInfo, JathakamResponse } from '../../types';

// Helper: extract YYYY-MM-DD from an ISO 8601 UTC timestamp
const toDate = (iso: string) => iso.slice(0, 10);

const isCurrentPeriod = (start: string, end: string) => {
  const today = new Date();
  return today >= new Date(start) && today <= new Date(end);
};

export const DashaTimeline = () => {
  const { horoscopeData } = useAppStore();
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [autoExpandedFor, setAutoExpandedFor] = useState<JathakamResponse | null>(null);

  const periods = horoscopeData?.dasha?.periods ?? [];
  const balance = horoscopeData?.dasha?.balance;

  const mahadashas = periods.filter((p) => p.category === 'mahadasha');
  const antardashasOf = (maha: DashaPeriodInfo) =>
    periods.filter(
      (p) => p.category === 'antardasha' && p.start_jd >= maha.start_jd && p.end_jd <= maha.end_jd,
    );

  const effectiveYears = (p: DashaPeriodInfo) => p.years + p.days / 365.25;

  // Auto-expand the current Mahadasha once per payload (guarded state
  // adjustment during render — the documented pattern for "derived from
  // previous render" state).
  if (horoscopeData && autoExpandedFor !== horoscopeData) {
    setAutoExpandedFor(horoscopeData);
    const currentIndex = mahadashas.findIndex((maha) => isCurrentPeriod(maha.start_utc, maha.end_utc));
    setExpandedIndex(currentIndex !== -1 ? currentIndex : null);
  }

  if (!horoscopeData || !horoscopeData.dasha || !balance) return null;

  return (
    <div className="w-full mt-10">
      <div className="mb-8 px-2 flex items-end justify-between border-b border-white/10 pb-4">
        <div>
          <h2 className="font-cinematic text-3xl font-bold text-white flex items-center gap-3">
            <Clock className="text-gold-primary" size={28} />
            Vimshottari Dasha
          </h2>
          <p className="text-sm text-gray-400 mt-1">120-Year Planetary Timeline</p>
        </div>
        <div className="text-right text-xs text-gray-500">
          <p>Balance at birth: {balance.lord}</p>
          <p>{balance.balance_years.toFixed(2)} years</p>
        </div>
      </div>

      <div className="relative border-l-2 border-white/10 ml-4 md:ml-6 space-y-6 pb-10">
        {mahadashas.map((maha, index) => {
          const isActiveMaha = isCurrentPeriod(maha.start_utc, maha.end_utc);
          const isOpen = expandedIndex === index;
          const antardashas = antardashasOf(maha);

          return (
            <div key={index} className="relative pl-6 md:pl-8">
              {/* Timeline Node (Dot) */}
              <div className={`absolute -left-[9px] top-4 w-4 h-4 rounded-full border-2 transition-colors duration-500 ${
                isActiveMaha 
                  ? 'bg-gold-primary border-white shadow-[0_0_15px_rgba(212,168,75,0.8)]' 
                  : 'bg-space-900 border-gold-primary/50'
              }`}>
                {isActiveMaha && (
                  <span className="absolute inset-0 rounded-full animate-ping bg-gold-primary/50"></span>
                )}
              </div>

              {/* Mahadasha Card */}
              <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: index * 0.05 }}
                className={`glass-card rounded-xl overflow-hidden transition-all duration-300 ${
                  isActiveMaha ? 'border-gold-primary/50 bg-gold-primary/5' : 'border-white/10'
                }`}
              >
                <button
                  onClick={() => setExpandedIndex(isOpen ? null : index)}
                  className="w-full text-left p-5 flex items-center justify-between hover:bg-white/5 transition-colors"
                >
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className={`font-cinematic text-2xl font-bold ${isActiveMaha ? 'text-gold-light' : 'text-white'}`}>
                        {maha.graha} <span className="text-sm font-sans font-normal text-gray-400">Mahadasha</span>
                      </h3>
                      {isActiveMaha && (
                        <span className="text-[10px] uppercase tracking-widest px-2 py-0.5 rounded bg-gold-primary/20 text-gold-primary border border-gold-primary/30">
                          Active Now
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-400 tracking-widest uppercase font-medium">
                      {toDate(maha.start_utc)} <span className="text-gold-primary/50 mx-2">→</span> {toDate(maha.end_utc)}
                    </p>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-gray-500 hidden sm:block">
                      {effectiveYears(maha).toFixed(1)} Years
                    </span>
                    <motion.div animate={{ rotate: isOpen ? 180 : 0 }} transition={{ duration: 0.3 }}>
                      <ChevronDown className={isActiveMaha ? 'text-gold-light' : 'text-gray-500'} />
                    </motion.div>
                  </div>
                </button>

                {/* Antardashas (Sub-periods) */}
                <AnimatePresence>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.4, ease:[0.16, 1, 0.3, 1] }}
                    >
                      <div className="bg-black/40 border-t border-white/5 p-5">
                        <div className="text-xs text-gold-primary uppercase tracking-widest mb-4 flex items-center gap-2">
                          <div className="w-1 h-1 rounded-full bg-gold-primary"></div>
                          Antardashas (Sub-Periods)
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                          {antardashas.map((antar, aIndex) => {
                            const isActiveAntar = isCurrentPeriod(antar.start_utc, antar.end_utc);
                            
                            return (
                              <div 
                                key={aIndex} 
                                className={`p-3 rounded-lg border flex justify-between items-center transition-colors ${
                                  isActiveAntar 
                                    ? 'border-gold-primary/40 bg-gold-primary/10' 
                                    : 'border-white/5 bg-white/5 hover:bg-white/10'
                                }`}
                              >
                                <div>
                                  <p className={`font-medium ${isActiveAntar ? 'text-gold-light' : 'text-gray-200'}`}>
                                    {antar.graha}
                                  </p>
                                  <p className="text-[10px] text-gray-500 mt-1">
                                    {toDate(antar.start_utc)}
                                  </p>
                                </div>
                                {isActiveAntar && (
                                  <div className="w-2 h-2 rounded-full bg-gold-primary animate-pulse"></div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
