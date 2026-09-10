import mazorcaImg from "../assets/images/mazorca.png";
import "../styles/registro.css";

export function AccesoDenegadoPage() {
  return (
    <div className="registro-page">
      <img src={mazorcaImg} alt="" className="mazorca mazorca--top-left" />
      <img src={mazorcaImg} alt="" className="mazorca mazorca--bottom-left" />
      <img src={mazorcaImg} alt="" className="mazorca mazorca--top-right" />
      <img src={mazorcaImg} alt="" className="mazorca mazorca--bottom-right" />

      <div className="registro-message registro-message--error">
        <div className="registro-message__icon">&#128274;</div>
        <h2 className="registro-message__title">Acceso no autorizado</h2>
        <p className="registro-message__text">
          No tiene autorizacion para acceder a esta seccion.
          El registro de asistencia unicamente puede realizarse
          mediante el escaneo del codigo QR en su sede.
        </p>
      </div>
    </div>
  );
}
