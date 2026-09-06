param(
    [string]$OutputDir = "D:\project\skill\screenshots"
)

Add-Type -AssemblyName System.Drawing

# Declare DPI awareness so coordinates are physical pixels, not scaled ones.
Add-Type -Language CSharp -ReferencedAssemblies "System.Drawing" @"
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Runtime.InteropServices;

public struct RECT { public int left, top, right, bottom; }

public class ScreenCaptureHelper
{
    [DllImport("user32.dll")]
    private static extern bool EnumDisplayMonitors(IntPtr hdc, IntPtr lprcClip, MonitorEnumProc lpfnEnum, IntPtr dwData);
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    private static extern bool GetMonitorInfo(IntPtr hMonitor, ref MONITORINFO lpmi);
    [DllImport("user32.dll")]
    private static extern bool SetProcessDPIAware();

    private delegate bool MonitorEnumProc(IntPtr hMonitor, IntPtr hdc, IntPtr lprcClip, IntPtr dwData);

    [StructLayout(LayoutKind.Sequential)]
    private struct MONITORINFO
    {
        public int cbSize;
        public RECT rcMonitor;
        public RECT rcWork;
        public uint dwFlags;
    }

    private static List<RECT> _monitors = new List<RECT>();

    private static bool MonitorCallback(IntPtr hMonitor, IntPtr hdc, IntPtr lprcClip, IntPtr dwData)
    {
        MONITORINFO mi = new MONITORINFO();
        mi.cbSize = Marshal.SizeOf(typeof(MONITORINFO));
        GetMonitorInfo(hMonitor, ref mi);
        _monitors.Add(mi.rcMonitor);
        return true;
    }

    // Returns the union bounding box of all monitors (physical pixels), plus per-monitor info.
    public static string CaptureAll(string outDir, out string infoLines)
    {
        SetProcessDPIAware();
        _monitors.Clear();
        EnumDisplayMonitors(IntPtr.Zero, IntPtr.Zero, MonitorCallback, IntPtr.Zero);

        if (_monitors.Count == 0)
        {
            infoLines = "ERROR: no monitors found";
            return null;
        }

        int minX = int.MaxValue, minY = int.MaxValue, maxX = int.MinValue, maxY = int.MinValue;
        var lines = new List<string>();
        for (int i = 0; i < _monitors.Count; i++)
        {
            RECT r = _monitors[i];
            if (r.left < minX) minX = r.left;
            if (r.top < minY) minY = r.top;
            if (r.right > maxX) maxX = r.right;
            if (r.bottom > maxY) maxY = r.bottom;
            lines.Add(string.Format("monitor[{0}] = ({1},{2})-({3},{4})  [{5}x{6}]",
                i, r.left, r.top, r.right, r.bottom, r.right - r.left, r.bottom - r.top));
        }
        infoLines = string.Join(" | ", lines);

        int w = maxX - minX;
        int h = maxY - minY;
        var bitmap = new System.Drawing.Bitmap(w, h);
        using (var g = System.Drawing.Graphics.FromImage(bitmap))
        {
            g.CopyFromScreen(minX, minY, 0, 0, bitmap.Size);
        }

        string stamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
        System.IO.Directory.CreateDirectory(outDir);
        string path = System.IO.Path.Combine(outDir, "desktop_" + stamp + ".png");
        bitmap.Save(path, System.Drawing.Imaging.ImageFormat.Png);
        bitmap.Dispose();
        return path;
    }
}
"@

$info = ""
$result = [ScreenCaptureHelper]::CaptureAll($OutputDir, [ref]$info)
Write-Output ("Screens: " + $info)
Write-Output ("Captured: " + $result)
