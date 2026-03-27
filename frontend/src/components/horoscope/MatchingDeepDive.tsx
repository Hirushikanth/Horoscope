import { useAppStore } from '../../store/appStore';
import { GlassAccordion } from '../ui/GlassAccordion';
import { CheckCircle2, XCircle, AlertTriangle, Clock, Compass, Sparkles } from 'lucide-react';

export const MatchingDeepDive = () => {
  const { matchingData, matchingInput } = useAppStore();
  if (!matchingData) return null;

  const { 
    navamsa_compatibility: d9, 
    lagna_analysis: lagna, 
    dasha_compatibility: dasha, 
    south_indian_poruthams: south
  } = matchingData;

  const showSouthIndian = matchingInput?.system === 'south_indian' || matchingInput?.system === 'both';

  return (
    <div className="w-full mt-12 pb-12">
      <div className="mb-6 px-2">
        <h2 className="font-cinematic text-3xl font-bold text-white">Astrological Deep Dive</h2>
        <p className="text-sm text-gray-400 mt-1">Advanced metrics: Navamsa, Lagna, and Dasha Timing</p>
      </div>

      <div className="flex flex-col space-y-4">
        
        {/* 1. NAVAMSA (D9) ACCORDION */}
        {d9 && (
          <GlassAccordion
            title="Navamsa (D9) Synthesis"
            subtitle="The soul's truth and marital endurance"
            badges={
              <span className={`text-[10px] uppercase tracking-widest px-2 py-1 rounded border ${
                d9.assessment === 'Strong' ? 'border-green-400/30 bg-green-400/10 text-green-400' :
                d9.assessment === 'Weak' ? 'border-red-400/30 bg-red-400/10 text-red-400' :
                'border-gold-primary/30 bg-gold-primary/10 text-gold-light'
              }`}>
                {d9.assessment} Match
              </span>
            }
          >
            <div className="space-y-6">
              <p className="text-gray-300 leading-relaxed text-sm">{d9.assessment_description}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-white/10 pt-4">
                <div>
                  <p className="text-gold-primary text-xs uppercase tracking-widest mb-2 flex items-center gap-2"><Sparkles size={14}/> Bride's D9</p>
                  <p className="text-white">Lagna: {d9.bride.d9_lagna}</p>
                  <p className="text-white">7th Lord: {d9.bride.d9_7th_lord}</p>
                  {d9.bride.jupiter_d9 && <p className="text-gray-400 text-xs mt-1">Jupiter (Karaka): {d9.bride.jupiter_d9.dignity}</p>}
                </div>
                <div>
                  <p className="text-gold-primary text-xs uppercase tracking-widest mb-2 flex items-center gap-2"><Sparkles size={14}/> Groom's D9</p>
                  <p className="text-white">Lagna: {d9.groom.d9_lagna}</p>
                  <p className="text-white">7th Lord: {d9.groom.d9_7th_lord}</p>
                  {d9.groom.venus_d9 && <p className="text-gray-400 text-xs mt-1">Venus (Karaka): {d9.groom.venus_d9.dignity}</p>}
                </div>
              </div>

              <div className="bg-black/30 p-4 rounded-lg border border-white/5">
                <p className="text-gold-light text-xs uppercase tracking-widest mb-3">D9 Compatibility Factors</p>
                <ul className="space-y-2">
                  {d9.compatibility_factors.map((factor: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                      <CheckCircle2 size={16} className="text-green-400 flex-shrink-0 mt-0.5" />
                      <span>{factor}</span>
                    </li>
                  ))}
                  {d9.compatibility_factors.length === 0 && <li className="text-gray-500 text-sm">No major D9 alignments detected.</li>}
                </ul>
              </div>
            </div>
          </GlassAccordion>
        )}

        {/* 2. LAGNA & ARUDHA ACCORDION */}
        {lagna && (
          <GlassAccordion
            title="Lagna & Upapada Analysis"
            subtitle="7th House, Karakas, and Arudha Padas"
            badges={
              lagna.lagna_warnings.length > 0 ? (
                <span className="text-[10px] uppercase tracking-widest px-2 py-1 rounded border border-orange-500/30 bg-orange-500/10 text-orange-400 flex items-center gap-1">
                  <AlertTriangle size={12} /> {lagna.lagna_warnings.length} Warnings
                </span>
              ) : null
            }
          >
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* 7th House Breakdown */}
                <div className="space-y-2">
                  <p className="text-gold-primary text-xs uppercase tracking-widest mb-2 flex items-center gap-2"><Compass size={14}/> 7th House Quality</p>
                  <p className="text-sm text-white"><span className="text-gray-400">Bride:</span> {lagna.seventh_house.bride.assessment_description}</p>
                  <p className="text-sm text-white"><span className="text-gray-400">Groom:</span> {lagna.seventh_house.groom.assessment_description}</p>
                </div>

                {/* Upapada Lagna Breakdown */}
                <div className="space-y-2">
                  <p className="text-gold-primary text-xs uppercase tracking-widest mb-2 flex items-center gap-2"><Compass size={14}/> Upapada Lagna (UL)</p>
                  <p className="text-sm text-white"><span className="text-gray-400">Bride UL:</span> {lagna.upapada_lagna.bride.ul_sign}</p>
                  <p className="text-sm text-white"><span className="text-gray-400">Groom UL:</span> {lagna.upapada_lagna.groom.ul_sign}</p>
                  {lagna.upapada_lagna.cross_chart_notes.map((note: string, i: number) => (
                    <p key={i} className="text-xs text-green-400 mt-1 flex items-center gap-1"><CheckCircle2 size={12}/> {note}</p>
                  ))}
                </div>
              </div>

              {/* Warnings List */}
              {lagna.lagna_warnings.length > 0 && (
                <div className="bg-orange-500/10 p-4 rounded-lg border border-orange-500/20 mt-4">
                  <p className="text-orange-400 text-xs uppercase tracking-widest mb-3">Lagna Chart Cautions</p>
                  <ul className="space-y-2">
                    {lagna.lagna_warnings.map((warning: string, i: number) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                        <AlertTriangle size={16} className="text-orange-400 flex-shrink-0 mt-0.5" />
                        <span>{warning}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </GlassAccordion>
        )}

        {/* 3. DASHA SYNCHRONIZATION ACCORDION */}
        {dasha && (
          <GlassAccordion
            title="Dasha Synchronization"
            subtitle="Current planetary life periods"
            badges={
              <span className={`text-[10px] uppercase tracking-widest px-2 py-1 rounded border ${
                dasha.assessment === 'Favorable' ? 'border-green-400/30 bg-green-400/10 text-green-400' :
                dasha.assessment === 'Challenging' ? 'border-red-400/30 bg-red-400/10 text-red-400' :
                'border-gold-primary/30 bg-gold-primary/10 text-gold-light'
              }`}>
                {dasha.assessment}
              </span>
            }
          >
            <div className="space-y-6">
              <p className="text-gray-300 leading-relaxed text-sm">{dasha.assessment_description}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-white/10 pt-4">
                <div className="bg-white/5 p-4 rounded-lg border border-white/10">
                  <p className="text-gold-primary text-xs uppercase tracking-widest mb-3 flex items-center gap-2"><Clock size={14}/> Bride's Current Era</p>
                  <h4 className="font-cinematic text-2xl text-white">{dasha.bride_dasha.mahadasha_lord} <span className="text-sm text-gray-400 font-sans">Mahadasha</span></h4>
                  <p className="text-xs text-gray-400 mt-1">Antardasha: {dasha.bride_dasha.antardasha_lord}</p>
                  <p className="text-xs text-gray-500 mt-1">Ends: {dasha.bride_dasha.mahadasha_end}</p>
                </div>
                <div className="bg-white/5 p-4 rounded-lg border border-white/10">
                  <p className="text-gold-primary text-xs uppercase tracking-widest mb-3 flex items-center gap-2"><Clock size={14}/> Groom's Current Era</p>
                  <h4 className="font-cinematic text-2xl text-white">{dasha.groom_dasha.mahadasha_lord} <span className="text-sm text-gray-400 font-sans">Mahadasha</span></h4>
                  <p className="text-xs text-gray-400 mt-1">Antardasha: {dasha.groom_dasha.antardasha_lord}</p>
                  <p className="text-xs text-gray-500 mt-1">Ends: {dasha.groom_dasha.mahadasha_end}</p>
                </div>
              </div>

              {(dasha.factors.length > 0 || dasha.warnings.length > 0) && (
                <div className="space-y-2 mt-4 border-t border-white/10 pt-4">
                  {dasha.factors.map((f: string, i: number) => (
                    <p key={i} className="text-sm text-green-400 flex items-start gap-2"><CheckCircle2 size={16} className="mt-0.5 flex-shrink-0"/> {f}</p>
                  ))}
                  {dasha.warnings.map((w: string, i: number) => (
                    <p key={i} className="text-sm text-orange-400 flex items-start gap-2"><AlertTriangle size={16} className="mt-0.5 flex-shrink-0"/> {w}</p>
                  ))}
                </div>
              )}
            </div>
          </GlassAccordion>
        )}

        {/* 4. SOUTH INDIAN PORUTHAMS ACCORDION */}
        {showSouthIndian && south && (
          <GlassAccordion
            title="Dashakoota (10 Poruthams)"
            subtitle="South Indian compatibility system"
            badges={
              <span className={`text-[10px] uppercase tracking-widest px-2 py-1 rounded border ${
                south.total_matches >= 6 ? 'border-green-400/30 bg-green-400/10 text-green-400' :
                'border-red-400/30 bg-red-400/10 text-red-400'
              }`}>
                {south.total_matches}/10 Matched
              </span>
            }
          >
            <div className="space-y-4">
              <p className="text-gray-300 text-sm mb-4">{south.assessment}</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-3">
                {Object.entries(south.poruthams).map(([name, data]: [string, any]) => (
                  <div key={name} className="flex items-start gap-3 p-3 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                    {data.match ? (
                      <CheckCircle2 className="text-green-400 flex-shrink-0 mt-0.5" size={18} />
                    ) : (
                      <XCircle className="text-red-400 flex-shrink-0 mt-0.5" size={18} />
                    )}
                    <div>
                      <h4 className={`text-sm font-bold ${data.match ? 'text-white' : 'text-gray-400'}`}>{name}</h4>
                      <p className="text-xs text-gray-500 mt-1 leading-relaxed">{data.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </GlassAccordion>
        )}

      </div>
    </div>
  );
};