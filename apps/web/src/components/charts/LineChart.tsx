import { useMemo, useState } from "react";

export interface PuntoSerie {
  etiqueta: string;
  valor: number;
}

interface Props {
  serie: PuntoSerie[];
  alto?: number;
  /** Índices que muestran un marcador circular sobre la curva. */
  marcadores?: number[];
  sufijo?: string;
}

const ANCHO = 460;
const PAD_X = 14;
const PAD_TOP = 58;
const PAD_BOTTOM = 30;

/** Curva Catmull-Rom convertida a Bézier cúbica para un trazo suave. */
function curva(puntos: { x: number; y: number }[]): string {
  if (puntos.length === 0) return "";
  const primero = puntos[0];
  if (!primero) return "";
  if (puntos.length === 1) return `M ${primero.x} ${primero.y}`;

  let d = `M ${primero.x} ${primero.y}`;
  for (let i = 0; i < puntos.length - 1; i += 1) {
    const p0 = puntos[Math.max(0, i - 1)];
    const p1 = puntos[i];
    const p2 = puntos[i + 1];
    const p3 = puntos[Math.min(puntos.length - 1, i + 2)];
    if (!p0 || !p1 || !p2 || !p3) continue;

    const c1x = p1.x + (p2.x - p0.x) / 6;
    const c1y = p1.y + (p2.y - p0.y) / 6;
    const c2x = p2.x - (p3.x - p1.x) / 6;
    const c2y = p2.y - (p3.y - p1.y) / 6;
    d += ` C ${c1x} ${c1y} ${c2x} ${c2y} ${p2.x} ${p2.y}`;
  }
  return d;
}

export function LineChart({ serie, alto = 240, marcadores, sufijo = "entradas" }: Props) {
  const [activo, setActivo] = useState<number>(() => {
    if (serie.length === 0) return 0;
    const indice = serie.reduce(
      (mejor, actual, i) => ((serie[mejor]?.valor ?? 0) < actual.valor ? i : mejor),
      0,
    );
    return marcadores?.[0] ?? indice;
  });

  const geometria = useMemo(() => {
    if (serie.length === 0) return { puntos: [], trazo: "", area: "" };
    const valores = serie.map((p) => p.valor);
    const max = Math.max(...valores, 1);
    const min = Math.min(...valores, 0);
    const rango = max - min || 1;
    const anchoUtil = ANCHO - PAD_X * 2;
    const altoUtil = alto - PAD_TOP - PAD_BOTTOM;

    const puntos = serie.map((p, i) => ({
      x: PAD_X + (serie.length === 1 ? anchoUtil / 2 : (i / (serie.length - 1)) * anchoUtil),
      y: PAD_TOP + altoUtil - ((p.valor - min) / rango) * altoUtil,
    }));

    const trazo = curva(puntos);
    const ultimo = puntos[puntos.length - 1];
    const primero = puntos[0];
    const area =
      trazo && ultimo && primero
        ? `${trazo} L ${ultimo.x} ${alto - PAD_BOTTOM} L ${primero.x} ${alto - PAD_BOTTOM} Z`
        : "";

    return { puntos, trazo, area };
  }, [serie, alto]);

  const indicesMarcador = marcadores ?? serie.map((_, i) => i).filter((i) => i % 2 === 0);
  const puntoActivo = geometria.puntos[activo];
  const datoActivo = serie[activo];

  if (serie.length === 0) {
    return (
      <div className="linechart linechart--empty" style={{ height: alto }}>
        <p className="empty-note">Sin datos para el periodo seleccionado.</p>
      </div>
    );
  }

  return (
    <div className="linechart">
      {datoActivo ? (
        <div className="linechart__tooltip">
          <p className="linechart__tooltip-title">{datoActivo.etiqueta}</p>
          <p className="linechart__tooltip-value">
            <span className="linechart__tooltip-dot" />
            {datoActivo.valor} {sufijo}
          </p>
        </div>
      ) : null}

      <svg
        width="100%"
        height={alto}
        viewBox={`0 0 ${ANCHO} ${alto}`}
        preserveAspectRatio="none"
        role="img"
        aria-label={`Entradas por hora: ${serie.map((p) => `${p.etiqueta} ${p.valor}`).join(", ")}`}
      >
        <defs>
          <linearGradient id="fp-line-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#f24976" stopOpacity="0.22" />
            <stop offset="100%" stopColor="#f24976" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Líneas guía verticales */}
        {indicesMarcador.map((i) => {
          const p = geometria.puntos[i];
          if (!p) return null;
          return (
            <line
              key={`guia-${i}`}
              x1={p.x}
              y1={PAD_TOP - 24}
              x2={p.x}
              y2={alto - PAD_BOTTOM}
              stroke="#f3e6e9"
              strokeWidth="1"
            />
          );
        })}

        <path d={geometria.area} fill="url(#fp-line-fill)" />
        <path
          d={geometria.trazo}
          fill="none"
          stroke="#f24976"
          strokeWidth="2.4"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Zonas sensibles al puntero */}
        {geometria.puntos.map((p, i) => (
          <rect
            key={`hit-${i}`}
            x={p.x - (ANCHO - PAD_X * 2) / (serie.length * 2)}
            y={0}
            width={(ANCHO - PAD_X * 2) / serie.length}
            height={alto}
            fill="transparent"
            onMouseEnter={() => setActivo(i)}
          />
        ))}

        {indicesMarcador.map((i) => {
          const p = geometria.puntos[i];
          if (!p) return null;
          return (
            <circle
              key={`marca-${i}`}
              cx={p.x}
              cy={p.y}
              r="4.2"
              fill="#fff"
              stroke="#2f2c29"
              strokeWidth="1.6"
            />
          );
        })}

        {puntoActivo ? (
          <circle cx={puntoActivo.x} cy={puntoActivo.y} r="5.4" fill="#f24976" stroke="#fff" strokeWidth="2" />
        ) : null}
      </svg>

      <div style={{ position: "relative", height: 20, marginTop: -20 }}>
        {indicesMarcador.map((i) => {
          const p = geometria.puntos[i];
          const dato = serie[i];
          if (!p || !dato) return null;
          return (
            <span
              key={`eje-${i}`}
              style={{
                position: "absolute",
                left: `${(p.x / ANCHO) * 100}%`,
                transform: "translateX(-50%)",
                fontSize: 13,
                color: "var(--fp-text-faint)",
                whiteSpace: "nowrap",
              }}
            >
              {dato.etiqueta}
            </span>
          );
        })}
      </div>
    </div>
  );
}
