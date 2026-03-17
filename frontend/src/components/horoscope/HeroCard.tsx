import { Moon, Sparkles, Sun } from 'lucide-react';
import { useAppStore } from '../../store/appStore';
import { GlassCard } from '../ui/GlassCard';

export const HeroCard = () => {
  const { horoscopeData } = useAppStore();
  if (!horoscopeData) return null;

  const { ascendant, janma_nakshatra } = horoscopeData;

  return (
    <GlassCard className="col-span-1 md:col-span-2 lg:col-span-2 row-span-2 p-8 flex flex-col justify-between relative overflow-hidden group">
      {/* Decorative Background Element */}
      <div className="absolute -top-24 -right-24 w-64 h-64 bg-gold-primary/10 rounded-full blur-3xl group-hover:bg-gold-primary/20 transition-all duration-700"></div>
      
      <div className="relative z-10">
        <h3 className="text-gold-primary tracking-[0.2em] text-xs uppercase mb-2 font-medium">Cosmic Trinity</h3>
        <h2 className="font-cinematic text-4xl md:text-5xl font-bold text-white leading-tight drop-shadow-lg">
          {ascendant.rashi.english} <span className="text-gold-light opacity-50 font-sans font-light text-3xl">Ascendant</span>
        </h2>
        <p className="text-gray-400 mt-3 max-w-sm text-sm leading-relaxed">
          Ruled by <span className="text-white font-medium">{ascendant.rashi.lord}</span>. The Ascendant defines your physical incarnation and the lens through which you view the universe.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-8 relative z-10">
        <div className="bg-space-800/50 backdrop-blur-md border border-white/5 p-4 rounded-xl">
          <div className="flex items-center gap-2 mb-2 text-gold-primary">
            <Moon size={16} />
            <span className="text-xs uppercase tracking-wider font-semibold">Moon Sign</span>
          </div>
          <p className="font-cinematic text-2xl text-white">{janma_nakshatra.moon_rashi.english}</p>
          <p className="text-xs text-gray-500 mt-1">Ruled by {janma_nakshatra.moon_rashi.lord}</p>
        </div>

        <div className="bg-space-800/50 backdrop-blur-md border border-white/5 p-4 rounded-xl">
          <div className="flex items-center gap-2 mb-2 text-gold-primary">
            <Sparkles size={16} />
            <span className="text-xs uppercase tracking-wider font-semibold">Birth Star</span>
          </div>
          <p className="font-cinematic text-2xl text-white">{janma_nakshatra.name}</p>
          <p className="text-xs text-gray-500 mt-1">Pada {janma_nakshatra.pada} • {janma_nakshatra.deity}</p>
        </div>
      </div>
    </GlassCard>
  );
};