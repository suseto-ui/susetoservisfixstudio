[Setup]
AppName=SusetoDroidFixStudio & EUDCP Enterprise Suite
AppVersion=1.0.0
AppPublisher=Suseto Droid Labs
DefaultDirName=C:\SusetoFix
DefaultGroupName=SusetoFix
OutputDir=Output
OutputBaseFilename=SusetoFix_Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\SusetoDroidFixStudio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist_web\*"; DestDir: "{app}\dist_web"; Flags: ignoreversion recursesubdirs createallsubdirs; Flags: skipifsourcedoesntexist
Source: "drivers\*"; DestDir: "{app}\drivers"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "db\*"; DestDir: "{app}\db"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "bin\*"; DestDir: "{app}\bin"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\SusetoDroidFixStudio"; Filename: "{app}\SusetoDroidFixStudio.exe"
Name: "{group}\Suseto Kiosk (1-Tlačítková Obnova)"; Filename: "{app}\SusetoDroidFixStudio.exe"; Parameters: "--kiosk"
Name: "{group}\Ovladače - Instalace WinUSB"; Filename: "{app}\drivers\winusb_setup.cmd"
Name: "{autodesktop}\SusetoDroidFixStudio"; Filename: "{app}\SusetoDroidFixStudio.exe"; Tasks: desktopicon
Name: "{autodesktop}\Suseto Kiosk Servis"; Filename: "{app}\SusetoDroidFixStudio.exe"; Parameters: "--kiosk"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
Filename: "{app}\drivers\winusb_setup.cmd"; Description: "Instalace a registrace ovladačů (FTDI, CP210x, WinUSB)"; Flags: postinstall shellexec waituntilterminated
Filename: "{app}\SusetoDroidFixStudio.exe"; Description: "Spustit SusetoDroidFixStudio"; Flags: postinstall nowait skipifsilent
