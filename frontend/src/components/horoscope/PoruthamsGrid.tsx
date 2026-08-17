import { useAppStore } from '../../store/appStore';
import { GlassCard } from '../ui/GlassCard';
import { CheckCircle2, MinusCircle, XCircle } from 'lucide-react';
import type { PoruthamResult } from '../../types';

const RESULT_META: Record<PoruthamResult, { label: string; tamil: string; color: string }> = {
  uthamam: { label: 'Uthamam', tamil: 'உத்தமம்', color: 'text-green-400 border-green-400/30 bg-green-400/10' },
  madhyamam: { label: 'Madhyamam', tamil: 'மத்திமம்', color: 'text-gold-light border-gold-primary/30 bg-gold-primary/10' },
  athamam: { label: 'Athamam', tamil: 'அதமம்', color: 'text-red-400 border-red-400/30 bg-red-400/10' },
};

const ResultIcon = ({ result }: { result: PoruthamResult }) =>
  result === 'uthamam' ? <CheckCircle2 className="text-green-400 flex-shrink-0" size={20} /> :
  result === 'madhyamam' ? <MinusCircle className="text-gold-primary flex-shrink-0" size={20} /> :
  <XCircle className="text-red-400 flex-shrink-0" size={20} />;

export const PoruthamsGrid = () => {
  const { matchingData } = useAppStore();
  if (!matchingData) return null;

  const { poruthams, score, verdict, chevvai_cross_check } = matchingData;

  const nonNegotiables = Object.entries(verdict.non_negotiables);

  return (
    <div className="w-full space-y-8">
      <div>
        <div className="mb-6 flex items-end justify-between px-2">
          <div>
            <h2 className="font-cinematic text-3xl font-bold text-white">Kalyana Porutham</h2>
            <p className="text-sm text-gray-400 mt-1">The 11 checks of the Tamil marriage match</p>
          </div>
          <div className="text-right">
            <p className="font-cinematic text-3xl font-bold text-gold-light">{score.total}<span className="text-lg text-gray-500">/{score.out_of}</span></p>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest">{verdict.verdict} • Band {verdict.band}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {poruthams.map((check, index) => {
            const meta = RESULT_META[check.result];
            return (
              <GlassCard key={check.id} delay={index * 0.05} className="p-5 flex flex-col gap-3 h-full">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <ResultIcon result={check.result} />
                    <div>
                      <h3 className="text-gold-light font-cinematic text-xl font-bold leading-tight">
                        {check.name.tamil ?? check.name.english}
                      </h3>
                      <p className="text-[10px] text-gray-400 uppercase tracking-widest mt-0.5">{check.governs}</p>
                    </div>
                  </div>
                  {check.in_total && (
                    <span className={`text-[10px] px-2 py-0.5 rounded border uppercase tracking-widest whitespace-nowrap ${meta.color}`}>
                      {meta.tamil} {meta.label}
                    </span>
                  )}
                </div>

                {check.notes.length > 0 && (
                  <ul className="text-xs text-gray-400 leading-snug space-y-1">
                    {check.notes.map((note, i) => <li key={i}>• {note}</li>)}
                  </ul>
                )}
              </GlassCard>
            );
          })}
        </div>
      </div>

      {/* Verdict + gates + Chevvai cross-check */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <GlassCard className="p-5 flex flex-col justify-between h-full">
          <div>
            <h3 className="text-gold-primary text-xs uppercase tracking-widest mb-3 font-bold">Verdict</h3>
            <div className="flex flex-wrap gap-2 mb-3">
              {Object.entries(verdict.gates).map(([gate, status]) => (
                <span key={gate} className={`text-[10px] uppercase tracking-widest px-2 py-1 rounded border ${
                  status === 'ok' ? 'border-green-400/30 bg-green-400/10 text-green-400' : 'border-red-400/30 bg-red-400/10 text-red-400'
                }`}>
                  {gate === 'rajju' ? 'Rajju' : gate === 'vedha' ? 'Vedha' : gate}: {status}
                </span>
              ))}
            </div>
            {verdict.gate_overridden && (
              <p className="text-xs text-red-400 mb-2">Gate failure overrode the high score total.</p>
            )}

            {nonNegotiables.length > 0 && (
              <div className="mb-3 pt-3 border-t border-white/10">
                <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-2">Non-negotiables</p>
                <div className="flex flex-wrap gap-2">
                  {nonNegotiables.map(([name, ok]) => (
                    <span key={name} className={`text-[10px] uppercase tracking-widest px-2 py-1 rounded border ${
                      ok ? 'border-green-400/30 bg-green-400/10 text-green-400' : 'border-red-400/30 bg-red-400/10 text-red-400'
                    }`}>
                      {name}: {ok ? 'OK' : 'Failed'}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
          <ul className="text-xs text-gray-400 space-y-1">
            {verdict.reasons.map((reason, i) => <li key={i}>• {reason}</li>)}
          </ul>
        </GlassCard>

        <GlassCard className="p-5 flex flex-col justify-between h-full">
          <div>
            <h3 className="text-gold-primary text-xs uppercase tracking-widest mb-3 font-bold">Chevvai Dosham Cross-check</h3>
            <div className="flex flex-wrap gap-2 mb-3">
              <span className={`text-[10px] uppercase tracking-widest px-2 py-1 rounded border ${
                chevvai_cross_check.bride_dosham ? 'border-red-400/30 bg-red-400/10 text-red-400' : 'border-green-400/30 bg-green-400/10 text-green-400'
              }`}>
                Bride: {chevvai_cross_check.bride_dosham ? 'Dosham' : 'No Dosham'}
              </span>
              <span className={`text-[10px] uppercase tracking-widest px-2 py-1 rounded border ${
                chevvai_cross_check.groom_dosham ? 'border-red-400/30 bg-red-400/10 text-red-400' : 'border-green-400/30 bg-green-400/10 text-green-400'
              }`}>
                Groom: {chevvai_cross_check.groom_dosham ? 'Dosham' : 'No Dosham'}
              </span>
            </div>
            <p className="text-xs text-gray-400">{chevvai_cross_check.note}</p>
          </div>
          <p className="text-[10px] text-gray-500 uppercase tracking-widest mt-4">
            {score.uthamam_count} Uthamam • {score.madhyamam_count} Madhyamam • {score.athamam_count} Athamam
          </p>
        </GlassCard>
      </div>
    </div>
  );
};
