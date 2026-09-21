[Setup]
AppId={{E3F7A1B2-5C4D-4E6F-8A9B-0C1D2E3F4A5B}
AppName=Familia Puess
AppVersion=1.1.0
AppPublisher=Familia Puess
DefaultDirName={autopf}\FamiliaPuess
DefaultGroupName=Familia Puess
UninstallDisplayIcon={app}\FamiliaPuess.exe
OutputDir=installer_output
OutputBaseFilename=FamiliaPuess_Setup_1.1.0
SetupIconFile=apps\Desktop\assets\images\app.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "dist\FamiliaPuess.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Familia Puess"; Filename: "{app}\FamiliaPuess.exe"
Name: "{autodesktop}\Familia Puess"; Filename: "{app}\FamiliaPuess.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"

[Run]
Filename: "{app}\FamiliaPuess.exe"; Description: "Iniciar Familia Puess"; Flags: nowait postinstall skipifsilent
