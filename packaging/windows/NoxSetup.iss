#define MyAppName "Nox"
#ifndef MyAppVersion
#define MyAppVersion "0.5.0"
#endif
#define MyAppPublisher "Nox Agent OS"
#define MyAppExeName "nox.exe"

[Setup]
AppId={{8B8F24E5-F0F5-4930-B22A-81D84D3E31E3}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
VersionInfoVersion={#MyAppVersion}
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
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{code:GetUserPathWithAppFirst}"; Check: WizardIsTaskSelected('addtopath')

[Code]
function GetUserPathWithAppFirst(Param: string): string;
var
  CurrentPath: string;
  AppPath: string;
  Segment: string;
  Remainder: string;
  SeparatorIndex: Integer;
begin
  AppPath := ExpandConstant('{app}');
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', CurrentPath) then
  begin
    Result := AppPath;
    exit;
  end;

  Result := AppPath;
  Remainder := CurrentPath;

  while Remainder <> '' do
  begin
    SeparatorIndex := Pos(';', Remainder);
    if SeparatorIndex > 0 then
    begin
      Segment := Trim(Copy(Remainder, 1, SeparatorIndex - 1));
      Delete(Remainder, 1, SeparatorIndex);
    end
      else
    begin
      Segment := Trim(Remainder);
      Remainder := '';
    end;

    if (Segment <> '') and (Uppercase(Segment) <> Uppercase(AppPath)) then
    begin
      Result := Result + ';' + Segment;
    end;
  end;
end;
