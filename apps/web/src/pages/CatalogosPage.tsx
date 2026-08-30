import { useMemo, useState } from "react";
import {
  Badge,
  Card,
  ConfirmDialog,
  EmptyRow,
  Modal,
  SearchInput,
  StatCard,
  Switch,
  TextField,
} from "../components/ui";
import { CatalogIcon, EditIcon, PlusIcon, TagIcon, TrashIcon } from "../components/ui/Icons";
import { useDatos } from "../context/DataProvider";
import { useToast } from "../context/ToastProvider";
import { CATALOGOS } from "../data/initial";
import { coincide } from "../lib/format";
import type { CatalogoTipo, ItemCatalogo } from "../types/admin";

export function CatalogosPage() {
  const { itemsCatalogo, guardarItemCatalogo, eliminarItemCatalogo } = useDatos();
  const { mostrar } = useToast();

  const [catalogoActivo, setCatalogoActivo] = useState<CatalogoTipo>("cargos");
  const [busqueda, setBusqueda] = useState("");
  const [editando, setEditando] = useState<ItemCatalogo | null>(null);
  const [aEliminar, setAEliminar] = useState<ItemCatalogo | null>(null);
  const [errores, setErrores] = useState<Record<string, string>>({});

  const definicion = CATALOGOS.find((c) => c.valor === catalogoActivo);

  const items = useMemo(
    () =>
      itemsCatalogo
        .filter((item) => item.catalogo === catalogoActivo)
        .filter(
          (item) =>
            coincide(item.nombre, busqueda) ||
            coincide(item.codigo, busqueda) ||
            coincide(item.descripcion, busqueda),
        )
        .sort((a, b) => a.orden - b.orden),
    [itemsCatalogo, catalogoActivo, busqueda],
  );

  const metricas = useMemo(() => {
    const delCatalogo = itemsCatalogo.filter((i) => i.catalogo === catalogoActivo);
    return {
      catalogos: CATALOGOS.length,
      totalItems: itemsCatalogo.length,
      enCatalogo: delCatalogo.length,
      activos: delCatalogo.filter((i) => i.activo).length,
    };
  }, [itemsCatalogo, catalogoActivo]);

  const nuevo = (): ItemCatalogo => ({
    id: "",
    catalogo: catalogoActivo,
    codigo: "",
    nombre: "",
    descripcion: "",
    orden: items.length + 1,
    activo: true,
  });

  const guardar = () => {
    if (!editando) return;

    const nuevos: Record<string, string> = {};
    if (!editando.codigo.trim()) nuevos.codigo = "El código es obligatorio.";
    if (!editando.nombre.trim()) nuevos.nombre = "El nombre es obligatorio.";

    // El código identifica el valor ante la API, así que no puede repetirse.
    const duplicado = itemsCatalogo.some(
      (i) =>
        i.catalogo === editando.catalogo &&
        i.codigo.toUpperCase() === editando.codigo.trim().toUpperCase() &&
        i.id !== editando.id,
    );
    if (duplicado) nuevos.codigo = "Ya existe un valor con este código en el catálogo.";

    setErrores(nuevos);
    if (Object.keys(nuevos).length > 0) return;

    const esNuevo = !editando.id;
    guardarItemCatalogo({
      ...editando,
      codigo: editando.codigo.trim().toUpperCase(),
      id: editando.id || `${editando.catalogo}-${Date.now()}`,
    });
    setEditando(null);
    setErrores({});
    mostrar(esNuevo ? "Valor agregado al catálogo." : "Valor actualizado.");
  };

  return (
    <>
      <div className="page-actions">
        <button type="button" className="btn btn--primary" onClick={() => setEditando(nuevo())}>
          <PlusIcon size={20} /> Nuevo valor
        </button>
      </div>

      <div className="stat-grid">
        <StatCard
          icono={<CatalogIcon size={26} />}
          color="yellow"
          etiqueta="Catálogos disponibles"
          valor={metricas.catalogos}
          pista="En total"
        />
        <StatCard
          icono={<TagIcon size={26} />}
          color="yellow"
          etiqueta="Valores registrados"
          valor={metricas.totalItems}
          pista="En todos los catálogos"
        />
        <StatCard
          icono={<TagIcon size={26} />}
          color="pink"
          etiqueta="Valores en este catálogo"
          valor={metricas.enCatalogo}
          pista={definicion?.etiqueta ?? ""}
        />
        <StatCard
          icono={<TagIcon size={26} />}
          color="pink"
          etiqueta="Valores activos"
          valor={metricas.activos}
          pista="Visibles en los formularios"
        />
      </div>

      {/* --------------------------------------------- Selector de catálogo */}
      <div className="settings-tabs" role="tablist" aria-label="Catálogos del sistema">
        {CATALOGOS.map((catalogo) => (
          <button
            key={catalogo.valor}
            type="button"
            role="tab"
            aria-selected={catalogoActivo === catalogo.valor}
            className={`settings-tab ${catalogoActivo === catalogo.valor ? "settings-tab--active" : ""}`.trim()}
            onClick={() => {
              setCatalogoActivo(catalogo.valor);
              setBusqueda("");
            }}
          >
            {catalogo.etiqueta}
          </button>
        ))}
      </div>

      <Card>
        <div className="card__head">
          <div>
            <h2 className="card__title">{definicion?.etiqueta}</h2>
            <p className="setting-row__hint" style={{ marginTop: 4 }}>
              {definicion?.descripcion}
            </p>
          </div>
          <div style={{ flex: "0 1 320px", display: "flex" }}>
            <SearchInput valor={busqueda} alCambiar={setBusqueda} placeholder="Buscar valor" />
          </div>
        </div>

        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th style={{ width: 80 }}>Orden</th>
                <th>Código</th>
                <th>Nombre</th>
                <th>Descripción</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <EmptyRow columnas={6} mensaje="Este catálogo aún no tiene valores registrados." />
              ) : (
                items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.orden}</td>
                    <td style={{ fontFamily: "ui-monospace, monospace", fontSize: 14 }}>{item.codigo}</td>
                    <td>{item.nombre}</td>
                    <td style={{ maxWidth: 340, color: "var(--fp-text-muted)" }}>{item.descripcion}</td>
                    <td>
                      <Badge tono={item.activo ? "green" : "grey"}>{item.activo ? "Activo" : "Inactivo"}</Badge>
                    </td>
                    <td>
                      <div className="table__actions">
                        <button
                          type="button"
                          className="btn btn--icon"
                          aria-label={`Editar ${item.nombre}`}
                          onClick={() => setEditando(item)}
                        >
                          <EditIcon size={19} />
                        </button>
                        <button
                          type="button"
                          className="btn btn--icon"
                          aria-label={`Eliminar ${item.nombre}`}
                          onClick={() => setAEliminar(item)}
                        >
                          <TrashIcon size={19} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* -------------------------------------------------------- Modales - */}
      <Modal
        abierto={editando !== null}
        titulo={editando?.id ? "Editar valor" : "Nuevo valor"}
        subtitulo={`Catálogo: ${definicion?.etiqueta ?? ""}`}
        ancho="ancho"
        alCerrar={() => {
          setEditando(null);
          setErrores({});
        }}
        pie={
          <>
            <button
              type="button"
              className="btn btn--neutral"
              onClick={() => {
                setEditando(null);
                setErrores({});
              }}
            >
              Cancelar
            </button>
            <button type="button" className="btn btn--primary" onClick={guardar}>
              Guardar valor
            </button>
          </>
        }
      >
        {editando ? (
          <>
            <div className="modal__grid">
              <TextField
                etiqueta="Código"
                requerido
                placeholder="CAJ"
                valor={editando.codigo}
                error={errores.codigo}
                alCambiar={(v) => setEditando({ ...editando, codigo: v.toUpperCase() })}
              />
              <TextField
                etiqueta="Nombre"
                requerido
                valor={editando.nombre}
                error={errores.nombre}
                alCambiar={(v) => setEditando({ ...editando, nombre: v })}
              />
              <TextField
                etiqueta="Orden"
                tipo="number"
                valor={String(editando.orden)}
                alCambiar={(v) => setEditando({ ...editando, orden: Number(v) || 0 })}
              />
            </div>

            <div className="field">
              <label className="field__label" htmlFor="catalogo-descripcion">
                Descripción
              </label>
              <textarea
                id="catalogo-descripcion"
                className="textarea"
                value={editando.descripcion}
                onChange={(e) => setEditando({ ...editando, descripcion: e.target.value })}
              />
            </div>

            <div className="setting-row">
              <div>
                <p className="setting-row__label">Valor activo</p>
                <p className="setting-row__hint">
                  Los valores inactivos dejan de aparecer en los formularios, pero se conservan en los
                  registros históricos que ya los usaban.
                </p>
              </div>
              <Switch
                marcado={editando.activo}
                etiqueta="Valor activo"
                alCambiar={(v) => setEditando({ ...editando, activo: v })}
              />
            </div>
          </>
        ) : null}
      </Modal>

      <ConfirmDialog
        abierto={aEliminar !== null}
        titulo="Eliminar valor del catálogo"
        mensaje={`Se eliminará "${aEliminar?.nombre ?? ""}". Si algún registro lo está usando, conviene desactivarlo en lugar de borrarlo.`}
        alCerrar={() => setAEliminar(null)}
        alConfirmar={() => {
          if (aEliminar) {
            eliminarItemCatalogo(aEliminar.id);
            mostrar("Valor eliminado del catálogo.");
          }
          setAEliminar(null);
        }}
      />
    </>
  );
}
