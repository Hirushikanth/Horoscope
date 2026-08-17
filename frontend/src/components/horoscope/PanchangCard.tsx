import { useAppStore } from '../../store/appStore';
import { GlassCard } from '../ui/GlassCard';
import { Calendar, Clock, Compass, SunDim, Sparkles } from 'lucide-react';

const PAKSHA_TAMIL: Record<string, string> = {
  shukla: 'Valarpirai',
  krishna: 'Theipirai',
};

export const PanchangCard = () => {
  const { horoscopeData } = useAppStore();
  if (!horoscopeData) return null;

  const { panchangam } = horoscopeData;

  const items = [
    {
      icon: <Calendar size={18} />,
      label: 'Tithi (Thithi)',
      value: panchangam.tithi.name.tamil ?? panchangam.tithi.name.english,
      sub: `${PAKSHA_TAMIL[panchangam.tithi.paksha] ?? panchangam.tithi.paksha} • ${panchangam.tithi.number}/30`,
    },
    {
      icon: <Clock size={18} />,
      label: 'Vara (Vaaram)',
      value: panchangam.vara.name.tamil ?? panchangam.vara.name.english,
      sub: panchangam.vara.name.sanskrit,
    },
    {
      icon: <Sparkles size={18} />,
      label: 'Nakshatram',
      value: panchangam.nakshatra.name.tamil ?? panchangam.nakshatra.name.english,
      sub: `Pada ${panchangam.nakshatra.pada} • ${panchangam.nakshatra.lord}`,
    },
    {
      icon: <SunDim size={18} />,
      label: 'Yogam',
      value: panchangam.yoga.name.tamil ?? panchangam.yoga.name.english,
      sub: `No. ${panchangam.yoga.index + 1}`,
    },
    {
      icon: <Compass size={18} />,
      label: 'Karanam',
      value: panchangam.karana.name.tamil ?? panchangam.karana.name.english,
      sub: 'Half-Tithi',
    },
  ];

  return (
    <GlassCard className="col-span-1 md:col-span-2 lg:col-span-2 row-span-2 p-6 flex flex-col justify-between">
      <div className="mb-4">
        <h3 className="text-gold-primary tracking-[0.2em] text-xs uppercase font-medium">Birth Panchangam</h3>
        <h2 className="font-cinematic text-2xl font-semibold text-white mt-1">Panchangam details</h2>
        <p className="text-[10px] text-gray-500 mt-1 uppercase tracking-widest">
          Pancha-Anga • Tamil names preferred
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {items.map((item, i) => (
          <div key={i} className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-gold-primary/10 text-gold-primary border border-gold-primary/20">
              {item.icon}
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-widest mb-0.5">{item.label}</p>
              <p className="text-white font-medium leading-none">{item.value}</p>
              <p className="text-[10px] text-gold-light/60 mt-1">{item.sub}</p>
            </div>
          </div>
        ))}
      </div>
    </GlassCard>
  );
};
