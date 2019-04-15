#!/usr/bin/env sh
DIR="."
INNO="innoextract-1.7"
if command -v 7z >/dev/null; then
    ZIP="7z a -tzip -mx=9 -bso0 -bsp0";
elif command -v zip >/dev/null; then
    ZIP="zip -9q";
else
    echo "Please install either 7-Zip or Info-ZIP.";
    exit;
fi
DM="curl -sL"

cd ${DIR}
$DM -o 'pMetroSetup.exe' 'http://pmetro.su/download/pMetroSetup.exe'
INNOBIN="$INNO*/innoextract"
if [ "$(uname)" = "Linux" ] && [ ! -f ${DIR}/${INNOBIN} ]; then
    $DM "http://constexpr.org/innoextract/files/$INNO-linux.tar.xz" | tar -xJ
elif [ "$(expr substr $(uname) 1 5)" = "MINGW" ] && [ ! -f ${DIR}/${INNOBIN}.exe ]; then
    $DM -o "$INNO-windows.zip" "http://constexpr.org/innoextract/files/$INNO-windows.zip" 
    unzip -q "$INNO-windows.zip" -d $INNO && rm "$INNO-windows.zip"
fi
${DIR}/${INNOBIN} -se pMetroSetup.exe
for i in app/*.pmz; do
    $ZIP ./download/$(basename "$i" .pmz).zip $i;
done
rm -rf pMetroSetup.exe app/
d1=$(date -d "now" +%s)
d2=$(date -d "30 Dec 1899" +%s)
sed -i "s/Date=\".*\"/Date=\"$(( (d1 - d2) / 86400 ))\"/g" Files.xml

git add .
git commit -m $(date -d now +%F)
git push
