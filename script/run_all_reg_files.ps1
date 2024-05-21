param(
    $reg_dir_path
)

Get-ChildItem -Path $reg_dir_path -Filter "*.reg" | ForEach-Object {
    $regFilePath = $_.FullName

    try {
        Write-Host "Importing: $regFilePath"
        reg import $regFilePath
        Write-Host "Import successful!"
    }
    catch {
        Write-Error "Error importing $($regFilePath): $($_.Exception.Message)"
    }

    Write-Host ""  # Add an empty line for better readability
}

#Start-Sleep -Seconds 1