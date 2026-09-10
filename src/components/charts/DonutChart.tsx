import { useState } from "react";

export interface SegmentoDona {
  clave: string;
  etiqueta: string;
  valor: number;
  color: string;
}

interface Props {
  segmentos: SegmentoDona[];
  tamano?: number;
  grosor?: number;
}

/** Punto de la circunferencia en coordenadas cartesianas. */
function punto(cx: number, cy: number, radio: number, grados: number) {
  const rad = ((grados - 90) * Math.PI) / 180;
  return { x: cx + radio * Math.cos(rad), y: cy + radio * Math.sin(rad) };
}

/** Sector anular entre dos ángulos. */
function arco(
  cx: number,
  cy: number,
  rExterno: number,
  rInterno: number,
  desde: number,
  hasta: number,
): string {
  const barrido = hasta - desde;
  // Un segmento de 360° no se puede dibujar con un solo arco: se parte en dos.
  const fin = barrido >= 360 ? desde + 359.99 : hasta;
  const grande = fin - desde > 180 ? 1 : 0;

  const e1 = punto(cx, cy, rExterno, desde);
  const e2 = punto(cx, cy, rExterno, fin);
  const i2 = punto(cx, cy, rInterno, fin);
  const i1 = punto(cx, cy, rInterno, desde);

  return [
    `M ${e1.x} ${e1.y}`,
    `A ${rExterno} ${rExterno} 0 ${grande} 1 ${e2.x} ${e2.y}`,
    `L ${i2.x} ${i2.y}`,
    `A ${rInterno} ${rInterno} 0 ${grande} 0 ${i1.x} ${i1.y}`,
    "Z",
  ].join(" ");
}

export function DonutChart({ segmentos, tamano = 210, grosor = 46 }: Props) {
  const [activo, setActivo] = useState<string | null>(null);

  const total = segmentos.reduce((suma, s) => suma + s.valor, 0);
  const cx = tamano / 2;
  const cy = tamano / 2;
  const rExterno = tamano / 2 - 4;
  const rInterno = rExterno - grosor;

  let angulo = 0;
  const trazos = segmentos.map((segmento) => {
    const barrido = total > 0 ? (segmento.valor / total) * 360 : 0;
    const d = arco(cx, cy, rExterno, rInterno, angulo, angulo + barrido);
    angulo += barrido;
    return { ...segmento, d };
  });

  return (
    <svg
      className="donut-svg"
      width={tamano}
      height={tamano}
      viewBox={`0 0 ${tamano} ${tamano}`}
      role="img"
      aria-label={`Distribución de asistencia: ${segmentos
        .map((s) => `${s.etiqueta} ${s.valor}`)
        .join(", ")}`}
    >
      {total === 0 ? (
        <circle cx={cx} cy={cy} r={(rExterno + rInterno) / 2} fill="none" stroke="#efe7e0" strokeWidth={grosor} />
      ) : (
        trazos.map((trazo) => (
          <path
            key={trazo.clave}
            d={trazo.d}
            fill={trazo.color}
            opacity={activo && activo !== trazo.clave ? 0.35 : 1}
            onMouseEnter={() => setActivo(trazo.clave)}
            onMouseLeave={() => setActivo(null)}
          >
            <title>{`${trazo.etiqueta}: ${trazo.valor}`}</title>
          </path>
        ))
      )}
    </svg>
  );
}
