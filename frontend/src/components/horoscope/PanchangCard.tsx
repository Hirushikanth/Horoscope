import { useAppStore } from '../../store/appStore';
import { GlassCard } from '../ui/GlassCard';
import { Calendar, Clock, Compass, SunDim } from 'lucide-react';

export const PanchangCard = () => {
  const { horoscopeData } = useAppStore();
  if (!horoscopeData) return null;

  const { panchang } = horoscopeData;

  const items =[
    { icon: <Calendar size={18} />, label: "Tithi", value: panchang.tithi.name, sub: panchang.tithi.paksha },
    { icon: <Clock size={18} />, label: "Vara", value: panchang.vara.name, sub: panchang.vara.sanskrit },
    { icon: <SunDim size={18} />, label: "Yoga", value: panchang.yoga.name, sub: `No. ${panchang.yoga.number}` },
    { icon: <Compass size={18} />, label: "Karana", value: panchang.karana.name, sub: "Half-Tithi" },
  ];

  return (
    <GlassCard className="col-span-1 md:col-span-1 lg:col-span-2 p-6 flex flex-col justify-between">
      <div className="mb-4">
        <h3 className="text-gold-primary tracking-[0.2em] text-xs uppercase font-medium">Daily Elements</h3>
        <h2 className="font-cinematic text-2xl font-semibold text-white mt-1">Panchang details</h2>
      </div>

      <div className="grid grid-cols-2 gap-4">
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