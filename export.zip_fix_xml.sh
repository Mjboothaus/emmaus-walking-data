unzip export.zip
cd apple_health_export
patch < ~/code/github/mjboothaus/emmaus-walking-data/data/patch.txt
sed 's/startDate/endDate/2' export.xml > export-fixed.xml
pipx install healthkit-to-sqlite
healthkit-to-sqlite export-fixed.xml healthkit.db --xml