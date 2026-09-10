/* ==========================================================================
   Iconos.

   Todos los iconos son SVG en línea con trazo de 1.8 px para que hereden el
   color del texto y no dependan de librerías externas.
   ========================================================================== */

export interface IconProps {
  size?: number;
  strokeWidth?: number;
  className?: string;
}

function base(size: number, strokeWidth: number, className?: string) {
  return {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    className,
    "aria-hidden": true,
    focusable: false,
  };
}

type P = IconProps;

/* ------------------------------------------------------- Navegación ----- */

export const HomeIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M4 10.5 12 3.5l8 7V19a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2Z" />
    <circle cx="12" cy="11.5" r="1.6" />
  </svg>
);

export const ClockIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5.2l3.2 2" />
  </svg>
);

export const UsersIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <circle cx="10" cy="8" r="3.6" />
    <path d="M3.5 20.5a6.8 6.8 0 0 1 13 0" />
    <path d="M16.5 5.2a3.6 3.6 0 0 1 0 6.6" />
    <path d="M18.4 14.6a6.4 6.4 0 0 1 3.1 4.6" />
  </svg>
);

export const MonitorIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <rect x="2.5" y="4" width="19" height="12.5" rx="2" />
    <path d="M8.5 20.5h7M12 16.5v4" />
  </svg>
);

export const MapPinIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M19 10.4c0 5.2-7 11.1-7 11.1s-7-5.9-7-11.1a7 7 0 1 1 14 0Z" />
    <circle cx="12" cy="10.2" r="2.6" />
  </svg>
);

export const ChartIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M4 20V9.5M9.3 20V4.5M14.7 20v-8M20 20v-5" />
  </svg>
);

export const ShieldIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M12 2.8 4.8 5.6v6.1c0 4.4 3 8.4 7.2 9.5 4.2-1.1 7.2-5.1 7.2-9.5V5.6Z" />
  </svg>
);

export const SettingsIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <circle cx="12" cy="12" r="3.1" />
    <path d="M19.5 14.4a1.6 1.6 0 0 0 .3 1.8l.1.1a1.9 1.9 0 1 1-2.7 2.7l-.1-.1a1.6 1.6 0 0 0-1.8-.3 1.6 1.6 0 0 0-1 1.5v.2a1.9 1.9 0 1 1-3.8 0v-.1a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.8.3l-.1.1a1.9 1.9 0 1 1-2.7-2.7l.1-.1a1.6 1.6 0 0 0 .3-1.8 1.6 1.6 0 0 0-1.5-1h-.2a1.9 1.9 0 1 1 0-3.8h.1a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.3-1.8l-.1-.1a1.9 1.9 0 1 1 2.7-2.7l.1.1a1.6 1.6 0 0 0 1.8.3h.1a1.6 1.6 0 0 0 1-1.5v-.2a1.9 1.9 0 1 1 3.8 0v.1a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.3l.1-.1a1.9 1.9 0 1 1 2.7 2.7l-.1.1a1.6 1.6 0 0 0-.3 1.8v.1a1.6 1.6 0 0 0 1.5 1h.2a1.9 1.9 0 1 1 0 3.8h-.1a1.6 1.6 0 0 0-1.5 1Z" />
  </svg>
);

export const LockIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <rect x="4.5" y="10.2" width="15" height="10.3" rx="2.2" />
    <path d="M8.2 10.2V7.4a3.8 3.8 0 0 1 7.6 0v2.8" />
    <circle cx="12" cy="15.3" r="1.3" />
  </svg>
);

export const ClipboardIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <rect x="4.5" y="3.6" width="15" height="17" rx="2.4" />
    <path d="M8.6 8.4h6.8M8.6 12.2h6.8M8.6 16h4.2" />
  </svg>
);

/* ------------------------------------------------------- Interfaz ------- */

export const BellIcon = ({ size = 24, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M6.2 9.4a5.8 5.8 0 0 1 11.6 0c0 4 1.4 5.6 1.4 5.6H4.8s1.4-1.6 1.4-5.6Z" />
    <path d="M10.2 18.6a2 2 0 0 0 3.6 0" />
    <path d="M3.4 6.2a5 5 0 0 1 2-2.6M20.6 6.2a5 5 0 0 0-2-2.6" />
  </svg>
);

export const ChevronDownIcon = ({ size = 20, strokeWidth = 2.2, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="m6 9.5 6 5.5 6-5.5" />
  </svg>
);

export const ChevronLeftIcon = ({ size = 18, strokeWidth = 2, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="m14.5 5.5-6 6.5 6 6.5" />
  </svg>
);

export const ChevronRightIcon = ({ size = 18, strokeWidth = 2, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="m9.5 5.5 6 6.5-6 6.5" />
  </svg>
);

export const MenuIcon = ({ size = 22, strokeWidth = 2, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M4 7h16M4 12h16M4 17h16" />
  </svg>
);

export const SearchIcon = ({ size = 22, strokeWidth = 1.9, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <circle cx="11" cy="11" r="6.6" />
    <path d="m16.2 16.2 4 4" />
  </svg>
);

export const XIcon = ({ size = 20, strokeWidth = 2, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M6 6l12 12M18 6 6 18" />
  </svg>
);

export const PlusIcon = ({ size = 20, strokeWidth = 2.2, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M12 5v14M5 12h14" />
  </svg>
);

export const CheckIcon = ({ size = 16, strokeWidth = 2.6, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="m5 12.5 4.5 4.5L19 7" />
  </svg>
);

export const CalendarIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <rect x="3.6" y="5.2" width="16.8" height="15.2" rx="2.4" />
    <path d="M3.6 9.8h16.8M8.4 3.4v3.6M15.6 3.4v3.6" />
  </svg>
);

export const RefreshIcon = ({ size = 20, strokeWidth = 1.9, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M4.2 9.6a8 8 0 0 1 13.4-3.1L20 8.8" />
    <path d="M20 4v4.8h-4.8" />
    <path d="M19.8 14.4a8 8 0 0 1-13.4 3.1L4 15.2" />
    <path d="M4 20v-4.8h4.8" />
  </svg>
);

export const EditIcon = ({ size = 19, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M16.4 3.9a2.3 2.3 0 0 1 3.3 3.3L8.2 18.7 4 20l1.3-4.2Z" />
    <path d="m14.8 5.6 3.3 3.3" />
  </svg>
);

export const TrashIcon = ({ size = 19, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M4.5 6.6h15M9.6 6.6V4.8a1.4 1.4 0 0 1 1.4-1.4h2a1.4 1.4 0 0 1 1.4 1.4v1.8" />
    <path d="M6.4 6.6 7.3 19a1.8 1.8 0 0 0 1.8 1.7h5.8a1.8 1.8 0 0 0 1.8-1.7l.9-12.4" />
    <path d="M10.4 10.4v6M13.6 10.4v6" />
  </svg>
);

export const EyeIcon = ({ size = 19, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M2.4 12S5.9 5.6 12 5.6 21.6 12 21.6 12 18.1 18.4 12 18.4 2.4 12 2.4 12Z" />
    <circle cx="12" cy="12" r="3.1" />
  </svg>
);

export const EyeOffIcon = ({ size = 19, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M9.9 5.9A9.4 9.4 0 0 1 12 5.6c6.1 0 9.6 6.4 9.6 6.4a17 17 0 0 1-2.7 3.6" />
    <path d="M6.3 7.7A16.6 16.6 0 0 0 2.4 12s3.5 6.4 9.6 6.4a9 9 0 0 0 3.7-.8" />
    <path d="M9.9 9.9a3.1 3.1 0 0 0 4.2 4.2" />
    <path d="m3.6 3.6 16.8 16.8" />
  </svg>
);

export const DownloadIcon = ({ size = 19, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M12 3.8v10.6M7.8 10.6 12 14.8l4.2-4.2" />
    <path d="M4.4 16.4v2.2a1.8 1.8 0 0 0 1.8 1.8h11.6a1.8 1.8 0 0 0 1.8-1.8v-2.2" />
  </svg>
);

export const UploadIcon = ({ size = 20, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M12 15.4V4.8M7.8 9l4.2-4.2L16.2 9" />
    <path d="M4.4 16.4v2.2a1.8 1.8 0 0 0 1.8 1.8h11.6a1.8 1.8 0 0 0 1.8-1.8v-2.2" />
  </svg>
);

export const FileIcon = ({ size = 20, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M13.4 3.4H7.2a1.8 1.8 0 0 0-1.8 1.8v13.6a1.8 1.8 0 0 0 1.8 1.8h9.6a1.8 1.8 0 0 0 1.8-1.8V8.4Z" />
    <path d="M13.4 3.4v5h5.2" />
  </svg>
);

export const FilePlusIcon = ({ size = 20, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M13.4 3.4H7.2a1.8 1.8 0 0 0-1.8 1.8v13.6a1.8 1.8 0 0 0 1.8 1.8h9.6a1.8 1.8 0 0 0 1.8-1.8V8.4Z" />
    <path d="M13.4 3.4v5h5.2M12 11.6v5M9.5 14.1h5" />
  </svg>
);

export const FileCheckIcon = ({ size = 20, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M13.4 3.4H7.2a1.8 1.8 0 0 0-1.8 1.8v13.6a1.8 1.8 0 0 0 1.8 1.8h9.6a1.8 1.8 0 0 0 1.8-1.8V8.4Z" />
    <path d="M13.4 3.4v5h5.2m-9 6.4 1.9 1.9 3.6-3.6" />
  </svg>
);

export const FileXIcon = ({ size = 20, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M13.4 3.4H7.2a1.8 1.8 0 0 0-1.8 1.8v13.6a1.8 1.8 0 0 0 1.8 1.8h9.6a1.8 1.8 0 0 0 1.8-1.8V8.4Z" />
    <path d="M13.4 3.4v5h5.2m-8.8 4.4 4.4 4.4m0-4.4-4.4 4.4" />
  </svg>
);

export const FolderIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M3.4 6.6a1.8 1.8 0 0 1 1.8-1.8h3.7l2 2.6h7.9a1.8 1.8 0 0 1 1.8 1.8v8.2a1.8 1.8 0 0 1-1.8 1.8H5.2a1.8 1.8 0 0 1-1.8-1.8Z" />
  </svg>
);

export const LoaderIcon = ({ size = 22, strokeWidth = 1.9, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M12 3.2v3.4M12 17.4v3.4M3.2 12h3.4M17.4 12h3.4M5.8 5.8l2.4 2.4M15.8 15.8l2.4 2.4M18.2 5.8l-2.4 2.4M8.2 15.8l-2.4 2.4" />
  </svg>
);

export const LogOutIcon = ({ size = 18, strokeWidth = 1.9, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M9.4 20.4H5.8A1.8 1.8 0 0 1 4 18.6V5.4a1.8 1.8 0 0 1 1.8-1.8h3.6" />
    <path d="M15.4 16.4 19.8 12l-4.4-4.4M19.8 12H9.4" />
  </svg>
);

export const UserIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <circle cx="12" cy="8.2" r="3.9" />
    <path d="M4.6 20.4a7.4 7.4 0 0 1 14.8 0" />
  </svg>
);

export const UserCheckIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <circle cx="10" cy="8.2" r="3.9" />
    <path d="M3 20.4a7.2 7.2 0 0 1 12.2-5.2" />
    <path d="m15.8 17.6 2 2 3.6-3.8" />
  </svg>
);

export const UserXIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <circle cx="10" cy="8.2" r="3.9" />
    <path d="M3 20.4a7.2 7.2 0 0 1 11.6-5.7" />
    <path d="m16.4 15.8 4.6 4.6m0-4.6-4.6 4.6" />
  </svg>
);

export const ShieldCheckIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M12 2.8 4.8 5.6v6.1c0 4.4 3 8.4 7.2 9.5 4.2-1.1 7.2-5.1 7.2-9.5V5.6Z" />
    <path d="m9 11.8 2.2 2.2 4-4.2" />
  </svg>
);

export const DoorIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M5.4 20.6V4.6a1.4 1.4 0 0 1 1.4-1.4h10.4a1.4 1.4 0 0 1 1.4 1.4v16" />
    <path d="M3.4 20.6h17.2" />
    <circle cx="14.8" cy="12.2" r="1" fill="currentColor" stroke="none" />
  </svg>
);

export const DoorLateIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M6.4 20.6V4.6a1.4 1.4 0 0 1 1.4-1.4h8.4a1.4 1.4 0 0 1 1.4 1.4v16" />
    <path d="M4.4 20.6h15.2M9.6 9.4v3.4l2.2 1.4" />
  </svg>
);

export const BuildingIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M5.4 20.6V7.4L12 3.6l6.6 3.8v13.2" />
    <path d="M3.6 20.6h16.8M10 20.6v-4.4h4v4.4" />
  </svg>
);

export const BuildingCheckIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M5 20.6V5.2a1.6 1.6 0 0 1 1.6-1.6h6.6a1.6 1.6 0 0 1 1.6 1.6v5.6" />
    <path d="M3.4 20.6h9.2M8 7.4h2.4M8 11.2h2.4M8 15h2.4" />
    <circle cx="17.6" cy="16.6" r="4" />
    <path d="m15.9 16.6 1.2 1.2 2.2-2.4" />
  </svg>
);

export const BuildingXIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M5 20.6V5.2a1.6 1.6 0 0 1 1.6-1.6h6.6a1.6 1.6 0 0 1 1.6 1.6v5.6" />
    <path d="M3.4 20.6h9.2M8 7.4h2.4M8 11.2h2.4M8 15h2.4" />
    <circle cx="17.6" cy="16.6" r="4" />
    <path d="m16.1 15.1 3 3m0-3-3 3" />
  </svg>
);

export const BuildingOffIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M5 20.6V5.2a1.6 1.6 0 0 1 1.6-1.6h6.6a1.6 1.6 0 0 1 1.6 1.6v5.6" />
    <path d="M3.4 20.6h9.2M8 7.4h2.4M8 11.2h2.4" />
    <circle cx="17.6" cy="16.6" r="4" />
    <path d="m14.9 19.3 5.4-5.4" />
  </svg>
);

export const BoxIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M20.4 8.2 12 3.4 3.6 8.2v7.6L12 20.6l8.4-4.8Z" />
    <path d="m3.6 8.2 8.4 4.8 8.4-4.8M12 20.6V13" />
  </svg>
);

export const MonitorOffIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <rect x="2.5" y="4" width="19" height="12.5" rx="2" />
    <path d="M8.5 20.5h7M12 16.5v4M8.6 8.2l6.8 4.2M15.4 8.2l-6.8 4.2" />
  </svg>
);

export const WifiOffIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M2.6 8.6a15 15 0 0 1 4.6-2.7M21.4 8.6a15 15 0 0 0-8.9-3.2" />
    <path d="M5.9 12.5a10 10 0 0 1 2.6-1.7M18.1 12.5a10 10 0 0 0-3.6-2" />
    <path d="M9.2 16.2a5 5 0 0 1 5.6 0" />
    <path d="M12 20h.01M3 3l18 18" />
  </svg>
);

export const GridIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <rect x="3.6" y="3.6" width="6.6" height="6.6" rx="1.6" />
    <rect x="13.8" y="3.6" width="6.6" height="6.6" rx="1.6" />
    <rect x="3.6" y="13.8" width="6.6" height="6.6" rx="1.6" />
    <path d="M17.1 13.8v6.6M13.8 17.1h6.6" />
  </svg>
);

export const ListChecksIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M4.6 3.6h14.8a1.6 1.6 0 0 1 1.6 1.6v13.6a1.6 1.6 0 0 1-1.6 1.6H4.6A1.6 1.6 0 0 1 3 18.8V5.2a1.6 1.6 0 0 1 1.6-1.6Z" />
    <path d="M7.4 8.4h9.2M7.4 12h9.2m-9.2 3.6h4.6" />
  </svg>
);

export const CursorClickIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M9.4 9.4 20 13.2l-4.5 1.7-1.7 4.5Z" />
    <path d="M5.4 5.4 4 4M9 4.6V3M4.6 9H3M6.2 12.2 4.8 13.6" />
  </svg>
);

export const KeyIcon = ({ size = 20, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <circle cx="8.2" cy="15.8" r="4.2" />
    <path d="m11.2 12.8 8.6-8.6M17 7l2.2 2.2M14.6 9.4l2.2 2.2" />
  </svg>
);

export const AlertCircleIcon = ({ size = 20, strokeWidth = 1.9, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7.4v5.2M12 16.4h.01" />
  </svg>
);

export const CheckCircleIcon = ({ size = 20, strokeWidth = 1.9, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <circle cx="12" cy="12" r="9" />
    <path d="m8.2 12.2 2.6 2.6 5-5.2" />
  </svg>
);

export const InfoIcon = ({ size = 20, strokeWidth = 1.9, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 11.2v5M12 7.8h.01" />
  </svg>
);

export const SortIcon = ({ size = 15, strokeWidth = 2, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="m7.5 9.5 3-3.5 3 3.5M7.5 14.5l3 3.5 3-3.5" />
  </svg>
);

export const SaveIcon = ({ size = 19, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M5.2 3.6h10.2L20.4 8.6v9.8a1.8 1.8 0 0 1-1.8 1.8H5.2a1.8 1.8 0 0 1-1.8-1.8V5.4a1.8 1.8 0 0 1 1.8-1.8Z" />
    <path d="M7.6 3.6v5.2h7.6V3.6M7.6 20.4v-6h8.8v6" />
  </svg>
);

export const PowerIcon = ({ size = 19, strokeWidth = 1.9, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M12 3.6v8.2" />
    <path d="M17.4 6.4a7.6 7.6 0 1 1-10.8 0" />
  </svg>
);

/* ------------------------------------------------- Administración ------- */

export const CatalogIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M4.2 5.2a1.6 1.6 0 0 1 1.6-1.6h6.6" />
    <path d="M4.2 5.2v13.6a1.6 1.6 0 0 0 1.6 1.6h10.4a1.6 1.6 0 0 0 1.6-1.6v-5.2" />
    <path d="M7.6 9h5.2M7.6 12.6h4M7.6 16.2h3" />
    <path d="M17.4 3.4a1.9 1.9 0 0 1 2.7 2.7l-5.4 5.4-3.1.8.8-3.1Z" />
  </svg>
);

export const ParameterIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <rect x="3" y="4.4" width="18" height="11.6" rx="2" />
    <path d="M8.4 20.4h7.2M12 16v4.4" />
    <circle cx="12" cy="10.2" r="1.8" />
    <path d="M12 6.6v1.2M12 12.6v1.2M8.8 8.4l1 .6M14.2 11.4l1 .6M15.2 8.4l-1 .6M9.8 11.4l-1 .6" />
  </svg>
);

export const MoreIcon = ({ size = 20, strokeWidth = 2.2, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <circle cx="5.5" cy="12" r="1.1" fill="currentColor" />
    <circle cx="12" cy="12" r="1.1" fill="currentColor" />
    <circle cx="18.5" cy="12" r="1.1" fill="currentColor" />
  </svg>
);

export const TagIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M3.6 11.4V5.2a1.6 1.6 0 0 1 1.6-1.6h6.2l8.8 8.8a1.7 1.7 0 0 1 0 2.4l-5.6 5.6a1.7 1.7 0 0 1-2.4 0Z" />
    <circle cx="8.2" cy="8.2" r="1.4" />
  </svg>
);

export const SlidersIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M4 7.4h9.2M17.6 7.4H20M4 16.6h3.4M11.8 16.6H20" />
    <circle cx="15.4" cy="7.4" r="2.2" />
    <circle cx="9.6" cy="16.6" r="2.2" />
  </svg>
);

export const BriefcaseIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <rect x="3" y="7.4" width="18" height="12.4" rx="2" />
    <path d="M8.8 7.4V5.6a1.8 1.8 0 0 1 1.8-1.8h2.8a1.8 1.8 0 0 1 1.8 1.8v1.8" />
    <path d="M3 12.4h18" />
  </svg>
);

/* --------------------------------------------- Roles y permisos / perfil */

export const ShieldOffIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M12 2.8 4.8 5.6v6.1c0 4.4 3 8.4 7.2 9.5 4.2-1.1 7.2-5.1 7.2-9.5V5.6Z" />
    <path d="m8.6 15.4 6.8-6.8" />
  </svg>
);

export const UserShieldIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <circle cx="9.6" cy="8" r="3.6" />
    <path d="M3.2 20.4a6.6 6.6 0 0 1 10.2-5.5" />
    <path d="M18 12.2l3.4 1.3v2.9c0 2.1-1.4 4-3.4 4.6-2-.6-3.4-2.5-3.4-4.6v-2.9Z" />
  </svg>
);

export const CameraIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M3 8.6a2 2 0 0 1 2-2h2.2l1.4-2.2h6.8L16.8 6.6H19a2 2 0 0 1 2 2v8.8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z" />
    <circle cx="12" cy="13" r="3.4" />
  </svg>
);

export const MailIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <rect x="2.8" y="5" width="18.4" height="14" rx="2.2" />
    <path d="m3.6 7 8.4 6 8.4-6" />
  </svg>
);

export const PhoneIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <path d="M8.1 3.6 9.9 8l-2 1.6a11 11 0 0 0 5.9 5.9l1.6-2 4.4 1.8v3.1a2 2 0 0 1-2.2 2 17.6 17.6 0 0 1-15.9-15.9 2 2 0 0 1 2-2.2h3.1Z" />
  </svg>
);

export const CopyIcon = ({ size = 22, strokeWidth = 1.8, className }: P) => (
  <svg {...base(size, strokeWidth, className)}>
    <rect x="8.6" y="8.6" width="11.6" height="11.6" rx="2" />
    <path d="M15.4 5.6a2 2 0 0 0-2-1.8H5.8a2 2 0 0 0-2 2v7.6a2 2 0 0 0 1.8 2" />
  </svg>
);
