import { useAppStore } from '../../store/appStore';
import { GlassAccordion } from '../ui/GlassAccordion';
import type { DignityType, GrahaInfo } from '../../types';

const DIGNITY_LABELS: Record<DignityType, { tamil: string; english: string }> = {
  exalted: { tamil: 'Uccham', english: 'Exalted' },
  debilitated: { tamil: 'Neecham', english: 'Debilitated' },
  moolatrikona: { tamil: 'Moolatrikonam', english: 'Moolatrikona' },
  own_sign: { tamil: 'Aatchi', english: 'Own Sign' },
  neutral: { tamil: 'Samaanam', english: 'Neutral' },
};

const formatDegree = (deg: number) => {
  const d = Math.floor(deg);
  const m = Math.floor((deg - d) * 60);
  return `${d}°${m.toString().padStart(2, '0')}'`;
};

const display = (tamil: string | null, english: string) => tamil ?? english;

export const PlanetsList = () => {
  const { horoscopeData } = useAppStore();
  if (!horoscopeData) return null;

  const { grahas, bhavas } = horoscopeData;

  const dignityColor = (dignity: DignityType) =>
    dignity === 'exalted' || dignity === 'moolatrikona' ? 'text-green-400 border-green-400/30 bg-green-400/10' :
    dignity === 'debilitated' ? 'text-red-400 border-red-400/30 bg-red-400/10' :
    dignity === 'own_sign' ? 'text-gold-primary border-gold-primary/30 bg-gold-primary/10' :
    'text-gray-300 border-gray-500/30 bg-white/5';

  return (
    <div className="w-full">
      <div className="mb-6 flex items-end justify-between px-2">
        <div>
          <h2 className="font-cinematic text-3xl font-bold text-white">Navagrahas</h2>
          <p className="text-sm text-gray-400 mt-1">Graha Nila — planetary positions &amp; dignity</p>
        </div>
      </div>

      <div className="flex flex-col">
        {grahas.map((graha: GrahaInfo, index: number) => {
          const dignity = graha.dignity.dignity;
          const bhava = bhavas.find((b) => b.house_number === graha.house_number);
          const dignityMeta = DIGNITY_LABELS[dignity];

          return (
            <GlassAccordion
              key={graha.name}
              delay={0.1 * index}
              title={display(graha.names.tamil, graha.names.english)}
              subtitle={`${display(graha.rasi.tamil, graha.rasi.english)} • ${formatDegree(graha.degree_in_sign_deg)} • House ${graha.house_number}`}
              badges={
                <>
                  {graha.retrograde && (
                    <span className="text-[10px] uppercase tracking-widest px-2 py-1 rounded border border-orange-500/30 bg-orange-500/10 text-orange-400 hidden sm:inline-block">
                      Vakram (R)
                    </span>
                  )}
                  {graha.combust && (
                    <span className="text-[10px] uppercase tracking-widest px-2 py-1 rounded border border-red-500/30 bg-red-500/10 text-red-400 hidden sm:inline-block">
                      Asthamangam (C)
                    </span>
                  )}
                  {dignity !== 'neutral' && (
                    <span className={`text-[10px] uppercase tracking-widest px-2 py-1 rounded border ${dignityColor(dignity)}`}>
                      {dignityMeta.tamil}
                    </span>
                  )}
                </>
              }
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-gold-primary text-xs uppercase tracking-widest mb-1">Nakshatram Placement</p>
                  <p className="text-white text-base font-cinematic">{display(graha.nakshatra.tamil, graha.nakshatra.english)}</p>
                  <p className="text-gray-400 text-xs">Pada {graha.pada}</p>
                </div>
                <div>
                  <p className="text-gold-primary text-xs uppercase tracking-widest mb-1">Dignity details</p>
                  <p className="text-gray-300 text-sm">
                    {dignityMeta.tamil} ({dignityMeta.english}) in {display(graha.rasi.tamil, graha.rasi.english)}
                  </p>
                  <p className="text-gray-400 text-xs mt-1">
                    D9 Navamsa: {display(graha.navamsa_rasi.tamil, graha.navamsa_rasi.english)} •{' '}
                    {graha.vargottama ? 'Vargottama' : 'Non-vargottama'}
                  </p>
                </div>
                {graha.combust && (
                  <div className="col-span-1 md:col-span-2 mt-2 p-3 rounded bg-red-500/10 border border-red-500/20 text-red-300 text-sm">
                    This graha is in Asthamangam (combustion — too close to the Sun), weakening its external effects.
                  </div>
                )}
                {graha.retrograde && (
                  <div className="col-span-1 md:col-span-2 mt-2 p-3 rounded bg-orange-500/10 border border-orange-500/20 text-orange-300 text-sm">
                    This graha is in Vakram (retrogression), intensifying its internalised expression.
                  </div>
                )}
                {bhava && (
                  <div className="col-span-1 md:col-span-2 mt-2 p-3 rounded bg-white/5 border border-white/10 text-sm text-gray-300">
                    Occupies the {display(bhava.rasi.tamil, bhava.rasi.english)} sign of House {bhava.house_number}, ruled by {bhava.lord}.
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
