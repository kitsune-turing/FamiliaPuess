; Inno Setup script for Familia Puess Desktop
; Requires Inno Setup 6+ (https://jrsoftware.org/isinfo.php)

#define MyAppName "Familia Puess"
#define MyAppVersion "1.2.0"
#define MyAppPublisher "Familia Puess"
#define MyAppExeName "FamiliaPuess.exe"

[Setup]
AppId={{E8F3A1B2-4C5D-6E7F-8A9B-0C1D2E3F4A5B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\..\dist\installer
OutputBaseFilename=FamiliaPuess_Setup_{#MyAppVersion}
SetupIconFile=assets\app.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked
Name: "startupicon"; Description: "Iniciar con Windows"; GroupDescription: "Opciones adicionales:"; Flags: unchecked

[Files]
Source: "..\..\dist\FamiliaPuess\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[INI]
Filename: "{%USERPROFILE}\.familia_puess\config.ini"; Section: "auth"; Key: "api_key"; String: "{code:GetApiKey}"; Flags: createkeyifdoesntexist

[Code]
var
  ApiKeyPage: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  ApiKeyPage := CreateInputQueryPage(wpSelectTasks,
    'Configuración de API Key',
    'Conectar con el servidor',
    'Ingrese la API Key para conectar con el servidor (puede configurarlo después desde la aplicación):');
  ApiKeyPage.Add('API Key:', False);
end;

function GetApiKey(Param: string): string;
begin
  Result := ApiKeyPage.Values[0];
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
end;
