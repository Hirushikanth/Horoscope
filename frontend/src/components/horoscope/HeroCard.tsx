import { Moon, Sparkles, BadgeCheck } from 'lucide-react';
import { useAppStore } from '../../store/appStore';
import { GlassCard } from '../ui/GlassCard';

export const HeroCard = () => {
  const { horoscopeData } = useAppStore();
  if (!horoscopeData) return null;

  const { lagna, grahas, panchangam, bhavas, meta } = horoscopeData;

  const moon = grahas.find((g) => g.name === 'Moon');
  const lagnaHouse = bhavas.find((b) => b.house_number === 1);
  const moonHouse = moon ? bhavas.find((b) => b.house_number === moon.house_number) : undefined;

  return (
    <GlassCard className="col-span-1 md:col-span-2 lg:col-span-2 row-span-2 p-8 flex flex-col justify-between relative overflow-hidden group">
      {/* Decorative Background Element */}
      <div className="absolute -top-24 -right-24 w-64 h-64 bg-gold-primary/10 rounded-full blur-3xl group-hover:bg-gold-primary/20 transition-all duration-700"></div>

      <div className="relative z-10">
        <div className="flex flex-wrap items-center gap-2 mb-2">
          <h3 className="text-gold-primary tracking-[0.2em] text-xs uppercase font-medium">
            திருக்கணித ஜாதகம்
          </h3>
          <span className="inline-flex items-center gap-1 text-[9px] uppercase tracking-widest px-2 py-0.5 rounded-full border border-gold-primary/30 bg-gold-primary/10 text-gold-light">
            <BadgeCheck size={10} />
            Thirukkanitha
          </span>
          <span className="text-[9px] uppercase tracking-widest px-2 py-0.5 rounded-full border border-white/10 bg-white/5 text-gray-400">
            {meta.ayanamsa.system} • {meta.ayanamsa.value_deg.toFixed(2)}°
          </span>
        </div>
        <h2 className="font-cinematic text-4xl md:text-5xl font-bold text-white leading-tight drop-shadow-lg">
          {lagna.rasi.tamil ?? lagna.rasi.english}{' '}
          <span className="text-gold-light opacity-50 font-sans font-light text-3xl">Lagnam</span>
        </h2>
        <p className="text-gray-400 mt-3 max-w-sm text-sm leading-relaxed">
          Ruled by <span className="text-white font-medium">{lagnaHouse?.lord ?? '—'}</span>. The Lagnam defines
          your physical incarnation and the lens through which you view the universe.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-8 relative z-10">
        <div className="bg-space-800/50 backdrop-blur-md border border-white/5 p-4 rounded-xl">
          <div className="flex items-center gap-2 mb-2 text-gold-primary">
            <Moon size={16} />
            <span className="text-xs uppercase tracking-wider font-semibold">Rasi (Moon Sign)</span>
          </div>
          <p className="font-cinematic text-2xl text-white">{moon?.rasi.tamil ?? moon?.rasi.english ?? '—'}</p>
          <p className="text-xs text-gray-500 mt-1">Ruled by {moonHouse?.lord ?? '—'}</p>
        </div>

        <div className="bg-space-800/50 backdrop-blur-md border border-white/5 p-4 rounded-xl">
          <div className="flex items-center gap-2 mb-2 text-gold-primary">
            <Sparkles size={16} />
            <span className="text-xs uppercase tracking-wider font-semibold">Nakshatram</span>
          </div>
          <p className="font-cinematic text-2xl text-white">
            {panchangam.nakshatra.name.tamil ?? panchangam.nakshatra.name.english}
          </p>
          <p className="text-xs text-gray-500 mt-1">Pada {panchangam.nakshatra.pada} • {panchangam.nakshatra.lord}</p>
        </div>
      </div>
    </GlassCard>
  );
};
