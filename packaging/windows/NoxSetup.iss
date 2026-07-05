#define MyAppName "Nox"
#define MyAppVersion "0.1.2"
#define MyAppPublisher "Nox Agent OS"
#define MyAppExeName "nox.exe"

[Setup]
AppId={{8B8F24E5-F0F5-4930-B22A-81D84D3E31E3}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Nox
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\..\dist\installer
OutputBaseFilename=NoxSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesEnvironment=yes
PrivilegesRequired=lowest

[Tasks]
Name: "addtopath"; Description: "Add Nox to the user PATH"; GroupDescription: "Command line integration:"; Flags: checkedonce

[Files]
Source: "..\..\dist\nox\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Nox"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "doctor"; Description: "Run nox doctor"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: NeedsAddPath(ExpandConstant('{app}')) and WizardIsTaskSelected('addtopath')

[Code]
function NeedsAddPath(PathToAdd: string): Boolean;
var
  CurrentPath: string;
  NormalizedCurrent: string;
  NormalizedAdd: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', CurrentPath) then
  begin
    Result := True;
    exit;
  end;

  NormalizedCurrent := ';' + Uppercase(CurrentPath) + ';';
  NormalizedAdd := ';' + Uppercase(PathToAdd) + ';';
  Result := Pos(NormalizedAdd, NormalizedCurrent) = 0;
end;
