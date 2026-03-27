import { useAppStore } from '../../store/appStore';
import { GlassCard } from '../ui/GlassCard';
import { ScoreRing } from '../ui/ScoreRing';
import { Sparkles, Moon } from 'lucide-react';

export const MatchingHero = () => {
  const { matchingData, matchingInput } = useAppStore();
  if (!matchingData) return null;

  const { bride, groom, total_points, max_points, compatibility_level, conclusion, south_indian_poruthams } = matchingData;

  // Determine which score to show in the ring based on the selected system
  const isSouthOnly = matchingInput?.system === 'south_indian';
  
  const displayScore = isSouthOnly && south_indian_poruthams 
    ? south_indian_poruthams.total_matches 
    : total_points || 0;
    
  const displayMax = isSouthOnly && south_indian_poruthams 
    ? south_indian_poruthams.out_of 
    : max_points || 36;
    
  const ringLabel = isSouthOnly ? 'Dashakoota Score' : 'Ashta Koota Score';

  // Format a clean label if South Only
  const matchLevelLabel = isSouthOnly 
    ? (displayScore >= 6 ? 'Compatible' : 'Not Compatible') 
    : compatibility_level;

  const PartnerProfile = ({ label, data, glowColor }: { label: string, data: any, glowColor: string }) => (
    <div className="flex-1 text-center md:text-left relative z-10">
      <h3 className={`font-cinematic text-3xl font-bold ${glowColor} mb-1`}>{label}</h3>
      <p className="text-white font-medium text-lg mb-4">{data.rashi.name} <span className="text-gray-400 text-sm font-normal">({data.rashi.english}) Moon</span></p>
      
      <div className="space-y-3">
        <div className="flex items-center justify-center md:justify-start gap-2 text-sm text-gray-300">
          <Moon size={14} className="text-gold-primary" />
          <span>Ruled by <strong className="text-white">{data.rashi.lord}</strong></span>
        </div>
        <div className="flex items-center justify-center md:justify-start gap-2 text-sm text-gray-300">
          <Sparkles size={14} className="text-gold-primary" />
          <span>Star: <strong className="text-white">{data.nakshatra.name}</strong> (Pada {data.nakshatra.pada})</span>
        </div>
      </div>
    </div>
  );

  return (
    <GlassCard className="w-full p-8 md:p-12 relative overflow-hidden group">
      <div className="absolute top-0 left-0 w-64 h-64 bg-pink-500/10 rounded-full blur-[80px] -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
      <div className="absolute bottom-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-[80px] translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

      <div className="flex flex-col md:flex-row items-center justify-between gap-12 md:gap-8">
        
        <PartnerProfile label="Bride" data={bride} glowColor="text-pink-400 drop-shadow-[0_0_8px_rgba(236,72,153,0.3)]" />

        <div className="flex flex-col items-center justify-center flex-shrink-0 relative z-10">
          <p className="text-gold-primary tracking-[0.2em] text-xs uppercase mb-4 font-medium">{ringLabel}</p>
          
          <ScoreRing score={displayScore} maxScore={displayMax} size={220} strokeWidth={6} />
          
          <div className="mt-6 text-center max-w-[280px]">
            <h2 className="font-cinematic text-3xl font-bold text-white mb-2">{matchLevelLabel} Match</h2>
            <p className="text-xs text-gray-400 leading-relaxed">{conclusion}</p>
          </div>
        </div>

        <div className="flex-1 text-center md:text-right relative z-10">
          <h3 className="font-cinematic text-3xl font-bold text-blue-400 drop-shadow-[0_0_8px_rgba(96,165,250,0.3)] mb-1">Groom</h3>
          <p className="text-white font-medium text-lg mb-4">{groom.rashi.name} <span className="text-gray-400 text-sm font-normal">({groom.rashi.english}) Moon</span></p>
          
          <div className="space-y-3">
            <div className="flex items-center justify-center md:justify-end gap-2 text-sm text-gray-300">
              <span>Ruled by <strong className="text-white">{groom.rashi.lord}</strong></span>
              <Moon size={14} className="text-gold-primary" />
            </div>
            <div className="flex items-center justify-center md:justify-end gap-2 text-sm text-gray-300">
              <span>Star: <strong className="text-white">{groom.nakshatra.name}</strong> (Pada {groom.nakshatra.pada})</span>
              <Sparkles size={14} className="text-gold-primary" />
            </div>
          </div>
        </div>

      </div>
    </GlassCard>
  );
};