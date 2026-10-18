; Builds the Windows installer (Notes-Setup-<version>.exe) from the PyInstaller output in dist\Notes
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

[Setup]
AppId={{B7A3A1E2-5C47-4F0B-9F7B-0A1D6A9C3E21}
AppName=Notes
AppVersion={#AppVersion}
DefaultDirName={autopf}\Notes
DefaultGroupName=Notes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=output
OutputBaseFilename=Notes-Setup-{#AppVersion}
SetupIconFile=notes.ico
UninstallDisplayIcon={app}\Notes.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Shortcuts:"

[Files]
Source: "dist\Notes\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autoprograms}\Notes"; Filename: "{app}\Notes.exe"
Name: "{autoprograms}\Notes (browser)"; Filename: "{app}\Notes.exe"; Parameters: "--browser"
Name: "{autodesktop}\Notes"; Filename: "{app}\Notes.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Notes.exe"; Description: "Open Notes"; Flags: nowait postinstall skipifsilent
