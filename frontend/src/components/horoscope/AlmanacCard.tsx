import { useAppStore } from '../../store/appStore';
import { GlassCard } from '../ui/GlassCard';
import { Sunrise, Sunset, CloudMoon, Skull, Hourglass } from 'lucide-react';
import type { AlmanacWindow } from '../../types';

// Local ISO strings carry the birth-zone offset (e.g. "10:30:00+05:30");
// extract the clock part directly to stay tz-safe without converting.
const clockOf = (iso: string | null) => (iso ? iso.slice(11, 16) : '—');
const range = (win: AlmanacWindow | null) =>
  win ? `${clockOf(win.start_local)} – ${clockOf(win.end_local)}` : 'Unavailable';

export const AlmanacCard = () => {
  const { panchangamData } = useAppStore();
  if (!panchangamData) return null;

  const { almanac } = panchangamData;

  return (
    <GlassCard className="w-full p-6" hoverEffect={false}>
      <div className="mb-5">
        <h3 className="text-gold-primary tracking-[0.2em] text-xs uppercase font-medium">
          Daily Almanac
        </h3>
        <h2 className="font-cinematic text-2xl font-semibold text-white mt-1">
          Rahu Kalam &amp; Mithra Neri
        </h2>
        <p className="text-[10px] text-gray-500 mt-1 uppercase tracking-widest">
          Udaya day (sunrise-anchored) • local time
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <div className="p-3 rounded-lg bg-white/5 border border-white/10">
          <div className="flex items-center gap-2 mb-1.5 text-gold-primary">
            <Sunrise size={16} />
            <span className="text-[10px] uppercase tracking-widest font-semibold">Sunrise</span>
          </div>
          <p className="text-white font-medium">{clockOf(almanac.sunrise_local)}</p>
        </div>

        <div className="p-3 rounded-lg bg-white/5 border border-white/10">
          <div className="flex items-center gap-2 mb-1.5 text-gold-primary">
            <Sunset size={16} />
            <span className="text-[10px] uppercase tracking-widest font-semibold">Sunset</span>
          </div>
          <p className="text-white font-medium">{clockOf(almanac.sunset_local)}</p>
        </div>

        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/25">
          <div className="flex items-center gap-2 mb-1.5 text-red-400">
            <Skull size={16} />
            <span className="text-[10px] uppercase tracking-widest font-semibold">Rahu Kalam</span>
          </div>
          <p className="text-white font-medium">{range(almanac.rahu_kalam)}</p>
        </div>

        <div className="p-3 rounded-lg bg-white/5 border border-white/10">
          <div className="flex items-center gap-2 mb-1.5 text-gold-primary">
            <CloudMoon size={16} />
            <span className="text-[10px] uppercase tracking-widest font-semibold">Yamagandam</span>
          </div>
          <p className="text-white font-medium">{range(almanac.yamagandam)}</p>
        </div>

        <div className="p-3 rounded-lg bg-white/5 border border-white/10">
          <div className="flex items-center gap-2 mb-1.5 text-gold-primary">
            <Hourglass size={16} />
            <span className="text-[10px] uppercase tracking-widest font-semibold">Gulika Kalam</span>
          </div>
          <p className="text-white font-medium">{range(almanac.gulika)}</p>
        </div>
      </div>

      {almanac.abhijit && (
        <p className="text-[10px] text-gray-500 mt-4 uppercase tracking-widest">
          Abhijit Muhurta: <span className="text-gold-light">{range(almanac.abhijit)}</span>
        </p>
      )}
    </GlassCard>
  );
};
