import { useAppStore } from '../../store/appStore';
import { GlassCard } from '../ui/GlassCard';

export const AshtaKootaGrid = () => {
  const { matchingData } = useAppStore();
  if (!matchingData || !matchingData.kootas) return null;

  const { kootas } = matchingData;

  const kootaList = [
    { id: 'varna', name: 'Varna', label: 'Spiritual', data: kootas.varna },
    { id: 'vashya', name: 'Vashya', label: 'Attraction', data: kootas.vashya },
    { id: 'tara', name: 'Tara', label: 'Star Harmony', data: kootas.tara },
    { id: 'yoni', name: 'Yoni', label: 'Physical', data: kootas.yoni },
    { id: 'graha_maitri', name: 'Graha Maitri', label: 'Mental', data: kootas.graha_maitri },
    { id: 'gana', name: 'Gana', label: 'Temperament', data: kootas.gana },
    { id: 'bhakoot', name: 'Bhakoot', label: 'Emotional', data: kootas.bhakoot },
    { id: 'nadi', name: 'Nadi', label: 'Health/Genetic', data: kootas.nadi },
  ];

  return (
    <div className="w-full">
      <div className="mb-6 flex items-end justify-between px-2">
        <div>
          <h2 className="font-cinematic text-3xl font-bold text-white">Ashta Koota Milan</h2>
          <p className="text-sm text-gray-400 mt-1">Breakdown of the 8 compatibility pillars</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kootaList.map((item, index) => {
          const { obtained, max, description } = item.data;
          const percentage = (obtained / max) * 100;
          const isZero = obtained === 0;
          const isMax = obtained === max;

          return (
            <GlassCard key={item.id} delay={index * 0.05} className="p-5 flex flex-col justify-between h-40 group">
              <div>
                <div className="flex justify-between items-start mb-1">
                  <div>
                    <h3 className="text-gold-light font-cinematic text-xl font-bold">{item.name}</h3>
                    <p className="text-[10px] text-gray-400 uppercase tracking-widest">{item.label}</p>
                  </div>
                  <div className="text-right">
                    <span className={`text-xl font-bold ${isZero ? 'text-red-400' : isMax ? 'text-green-400' : 'text-white'}`}>
                      {obtained}
                    </span>
                    <span className="text-xs text-gray-500"> / {max}</span>
                  </div>
                </div>
                
                {/* Mini Progress Bar */}
                <div className="w-full h-1 bg-white/10 rounded-full mt-3 overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${isZero ? 'bg-red-400' : isMax ? 'bg-green-400' : 'bg-gold-primary'}`}
                    style={{ width: `${percentage}%` }}
                  ></div>
                </div>
              </div>

              <p className="text-xs text-gray-400 leading-snug line-clamp-2 mt-4 group-hover:line-clamp-none transition-all">
                {description}
              </p>
            </GlassCard>
          );
        })}
      </div>
    </div>
  );
};