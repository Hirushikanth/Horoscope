import { useEffect, useRef } from 'react';

export const StarfieldBg = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let stars: { x: number; y: number; radius: number; alpha: number; deltaAlpha: number; speedX: number; speedY: number }[] =[];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initStars();
    };

    const initStars = () => {
      stars =[];
      const numStars = Math.floor((canvas.width * canvas.height) / 2000); // Responsive density
      for (let i = 0; i < numStars; i++) {
        stars.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          radius: Math.random() * 1.2,
          alpha: Math.random(),
          deltaAlpha: (Math.random() * 0.02) - 0.01,
          speedX: (Math.random() * 0.05) - 0.025, // Slow horizontal drift
          speedY: (Math.random() * 0.05) - 0.025  // Slow vertical drift
        });
      }
    };

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Deep space radial gradient
      const gradient = ctx.createRadialGradient(
        canvas.width / 2, canvas.height / 2, 0, 
        canvas.width / 2, canvas.height / 2, canvas.width
      );
      gradient.addColorStop(0, '#0B0D17');
      gradient.addColorStop(1, '#050505');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw Stars
      stars.forEach((star) => {
        // Twinkle effect
        star.alpha += star.deltaAlpha;
        if (star.alpha <= 0.1 || star.alpha >= 1) star.deltaAlpha *= -1;

        // Parallax drift
        star.x += star.speedX;
        star.y += star.speedY;

        // Screen wrap
        if (star.x < 0) star.x = canvas.width;
        if (star.x > canvas.width) star.x = 0;
        if (star.y < 0) star.y = canvas.height;
        if (star.y > canvas.height) star.y = 0;

        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(212, 168, 75, ${star.alpha * 0.8})`; // Gold-tinted stars
        ctx.fill();
      });

      animationFrameId = requestAnimationFrame(draw);
    };

    window.addEventListener('resize', resize);
    resize();
    draw();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationFrameId);
    };
  },[]);

  return (
    <canvas 
      ref={canvasRef} 
      className="fixed inset-0 z-0 pointer-events-none"
    />
  );
};