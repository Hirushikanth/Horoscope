import { useAppStore } from '../../store/appStore';
import { GlassCard } from '../ui/GlassCard';
import { ScoreRing } from '../ui/ScoreRing';
import { Sparkles, Moon } from 'lucide-react';
import type { PartnerBrief } from '../../types';

const PartnerProfile = ({ label, data, glowColor }: { label: string, data: PartnerBrief, glowColor: string }) => (
  <div className="flex-1 text-center md:text-left relative z-10">
    <h3 className={`font-cinematic text-3xl font-bold ${glowColor} mb-1`}>{label}</h3>
    <p className="text-white font-medium text-lg mb-4">{data.rasi.tamil ?? data.rasi.english} <span className="text-gray-400 text-sm font-normal">Rasi</span></p>

    <div className="space-y-3">
      <div className="flex items-center justify-center md:justify-start gap-2 text-sm text-gray-300">
        <Moon size={14} className="text-gold-primary" />
        <span>Nakshatram: <strong className="text-white">{data.nakshatra.tamil ?? data.nakshatra.english}</strong> (Pada {data.pada})</span>
      </div>
      <div className="flex items-center justify-center md:justify-start gap-2 text-sm text-gray-300">
        <Sparkles size={14} className="text-gold-primary" />
        <span>Chevvai Dosham: <strong className={data.chevvai_dosham ? 'text-red-400' : 'text-green-400'}>{data.chevvai_dosham ? 'Present' : 'Absent'}</strong></span>
      </div>
    </div>
  </div>
);

export const MatchingHero = () => {
  const { matchingData } = useAppStore();
  if (!matchingData) return null;

  const { bride, groom, score, verdict } = matchingData;

  const matchLevelLabel =
    verdict.verdict === 'uthamam' ? 'Uthamam' :
    verdict.verdict === 'madhyamam' ? 'Madhyamam' :
    'Athamam';

  return (
    <GlassCard className="w-full p-8 md:p-12 relative overflow-hidden group">
      <div className="absolute top-0 left-0 w-64 h-64 bg-pink-500/10 rounded-full blur-[80px] -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
      <div className="absolute bottom-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-[80px] translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

      <div className="flex flex-col md:flex-row items-center justify-between gap-12 md:gap-8">

        <PartnerProfile label="Bride" data={bride} glowColor="text-pink-400 drop-shadow-[0_0_8px_rgba(236,72,153,0.3)]" />

        <div className="flex flex-col items-center justify-center flex-shrink-0 relative z-10">
          <p className="text-gold-primary tracking-[0.2em] text-xs uppercase mb-4 font-medium">Kalyana Porutham Score</p>

          <ScoreRing score={score.total} maxScore={score.out_of} size={220} strokeWidth={6} />

          <div className="mt-6 text-center max-w-[280px]">
            <h2 className="font-cinematic text-3xl font-bold text-white mb-2">{matchLevelLabel} Match</h2>
            <p className="text-xs text-gray-400 leading-relaxed">Band {verdict.band} • {verdict.reasons[0] ?? verdict.verdict}</p>
          </div>
        </div>

        <div className="flex-1 text-center md:text-right relative z-10">
          <h3 className="font-cinematic text-3xl font-bold text-blue-400 drop-shadow-[0_0_8px_rgba(96,165,250,0.3)] mb-1">Groom</h3>
          <p className="text-white font-medium text-lg mb-4">{groom.rasi.tamil ?? groom.rasi.english} <span className="text-gray-400 text-sm font-normal">Rasi</span></p>

          <div className="space-y-3">
            <div className="flex items-center justify-center md:justify-end gap-2 text-sm text-gray-300">
              <span>Nakshatram: <strong className="text-white">{groom.nakshatra.tamil ?? groom.nakshatra.english}</strong> (Pada {groom.pada})</span>
              <Moon size={14} className="text-gold-primary" />
            </div>
            <div className="flex items-center justify-center md:justify-end gap-2 text-sm text-gray-300">
              <span>Chevvai Dosham: <strong className={groom.chevvai_dosham ? 'text-red-400' : 'text-green-400'}>{groom.chevvai_dosham ? 'Present' : 'Absent'}</strong></span>
              <Sparkles size={14} className="text-gold-primary" />
            </div>
          </div>
        </div>

      </div>
    </GlassCard>
  );
};
