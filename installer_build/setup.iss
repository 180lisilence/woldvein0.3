; woldvein Trainer Installer Script for Inno Setup 6
; 生成 woldvein_trainer_v<版本>_setup.exe 安装包
; 版本号默认取下方 MyAppVersion；构建脚本可用 /DMyAppVersion=<版本> 覆盖（单一版本源 src/constants.py）

#define MyAppName "woldvein Trainer"
#define MyAppNameZh "平野孤鸿全能修改器"
#ifndef MyAppVersion
#define MyAppVersion "0.4.3"
#endif
#define MyAppPublisher "woldvein"
#define MyAppURL "https://github.com/180lisilence/woldvein0.3-0.4"
#define MyAppExeName "woldvein_trainer.exe"
#define MyAppIcon "app.ico"

[Setup]
AppId={{B5F7A2C1-3D9E-4F8B-9A6C-1E2D3F4A5B6C}
AppName={#MyAppName}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppVersion={#MyAppVersion}
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany=woldvein
VersionInfoDescription=woldvein Trainer Installer
VersionInfoProductName=woldvein Trainer
VersionInfoProductVersion={#MyAppVersion}.0

DefaultDirName={autopf}\woldvein_trainer
DisableDirPage=no
DefaultGroupName=woldvein Trainer

OutputDir=..\
OutputBaseFilename=woldvein_trainer_v{#MyAppVersion}_setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\{#MyAppIcon}
UninstallDisplayName={#MyAppName} {#MyAppVersion}

PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible

ShowLanguageDialog=yes

CloseApplications=force
RestartApplications=yes

[Languages]
Name: "zh"; MessagesFile: "ChineseSimplified.isl"; LicenseFile: "license_zh.txt"
Name: "en"; MessagesFile: "compiler:Default.isl"; LicenseFile: "license_en.txt"

[CustomMessages]
zh.CreateDesktopIcon=创建桌面快捷方式
zh.CreateStartMenu=创建开始菜单快捷方式
zh.CreateQuickLaunch=创建快速启动栏图标
zh.LaunchProgram=启动 woldvein Trainer
zh.ManualFile=用户手册
zh.UninstallItem=卸载 woldvein Trainer

en.CreateDesktopIcon=Create desktop shortcut
en.CreateStartMenu=Create Start Menu shortcuts
en.CreateQuickLaunch=Create a Quick Launch icon
en.LaunchProgram=Launch woldvein Trainer
en.ManualFile=User Manual
en.UninstallItem=Uninstall woldvein Trainer

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "startmenu"; Description: "{cm:CreateStartMenu}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunch}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; Check: not IsAdminInstallMode

[Files]
Source: "..\dist_final\woldvein_trainer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\woldvein_trainer.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "app.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\woldvein Trainer"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app.ico"; Comment: "Launch woldvein Trainer"
Name: "{group}\README"; Filename: "notepad.exe"; Parameters: """{app}\README.md"""; Comment: "Open README"
Name: "{group}\CHANGELOG"; Filename: "notepad.exe"; Parameters: """{app}\CHANGELOG.md"""; Comment: "Open changelog"
Name: "{group}\{cm:UninstallItem}"; Filename: "{uninstallexe}"; Comment: "Uninstall woldvein Trainer"

Name: "{commondesktop}\woldvein Trainer"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app.ico"; Tasks: desktopicon; Comment: "Launch woldvein Trainer"

Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch User Pinned\woldvein Trainer"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; IconFilename: "{app}\app.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\woldvein_trainer\logs"
Type: filesandordirs; Name: "{localappdata}\woldvein_trainer\lua_cmd.txt"
Type: filesandordirs; Name: "{localappdata}\woldvein_trainer\lua_result.txt"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  MsgResult: Integer;
  UserDataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    UserDataDir := ExpandConstant('{localappdata}\woldvein_trainer');
    if DirExists(UserDataDir) then
    begin
      if ActiveLanguage = 'zh' then
        MsgResult := MsgBox('是否删除用户配置和日志？'#13#10#13#10'路径：' + UserDataDir + #13#10#13#10'选择「是」将完全清除所有痕迹，'#13#10'选择「否」保留配置以便下次重装时恢复。', mbConfirmation, MB_YESNO or MB_DEFBUTTON2)
      else
        MsgResult := MsgBox('Delete user configuration and logs?'#13#10#13#10'Path: ' + UserDataDir + #13#10#13#10'Click "Yes" to completely remove all traces,'#13#10'Click "No" to keep configuration for reinstallation.', mbConfirmation, MB_YESNO or MB_DEFBUTTON2);

      if MsgResult = IDYES then
      begin
        DelTree(UserDataDir, True, True, True);
      end;
    end;
  end;
end;

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  if Exec(ExpandConstant('{cmd}'), '/C taskkill /F /IM woldvein_trainer.exe >nul 2>nul', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
  end;
  Result := True;
end;

function InitializeUninstall(): Boolean;
var
  ResultCode: Integer;
begin
  if Exec(ExpandConstant('{cmd}'), '/C taskkill /F /IM woldvein_trainer.exe >nul 2>nul', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
  end;
  Result := True;
end;
