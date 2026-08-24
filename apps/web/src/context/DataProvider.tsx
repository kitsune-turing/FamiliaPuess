import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import {
  AUDITORIAS,
  DISPOSITIVOS,
  ITEMS_CATALOGO,
  PARAMETROS,
  REGISTROS,
  REPORTES,
  SEDES,
  SESIONES,
  TRABAJADORES,
  USUARIOS,
} from "../data/initial";
import type {
  Auditoria,
  Dispositivo,
  ItemCatalogo,
  Parametro,
  RegistroEntrada,
  Reporte,
  Sede,
  SesionActiva,
  Trabajador,
  Usuario,
} from "../types/admin";

interface DataContextValue {
  sedes: Sede[];
  trabajadores: Trabajador[];
  dispositivos: Dispositivo[];
  usuarios: Usuario[];
  reportes: Reporte[];
  registros: RegistroEntrada[];
  auditorias: Auditoria[];
  sesiones: SesionActiva[];
  itemsCatalogo: ItemCatalogo[];
  parametros: Parametro[];

  guardarSede: (sede: Sede) => void;
  eliminarSede: (id: string) => void;

  guardarTrabajador: (trabajador: Trabajador) => void;
  eliminarTrabajador: (id: string) => void;

  guardarDispositivo: (dispositivo: Dispositivo) => void;
  eliminarDispositivo: (id: string) => void;

  guardarUsuario: (usuario: Usuario) => void;
  eliminarUsuario: (id: string) => void;

  agregarReporte: (reporte: Reporte) => void;
  eliminarReporte: (id: string) => void;

  guardarItemCatalogo: (item: ItemCatalogo) => void;
  eliminarItemCatalogo: (id: string) => void;

  guardarParametro: (parametro: Parametro) => void;
  restablecerParametros: () => void;

  cerrarSesionRemota: (id: string) => void;
  registrarAuditoria: (entrada: Auditoria) => void;
}

const DataContext = createContext<DataContextValue | null>(null);

/** Inserta o actualiza por id conservando el orden original. */
function upsert<T extends { id: string }>(lista: T[], elemento: T): T[] {
  const indice = lista.findIndex((item) => item.id === elemento.id);
  if (indice === -1) return [elemento, ...lista];
  const copia = [...lista];
  copia[indice] = elemento;
  return copia;
}

export function DataProvider({ children }: { children: ReactNode }) {
  const [sedes, setSedes] = useState<Sede[]>(SEDES);
  const [trabajadores, setTrabajadores] = useState<Trabajador[]>(TRABAJADORES);
  const [dispositivos, setDispositivos] = useState<Dispositivo[]>(DISPOSITIVOS);
  const [usuarios, setUsuarios] = useState<Usuario[]>(USUARIOS);
  const [reportes, setReportes] = useState<Reporte[]>(REPORTES);
  const [registros] = useState<RegistroEntrada[]>(REGISTROS);
  const [auditorias, setAuditorias] = useState<Auditoria[]>(AUDITORIAS);
  const [sesiones, setSesiones] = useState<SesionActiva[]>(SESIONES);
  const [itemsCatalogo, setItemsCatalogo] = useState<ItemCatalogo[]>(ITEMS_CATALOGO);
  const [parametros, setParametros] = useState<Parametro[]>(PARAMETROS);

  const registrarAuditoria = useCallback((entrada: Auditoria) => {
    setAuditorias((previas) => [entrada, ...previas]);
  }, []);

  const valor = useMemo<DataContextValue>(
    () => ({
      sedes,
      trabajadores,
      dispositivos,
      usuarios,
      reportes,
      registros,
      auditorias,
      sesiones,
      itemsCatalogo,
      parametros,

      guardarSede: (sede) => setSedes((previas) => upsert(previas, sede)),
      eliminarSede: (id) => setSedes((previas) => previas.filter((s) => s.id !== id)),

      guardarTrabajador: (trabajador) => setTrabajadores((previos) => upsert(previos, trabajador)),
      eliminarTrabajador: (id) => setTrabajadores((previos) => previos.filter((t) => t.id !== id)),

      guardarDispositivo: (dispositivo) =>
        setDispositivos((previos) => upsert(previos, dispositivo)),
      eliminarDispositivo: (id) => setDispositivos((previos) => previos.filter((d) => d.id !== id)),

      guardarUsuario: (usuario) => setUsuarios((previos) => upsert(previos, usuario)),
      eliminarUsuario: (id) => setUsuarios((previos) => previos.filter((u) => u.id !== id)),

      agregarReporte: (reporte) => setReportes((previos) => [reporte, ...previos]),
      eliminarReporte: (id) => setReportes((previos) => previos.filter((r) => r.id !== id)),

      guardarItemCatalogo: (item) => setItemsCatalogo((previos) => upsert(previos, item)),
      eliminarItemCatalogo: (id) => setItemsCatalogo((previos) => previos.filter((i) => i.id !== id)),

      guardarParametro: (parametro) => setParametros((previos) => upsert(previos, parametro)),
      restablecerParametros: () => setParametros(PARAMETROS),

      cerrarSesionRemota: (id) => setSesiones((previas) => previas.filter((s) => s.id !== id)),
      registrarAuditoria,
    }),
    [
      sedes,
      trabajadores,
      dispositivos,
      usuarios,
      reportes,
      registros,
      auditorias,
      sesiones,
      itemsCatalogo,
      parametros,
      registrarAuditoria,
    ],
  );

  return <DataContext.Provider value={valor}>{children}</DataContext.Provider>;
}

export function useDatos(): DataContextValue {
  const ctx = useContext(DataContext);
  if (!ctx) throw new Error("useDatos debe usarse dentro de DataProvider");
  return ctx;
}
