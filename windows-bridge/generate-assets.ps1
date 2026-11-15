$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing
$dir = Join-Path $PSScriptRoot "Assets"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
function New-JarvisPng([string]$name,[int]$w,[int]$h) {
    $bmp = New-Object System.Drawing.Bitmap($w,$h)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.Clear([System.Drawing.Color]::FromArgb(7,18,27))
    $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(69,223,255),[single][Math]::Max(2,[int]($w/90)))
    $font = New-Object System.Drawing.Font("Segoe UI",[single][Math]::Max(9,$w/10),[System.Drawing.FontStyle]::Bold)
    $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(69,223,255))
    $g.DrawEllipse($pen,[single]($w*.18),[single]($h*.12),[single]($w*.64),[single]($h*.76))
    $sf = New-Object System.Drawing.StringFormat
    $sf.Alignment = [System.Drawing.StringAlignment]::Center
    $sf.LineAlignment = [System.Drawing.StringAlignment]::Center
    $rect = New-Object System.Drawing.RectangleF(0,0,$w,$h)
    $g.DrawString("BJ",$font,$brush,$rect,$sf)
    $bmp.Save((Join-Path $dir $name),[System.Drawing.Imaging.ImageFormat]::Png)
    $sf.Dispose(); $rect = $null; $brush.Dispose(); $font.Dispose(); $pen.Dispose(); $g.Dispose(); $bmp.Dispose()
}
New-JarvisPng "StoreLogo.png" 50 50
New-JarvisPng "Square150x150Logo.png" 150 150
New-JarvisPng "Square44x44Logo.png" 44 44
New-JarvisPng "Wide310x150Logo.png" 310 150
New-JarvisPng "SplashScreen.png" 620 300
Write-Host "BALA JARVIS package assets generated." -ForegroundColor Cyan
