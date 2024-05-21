# Credit: https://hinchley.net/articles/create-a-new-registry-hive-using-powershell
param  (
  [string]$export_path = "C:/INF_REG_TO_HIVE.DAT"
)

Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
using Microsoft.Win32;

namespace Privileges {
  public class TokenPrivileges {
    [DllImport("advapi32.dll", CharSet = CharSet.Auto)]
    public static extern int OpenProcessToken(int ProcessHandle, int DesiredAccess, ref int tokenhandle);

    [DllImport("kernel32.dll", CharSet = CharSet.Auto)]
    public static extern int GetCurrentProcess();

    [DllImport("advapi32.dll", CharSet = CharSet.Auto)]
    public static extern int LookupPrivilegeValue(string lpsystemname, string lpname, [MarshalAs(UnmanagedType.Struct)] ref LUID lpLuid);

    [DllImport("advapi32.dll", CharSet = CharSet.Auto)]
    public static extern int AdjustTokenPrivileges(int tokenhandle, int disableprivs, [MarshalAs(UnmanagedType.Struct)] ref TOKEN_PRIVILEGE Newstate, int bufferlength, int PreivousState, int Returnlength);

    public const int TOKEN_ASSIGN_PRIMARY = 0x00000001;
    public const int TOKEN_DUPLICATE = 0x00000002;
    public const int TOKEN_IMPERSONATE = 0x00000004;
    public const int TOKEN_QUERY = 0x00000008;
    public const int TOKEN_QUERY_SOURCE = 0x00000010;
    public const int TOKEN_ADJUST_PRIVILEGES = 0x00000020;
    public const int TOKEN_ADJUST_GROUPS = 0x00000040;
    public const int TOKEN_ADJUST_DEFAULT = 0x00000080;

    public const UInt32 SE_PRIVILEGE_ENABLED_BY_DEFAULT = 0x00000001;
    public const UInt32 SE_PRIVILEGE_ENABLED = 0x00000002;
    public const UInt32 SE_PRIVILEGE_REMOVED = 0x00000004;
    public const UInt32 SE_PRIVILEGE_USED_FOR_ACCESS = 0x80000000;

    public static void EnablePrivilege(string privilege) {
      var token = 0;

      var TP = new TOKEN_PRIVILEGE();
      var LD = new LUID();

      OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ref token);
      LookupPrivilegeValue(null, privilege, ref LD);
      TP.PrivilegeCount = 1;

      var luidAndAtt = new LUID_AND_ATTRIBUTES {Attributes = SE_PRIVILEGE_ENABLED, Luid = LD};
      TP.Privilege = luidAndAtt;

      AdjustTokenPrivileges(token, 0, ref TP, 1024, 0, 0);
    }

    public static void DisablePrivilege(string privilege) {
      var token = 0;

      var TP = new TOKEN_PRIVILEGE();
      var LD = new LUID();

      OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ref token);
      LookupPrivilegeValue(null, privilege, ref LD);
      TP.PrivilegeCount = 1;

      var luidAndAtt = new LUID_AND_ATTRIBUTES {Luid = LD};
      TP.Privilege = luidAndAtt;

      AdjustTokenPrivileges(token, 0, ref TP, 1024, 0, 0);
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct LUID {
      internal uint LowPart;
      internal uint HighPart;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct LUID_AND_ATTRIBUTES {
      internal LUID Luid;
      internal uint Attributes;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct TOKEN_PRIVILEGE {
      internal uint PrivilegeCount;
      internal LUID_AND_ATTRIBUTES Privilege;
    }
  }
}
'@

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using Microsoft.Win32;

namespace Registry {
  public class Utils {
    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern int RegCloseKey(UIntPtr hKey);

    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern int RegOpenKeyEx(UIntPtr hKey, string subKey, int ulOptions, int samDesired, out UIntPtr hkResult);

    [DllImport("advapi32.dll", SetLastError=true, CharSet = CharSet.Unicode)]
    private static extern uint RegSaveKey(UIntPtr hKey, string lpFile, IntPtr lpSecurityAttributes);

    private static int KEY_READ = 131097;
    private static UIntPtr HKEY_LOCAL_MACHINE = new UIntPtr(0x80000002u);

    public static uint SaveKey(string key, string path) {
      UIntPtr hKey = UIntPtr.Zero;
      RegOpenKeyEx(HKEY_LOCAL_MACHINE, key, 0, KEY_READ, out hKey);
      uint result = RegSaveKey(hKey, path, IntPtr.Zero);
      RegCloseKey(hKey);
      return result;
    }
  }
}
'@

write-output "enable the privileges"
# Enable the privileges required to save the hive.
[Privileges.TokenPrivileges]::EnablePrivilege('SeBackupPrivilege') | Out-Null

write-output "build the hive"
# Build the hive.
new-item -path HKLM:\Software -name Hive | Out-Null
new-itemproperty -path HKLM:\Software\Hive -name Foo -value Bar -type string | Out-Null

write-output "export the hive"
# Export the hive.
[Registry.Utils]::SaveKey("SOFTWARE\\HIVE",  $export_path)

write-output "clean up"
# Clean up.
remove-item -path HKLM:\Software\Hive -force

write-output "disable the privileges"
# Disable the privileges required to save the hive.
[Privileges.TokenPrivileges]::DisablePrivilege('SeBackupPrivilege') | Out-Null

#Start-Sleep -Seconds 1