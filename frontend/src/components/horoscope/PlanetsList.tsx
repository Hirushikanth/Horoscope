import { useAppStore } from '../../store/appStore';
import { GlassAccordion } from '../ui/GlassAccordion';

export const PlanetsList = () => {
  const { horoscopeData } = useAppStore();
  if (!horoscopeData) return null;

  const { planets } = horoscopeData;

  // Filter out the _meta key
  const planetNames = Object.keys(planets).filter(name => !name.startsWith('_'));

  return (
    <div className="w-full">
      <div className="mb-6 flex items-end justify-between px-2">
        <div>
          <h2 className="font-cinematic text-3xl font-bold text-white">Navagrahas</h2>
          <p className="text-sm text-gray-400 mt-1">Planetary positions & dignity</p>
        </div>
      </div>

      <div className="flex flex-col">
        {planetNames.map((name, index) => {
          const p = planets[name];
          const dignityColor = 
            p.dignity?.status === 'Exalted' || p.dignity?.status === 'Moolatrikona' ? 'text-green-400 border-green-400/30 bg-green-400/10' :
            p.dignity?.status === 'Debilitated' ? 'text-red-400 border-red-400/30 bg-red-400/10' :
            p.dignity?.status === 'Own Sign' ? 'text-gold-primary border-gold-primary/30 bg-gold-primary/10' :
            'text-gray-300 border-gray-500/30 bg-white/5';

          return (
            <GlassAccordion
              key={name}
              delay={0.1 * index}
              title={name}
              subtitle={`${p.rashi.name} (${p.rashi.english}) • ${p.dms.formatted}`}
              badges={
                <>
                  {p.is_retrograde && (
                    <span className="text-[10px] uppercase tracking-widest px-2 py-1 rounded border border-orange-500/30 bg-orange-500/10 text-orange-400 hidden sm:inline-block">
                      Retrograde
                    </span>
                  )}
                  {p.dignity && p.dignity.status !== 'Neutral' && (
                    <span className={`text-[10px] uppercase tracking-widest px-2 py-1 rounded border ${dignityColor}`}>
                      {p.dignity.status}
                    </span>
                  )}
                </>
              }
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-gold-primary text-xs uppercase tracking-widest mb-1">Nakshatra Placement</p>
                  <p className="text-white text-base font-cinematic">{p.nakshatra.name}</p>
                  <p className="text-gray-400 text-xs">Pada {p.nakshatra.pada} • Ruled by {p.nakshatra.ruler}</p>
                </div>
                <div>
                  <p className="text-gold-primary text-xs uppercase tracking-widest mb-1">Dignity details</p>
                  <p className="text-gray-300 text-sm">{p.dignity?.description || 'Standard placement.'}</p>
                </div>
                {p.is_combust && (
                   <div className="col-span-1 md:col-span-2 mt-2 p-3 rounded bg-red-500/10 border border-red-500/20 text-red-300 text-sm">
                     ⚠️ This planet is Combust (too close to the Sun), weakening its external effects.
                   </div>
                )}
              </div>
            </GlassAccordion>
          );
        })}
      </div>
    </div>
  );
};