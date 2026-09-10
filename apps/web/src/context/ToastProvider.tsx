import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { CheckCircleIcon, AlertCircleIcon, InfoIcon } from "../components/ui/Icons";

type ToastTipo = "success" | "error" | "info";

interface Toast {
  id: number;
  mensaje: string;
  tipo: ToastTipo;
}

interface ToastContextValue {
  mostrar: (mensaje: string, tipo?: ToastTipo) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

let contador = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const mostrar = useCallback((mensaje: string, tipo: ToastTipo = "success") => {
    contador += 1;
    const id = contador;
    setToasts((previos) => [...previos, { id, mensaje, tipo }]);
    window.setTimeout(() => {
      setToasts((previos) => previos.filter((t) => t.id !== id));
    }, 3600);
  }, []);

  const valor = useMemo(() => ({ mostrar }), [mostrar]);

  return (
    <ToastContext.Provider value={valor}>
      {children}
      <div className="toast-stack" role="status" aria-live="polite">
        {toasts.map((toast) => (
          <div key={toast.id} className={`toast toast--${toast.tipo}`}>
            {toast.tipo === "success" ? (
              <CheckCircleIcon size={18} />
            ) : toast.tipo === "error" ? (
              <AlertCircleIcon size={18} />
            ) : (
              <InfoIcon size={18} />
            )}
            <span>{toast.mensaje}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast debe usarse dentro de ToastProvider");
  return ctx;
}
