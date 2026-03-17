import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { HeroCard } from './HeroCard';
import { PanchangCard } from './PanchangCard';
import { YogasCarousel } from './YogasCarousel';
import { KundliChart } from '../canvas/KundliChart';
import { PlanetsList } from './PlanetsList';
import { BhavasList } from './BhavasList';
import { DashaTimeline } from './DashaTimeline';
import { GlassCard } from '../ui/GlassCard';
import { useAppStore } from '../../store/appStore';

const TABS = [
  { id: 'overview', label: 'BENTO OVERVIEW' },
  { id: 'visual', label: 'Visual chart & planets' },
  { id: 'bhavas', label: 'Bhavas' },
  { id: 'dasha', label: 'Vimshottari Dasha' },
];

export const Dashboard = () => {
  const { horoscopeData } = useAppStore();
  const [activeTab, setActiveTab] = useState('overview');

  if (!horoscopeData) return null;

  return (
    <div className="w-full max-w-6xl mx-auto space-y-8">
      {/* ---------------- NAVIGATION PILLS ---------------- */}
      <div className="flex flex-wrap justify-center gap-2 p-1 bg-white/5 backdrop-blur-md rounded-full border border-white/10 w-fit mx-auto mb-12">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`relative px-6 py-2 text-xs font-medium tracking-widest uppercase transition-all duration-300 rounded-full ${
              activeTab === tab.id ? 'text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            {activeTab === tab.id && (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 bg-gold-primary/20 border border-gold-primary/30 rounded-full shadow-[0_0_15px_rgba(212,175,55,0.2)]"
                transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
              />
            )}
            <span className="relative z-10">{tab.label}</span>
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
          className="w-full"
        >
          {activeTab === 'overview' && (
            <div className="space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 auto-rows-[200px]">
                <HeroCard />
                <PanchangCard />

                <GlassCard className="col-span-1 p-6 flex flex-col justify-center text-center">
                  <p className="text-gold-primary tracking-widest text-[10px] uppercase mb-2">Born In</p>
                  <h3 className="font-cinematic text-3xl font-bold text-white mb-1">
                    {horoscopeData.janma_nakshatra.dasha_lord_at_birth}
                  </h3>
                  <p className="text-xs text-gray-400">Mahadasha</p>
                  <div className="mt-4 pt-4 border-t border-white/10">
                    <p className="text-white text-sm font-medium">
                      {horoscopeData.janma_nakshatra.dasha_balance_years.toFixed(1)} Years Balance
                    </p>
                  </div>
                </GlassCard>

                <GlassCard className="col-span-1 p-6 flex flex-col justify-center text-center">
                  <p className="text-gold-primary tracking-widest text-[10px] uppercase mb-2">Ayanamsa</p>
                  <h3 className="font-cinematic text-3xl font-bold text-white mb-1">
                    {horoscopeData.planets._meta.ayanamsa.toFixed(4)}°
                  </h3>
                  <p className="text-xs text-gray-400">Lahiri Chitrapaksha</p>
                  <div className="mt-4 pt-4 border-t border-white/10">
                    <p className="text-[10px] text-gray-500 uppercase tracking-widest">
                      NASA JPL DE440
                    </p>
                  </div>
                </GlassCard>
              </div>
              <div className="w-full">
                <YogasCarousel />
              </div>
            </div>
          )}

          {activeTab === 'visual' && (
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 w-full">
              <div className="xl:col-span-5 h-fit lg:sticky top-6">
                <KundliChart />
              </div>
              <div className="xl:col-span-7">
                <PlanetsList />
              </div>
            </div>
          )}

          {activeTab === 'bhavas' && (
            <div className="w-full">
              <BhavasList />
            </div>
          )}

          {activeTab === 'dasha' && (
            <div className="w-full">
              <DashaTimeline />
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};