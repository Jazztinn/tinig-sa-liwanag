import { useEffect, useRef } from "react";
import createGlobe from "cobe";

// Magic UI–style globe (cobe). Auto-rotates, gently draggable. Tuned for a
// dark cinematic backdrop with a warm amber marker over the Philippines.
const DEFAULT_CONFIG = {
  width: 800,
  height: 800,
  onRender: () => {},
  devicePixelRatio: 2,
  phi: 0,
  theta: 0.28,
  dark: 1,
  diffuse: 1.1,
  mapSamples: 16000,
  mapBrightness: 5,
  baseColor: [0.32, 0.32, 0.36],
  markerColor: [255 / 255, 180 / 255, 84 / 255], // amber
  glowColor: [0.18, 0.16, 0.12],
  markers: [
    { location: [10.72, 122.56], size: 0.1 }, // Iloilo / Panay (Hiligaynon)
    { location: [10.67, 122.95], size: 0.07 }, // Negros Occidental
    { location: [14.6, 120.98], size: 0.04 }, // Manila
  ],
};

export default function Globe({ className = "", style = {}, config = {} }) {
  const canvasRef = useRef(null);
  const phiRef = useRef(0);
  const pointerInteracting = useRef(null);
  const pointerMovement = useRef(0);

  useEffect(() => {
    let width = 0;
    const onResize = () => {
      if (canvasRef.current) width = canvasRef.current.offsetWidth;
    };
    window.addEventListener("resize", onResize);
    onResize();

    const globe = createGlobe(canvasRef.current, {
      ...DEFAULT_CONFIG,
      ...config,
      width: width * 2,
      height: width * 2,
      onRender: (state) => {
        if (pointerInteracting.current === null) phiRef.current += 0.003;
        state.phi = phiRef.current + pointerMovement.current;
        state.width = width * 2;
        state.height = width * 2;
      },
    });

    setTimeout(() => {
      if (canvasRef.current) canvasRef.current.style.opacity = "1";
    }, 0);

    return () => {
      globe.destroy();
      window.removeEventListener("resize", onResize);
    };
  }, []); // eslint-disable-line

  return (
    <div
      className={className}
      style={{ width: "100%", maxWidth: 600, aspectRatio: "1", margin: "0 auto", ...style }}
    >
      <canvas
        ref={canvasRef}
        onPointerDown={(e) => {
          pointerInteracting.current = e.clientX - pointerMovement.current;
          canvasRef.current.style.cursor = "grabbing";
        }}
        onPointerUp={() => {
          pointerInteracting.current = null;
          canvasRef.current.style.cursor = "grab";
        }}
        onPointerOut={() => {
          pointerInteracting.current = null;
        }}
        onPointerMove={(e) => {
          if (pointerInteracting.current !== null) {
            const delta = e.clientX - pointerInteracting.current;
            pointerMovement.current = delta / 200;
          }
        }}
        style={{ width: "100%", height: "100%", contain: "layout paint size", opacity: 0, transition: "opacity 1s ease", cursor: "grab" }}
      />
    </div>
  );
}
