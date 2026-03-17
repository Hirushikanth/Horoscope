import { useEffect, useRef } from 'react';
import { useAppStore } from '../../store/appStore';
import { GlassCard } from '../ui/GlassCard';

// Map Sanskrit Rashi names to Zodiac Numbers (1 = Aries, 12 = Pisces)
const signMap: Record<string, number> = {
  "Mesha": 1, "Vrishabha": 2, "Mithuna": 3, "Karka": 4, "Simha": 5, "Kanya": 6,
  "Tula": 7, "Vrischika": 8, "Dhanu": 9, "Makara": 10, "Kumbha": 11, "Meena": 12
};

// Map full planet names to traditional 2-letter abbreviations
const planetAbbr: Record<string, string> = {
  Sun: "Su", Moon: "Mo", Mars: "Ma", Mercury: "Me", Jupiter: "Ju", 
  Venus: "Ve", Saturn: "Sa", Rahu: "Ra", Ketu: "Ke"
};

// Mathematically calculated centroids (X, Y multipliers) for the 12 boxes of a North Indian Chart
const houseCentroids =[
  { x: 0.5, y: 0.22 },   // House 1 (Top Center Rhombus)
  { x: 0.22, y: 0.10 },  // House 2 (Top Left Triangle)
  { x: 0.10, y: 0.22 },  // House 3 (Left Top Triangle)
  { x: 0.28, y: 0.50 },  // House 4 (Left Center Rhombus)
  { x: 0.10, y: 0.78 },  // House 5 (Left Bottom Triangle)
  { x: 0.22, y: 0.90 },  // House 6 (Bottom Left Triangle)
  { x: 0.5, y: 0.78 },   // House 7 (Bottom Center Rhombus)
  { x: 0.78, y: 0.90 },  // House 8 (Bottom Right Triangle)
  { x: 0.90, y: 0.78 },  // House 9 (Right Bottom Triangle)
  { x: 0.72, y: 0.50 },  // House 10 (Right Center Rhombus)
  { x: 0.90, y: 0.22 },  // House 11 (Right Top Triangle)
  { x: 0.78, y: 0.10 },  // House 12 (Top Right Triangle)
];

export const KundliChart = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { horoscopeData } = useAppStore();

  useEffect(() => {
    if (!horoscopeData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // High-DPI Screen Support for crisp lines and text
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.parentElement?.getBoundingClientRect();
    const size = Math.min(rect?.width || 400, 500); // Responsive square
    
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;

    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, size, size);

    // ==========================================
    // 1. DRAW THE GEOMETRIC CHART (GOLD LINES)
    // ==========================================
    ctx.strokeStyle = '#D4A84B'; // Gold Primary
    ctx.lineWidth = 1.5;
    ctx.lineJoin = 'round';
    
    // Add subtle glow to the lines
    ctx.shadowColor = 'rgba(212, 168, 75, 0.4)';
    ctx.shadowBlur = 8;

    const w = size;
    const h = size;

    ctx.beginPath();
    // Outer Box
    ctx.strokeRect(2, 2, w - 4, h - 4);

    // Diagonals (Corner to Corner)
    ctx.moveTo(2, 2); ctx.lineTo(w - 2, h - 2);
    ctx.moveTo(w - 2, 2); ctx.lineTo(2, h - 2);

    // Inner Diamond (Midpoints)
    ctx.moveTo(w / 2, 2); ctx.lineTo(w - 2, h / 2);
    ctx.lineTo(w / 2, h - 2);
    ctx.lineTo(2, h / 2);
    ctx.lineTo(w / 2, 2);

    ctx.stroke();

    // Reset shadow for text
    ctx.shadowBlur = 0;

    // ==========================================
    // 2. PLOT THE DATA (RASHIS & PLANETS)
    // ==========================================
    const bhavas = horoscopeData.bhavas;

    bhavas.forEach((bhava: any, index: number) => {
      const centroid = houseCentroids[index];
      const cx = centroid.x * w;
      const cy = centroid.y * h;

      // Draw Rashi (Zodiac) Number in faded gold
      const signNum = signMap[bhava.sign];
      ctx.fillStyle = 'rgba(212, 168, 75, 0.6)';
      ctx.font = '500 12px Inter';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      // Offset the number slightly up or down depending on the house to make room for planets
      const numOffsetY = index === 0 || index === 3 || index === 6 || index === 9 ? -20 : -15;
      ctx.fillText(signNum.toString(), cx, cy + numOffsetY);

      // Draw Occupants (Planets)
      ctx.fillStyle = '#FFFFFF';
      ctx.font = '600 14px "Playfair Display"';
      
      bhava.occupants.forEach((planet: string, pIndex: number) => {
        const abbr = planetAbbr[planet] || planet.substring(0, 2);
        // Stack planets vertically if there are multiple in one house
        ctx.fillText(abbr, cx, cy + (pIndex * 16));
      });
    });

  }, [horoscopeData]);

  if (!horoscopeData) return null;

  return (
    <GlassCard className="w-full flex flex-col items-center justify-center p-6 md:p-8">
      <div className="w-full mb-6 text-center">
        <h2 className="text-gold-primary tracking-[0.2em] text-xs uppercase mb-1 font-medium">D-1 Rasi Chart</h2>
        <h3 className="font-cinematic text-2xl font-bold text-white">Lagna Kundli</h3>
      </div>
      
      {/* Container to maintain aspect ratio */}
      <div className="relative w-full max-w-[400px] aspect-square flex items-center justify-center">
        <canvas ref={canvasRef} className="block" />
      </div>
      
      <div className="w-full mt-6 grid grid-cols-2 md:grid-cols-4 gap-2 text-center text-[10px] text-gray-400 uppercase tracking-widest">
        <span>Su: Sun</span>
        <span>Mo: Moon</span>
        <span>Ju: Jupiter</span>
        <span>Ve: Venus</span>
        <span>Ma: Mars</span>
        <span>Me: Mercury</span>
        <span>Sa: Saturn</span>
        <span>Ra/Ke: Nodes</span>
      </div>
    </GlassCard>
  );
};