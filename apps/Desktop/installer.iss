; Inno Setup script for Familia Puess Desktop
; Requires Inno Setup 6+ (https://jrsoftware.org/isinfo.php)

#define MyAppName "Familia Puess"
#define MyAppVersion "1.0.0"
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

[Files]
Source: "..\..\dist\FamiliaPuess\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ApiKey: string;
  ConfigDir: string;
  ConfigFile: string;
begin
  if CurStep = ssPostInstall then
  begin
    if InputQuery('{#MyAppName}', 'Ingrese la API Key para conectar con el servidor (puede configurarlo despues):', ApiKey) then
    begin
      if ApiKey <> '' then
      begin
        ConfigDir := ExpandConstant('{%USERPROFILE}') + '\.familia_puess';
        ForceDirectories(ConfigDir);
        ConfigFile := ConfigDir + '\config.ini';
        SaveStringToFile(ConfigFile, '[auth]' + #13#10 + 'api_key = ' + ApiKey + #13#10, False);
      end;
    end;
  end;
end;
