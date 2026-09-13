; woldvein Trainer v0.3 Installer Script for Inno Setup 6
; 生成 woldvein_trainer_v0.3_setup.exe 安装包
;
; 特性：
;   - 中英双语（安装时选择语言）
;   - 自由选择安装路径
;   - 自动创建文件夹
;   - 桌面 + 开始菜单快捷方式
;   - 卸载引导（可选保留用户配置）
;   - 现代 UI（WizardStyle=modern）
;   - 控制面板卸载入口

#define MyAppName "woldvein Trainer"
#define MyAppNameZh "平野孤鸿全能修改器"
#define MyAppVersion "0.3"
#define MyAppPublisher "woldvein"
#define MyAppURL "https://github.com/180lisilence/woldvein0.3"
#define MyAppExeName "woldvein_trainer_v0.3.exe"
#define MyAppIcon "app.ico"

[Setup]
; 基本 ID（每个版本唯一，升级时不会被识别为不同软件）
AppId={{B5F7A2C1-3D9E-4F8B-9A6C-1E2D3F4A5B6C}
AppName={#MyAppName}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppVersion={#MyAppVersion}
VersionInfoVersion=0.3.0.0
VersionInfoCompany=woldvein
VersionInfoDescription=woldvein Trainer Installer
VersionInfoProductName=woldvein Trainer
VersionInfoProductVersion=0.3.0.0

; 安装目录（默认 Program Files\woldvein_trainer）
DefaultDirName={autopf}\woldvein_trainer
DisableDirPage=no
DefaultGroupName=woldvein Trainer

; 输出配置
OutputDir=..\
OutputBaseFilename=woldvein_trainer_v0.3_setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; 图标和外观
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\{#MyAppIcon}
UninstallDisplayName=woldvein Trainer v0.3

; 权限（需要管理员才能写入 Program Files）
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible

; 语言选择界面（首次安装时弹出）
ShowLanguageDialog=yes

; 卸载时关闭运行中的程序
CloseApplications=force
RestartApplications=yes

[Languages]
; 中英双语（用户在安装时选择）
Name: "zh"; MessagesFile: "ChineseSimplified.isl"; LicenseFile: "license_zh.txt"
Name: "en"; MessagesFile: "compiler:Default.isl"; LicenseFile: "license_en.txt"

[CustomMessages]
; 中文自定义消息（zh 语言）
zh.CreateDesktopIcon=创建桌面快捷方式
zh.CreateStartMenu=创建开始菜单快捷方式
zh.CreateQuickLaunch=创建快速启动栏图标
zh.LaunchProgram=启动 woldvein Trainer
zh.ManualFile=用户手册
zh.UninstallItem=卸载 woldvein Trainer

; 英文自定义消息
en.CreateDesktopIcon=Create desktop shortcut
en.CreateStartMenu=Create Start Menu shortcuts
en.CreateQuickLaunch=Create a Quick Launch icon
en.LaunchProgram=Launch woldvein Trainer
en.ManualFile=User Manual
en.UninstallItem=Uninstall woldvein Trainer

[Tasks]
; 快捷方式选项（用户可勾选）- Description 使用 {cm:xxx} 引用 CustomMessages，自动适配当前语言
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "startmenu"; Description: "{cm:CreateStartMenu}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunch}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; Check: not IsAdminInstallMode

[Files]
; 主程序和 DLL（必装）
Source: "..\dist\woldvein_trainer_v0.3\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\dist\woldvein_trainer.dll"; DestDir: "{app}"; Flags: ignoreversion
; 默认配置（只在首次安装时写入，升级时保留用户的 config.json）
; Source: "..\dist\config.json"; DestDir: "{app}"; Flags: onlyifdoesntexist
; 文档
Source: "..\docs\PRD_v0.1.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\docs\用户手册.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
; 图标
Source: "app.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 开始菜单快捷方式（中文/英文通过 Comment 自动适配）
Name: "{group}\woldvein Trainer"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app.ico"; Comment: "Launch woldvein Trainer"
Name: "{group}\{cm:ManualFile}"; Filename: "notepad.exe"; Parameters: """{app}\docs\用户手册.md"""; Comment: "Open user manual"
Name: "{group}\README"; Filename: "notepad.exe"; Parameters: """{app}\README.md"""; Comment: "Open README"
Name: "{group}\{cm:UninstallItem}"; Filename: "{uninstallexe}"; Comment: "Uninstall woldvein Trainer"

; 桌面快捷方式（用户勾选时创建）
Name: "{commondesktop}\woldvein Trainer"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app.ico"; Tasks: desktopicon; Comment: "Launch woldvein Trainer"

; 快速启动栏（用户勾选时创建）
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch User Pinned\woldvein Trainer"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; IconFilename: "{app}\app.ico"

[Run]
; 安装完成后可选启动程序
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; 卸载时删除 %LOCALAPPDATA% 下的配置和日志（通过批处理）
; 注：在 [UninstallDelete] 中清理更安全

[UninstallDelete]
; 卸载时清理用户数据（Type: filesandordirs 会删除整个目录）
; 保留 config.json 和 logs 是更友好的做法，这里提供清理选项
Type: filesandordirs; Name: "{localappdata}\woldvein_trainer\logs"
Type: filesandordirs; Name: "{localappdata}\woldvein_trainer\lua_cmd.txt"
Type: filesandordirs; Name: "{localappdata}\woldvein_trainer\lua_result.txt"

[Code]
// 卸载时询问是否保留用户配置
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
        // DelTree(Path, IsDir, DeleteFiles, DeleteSubdirsAlso) - 递归删除目录及所有子目录
        DelTree(UserDataDir, True, True, True);
      end;
    end;
  end;
end;

// 安装前检查：如果是升级安装，先关闭运行中的旧版本
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  // 尝试关闭运行中的修改器（避免文件被占用无法覆盖）
  if Exec(ExpandConstant('{cmd}'), '/C taskkill /F /IM woldvein_trainer_v0.3.exe >nul 2>nul', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    // 已尝试关闭，继续安装
  end;
  Result := True;
end;

// 卸载前关闭运行中的程序
function InitializeUninstall(): Boolean;
var
  ResultCode: Integer;
begin
  if Exec(ExpandConstant('{cmd}'), '/C taskkill /F /IM woldvein_trainer_v0.3.exe >nul 2>nul', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    // 已尝试关闭
  end;
  Result := True;
end;
