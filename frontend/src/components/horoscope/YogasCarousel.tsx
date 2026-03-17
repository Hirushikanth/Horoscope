import { useAppStore } from '../../store/appStore';
import { GlassCard } from '../ui/GlassCard';
import { motion } from 'motion/react';

export const YogasCarousel = () => {
  const { horoscopeData } = useAppStore();
  if (!horoscopeData || !horoscopeData.yogas || horoscopeData.yogas.length === 0) return null;

  return (
    <div className="col-span-1 md:col-span-3 lg:col-span-4 mt-4">
      <div className="flex items-center justify-between mb-4 px-2">
        <div>
          <h2 className="font-cinematic text-2xl font-bold text-white">Active Yogas</h2>
          <p className="text-sm text-gray-400">Special planetary combinations present at birth</p>
        </div>
        <div className="text-gold-primary text-sm tracking-widest uppercase font-medium">
          {horoscopeData.yogas.length} Detected
        </div>
      </div>

      {/* Hide Scrollbar CSS trick applied inline */}
      <div className="flex overflow-x-auto gap-4 pb-6 snap-x snap-mandatory [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden px-2">
        {horoscopeData.yogas.map((yoga: any, index: number) => (
          <GlassCard 
            key={index} 
            delay={0.1 * index}
            className="min-w-[280px] md:min-w-[320px] p-6 snap-start flex-shrink-0 group hover:-translate-y-2 transition-transform duration-500"
          >
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-cinematic text-xl text-white font-semibold">{yoga.name}</h3>
              <span className={`text-[10px] px-2 py-1 rounded border uppercase tracking-widest ${
                yoga.type === 'Benefic' 
                  ? 'bg-gold-primary/10 text-gold-primary border-gold-primary/30' 
                  : 'bg-red-500/10 text-red-400 border-red-500/30'
              }`}>
                {yoga.type}
              </span>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed mb-4 line-clamp-3 group-hover:line-clamp-none transition-all">
              {yoga.description}
            </p>
            <div className="flex flex-wrap gap-2 mt-auto">
              {yoga.planets.map((planet: string, i: number) => (
                <span key={i} className="text-xs bg-white/5 text-gray-300 px-2 py-1 rounded-md border border-white/10">
                  {planet}
                </span>
              ))}
            </div>
          </GlassCard>
        ))}
      </div>
    </div>
  );
};