; Inno-Setup-Skript für Sayvant. Aufruf: ISCC.exe /DAppVersion=0.2.0 packaging\sayvant.iss
; Installiert ohne Administratorrechte nach %LOCALAPPDATA%\Programs\Sayvant.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6E1C3B0A-7A5F-4C1D-9D63-5A2F0B8E4C71}
AppName=Sayvant
AppVersion={#AppVersion}
AppVerName=Sayvant {#AppVersion}
AppPublisher=Githubtezla
AppPublisherURL=https://github.com/Githubtezla/Sayvant
AppSupportURL=https://github.com/Githubtezla/Sayvant/issues
DefaultDirName={localappdata}\Programs\Sayvant
DisableProgramGroupPage=yes
DisableDirPage=auto
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=Sayvant-Setup-{#AppVersion}
SetupIconFile=..\build\sayvant.ico
UninstallDisplayIcon={app}\Sayvant.exe
UninstallDisplayName=Sayvant
LicenseFile=..\LICENSE
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
AppMutex=Local\SayvantDiktat
CloseApplications=yes
VersionInfoVersion={#AppVersion}
VersionInfoProductName=Sayvant

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[CustomMessages]
english.Autostart=Start Sayvant with Windows
german.Autostart=Sayvant mit Windows starten

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\Sayvant\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Sayvant"; Filename: "{app}\Sayvant.exe"
Name: "{autodesktop}\Sayvant"; Filename: "{app}\Sayvant.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Sayvant.exe"; Description: "{cm:LaunchProgram,Sayvant}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/C taskkill /IM Sayvant.exe /F"; Flags: runhidden; RunOnceId: "StopSayvant"

[UninstallDelete]
; Autostart-Verknüpfung, die Sayvant selbst anlegt. Einstellungen und Verlauf in %APPDATA%\Sayvant bleiben erhalten.
Type: files; Name: "{userstartup}\Sayvant.lnk"
