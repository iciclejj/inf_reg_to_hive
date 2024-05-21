param (
    $hive_filepath
)

reg load "HKU\INF_REG_TO_HIVE" "$hive_filepath"

#Start-Sleep -Seconds 1