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
URL="http://pmetro.chpeks.com/download/pMetroSetup.exe"

cd ${DIR}
$DM -o 'pMetroSetup.exe' $URL
INNOBIN="$INNO*/innoextract"
if [ "$(uname)" = "Linux" ] && [ ! -f ${DIR}/${INNOBIN} ]; then
    $DM "http://constexpr.org/innoextract/files/$INNO-linux.tar.xz" | tar -xJ
elif [ "$(expr substr $(uname) 1 5)" = "MINGW" ] && [ ! -f ${DIR}/${INNOBIN}.exe ]; then
    $DM -o "$INNO-windows.zip" "http://constexpr.org/innoextract/files/$INNO-windows.zip" 
    unzip -q "$INNO-windows.zip" -d $INNO && rm "$INNO-windows.zip"
fi
${DIR}/${INNOBIN} -se pMetroSetup.exe
cd app/
for i in *.pmz; do
    $ZIP ../download/$(basename "$i" .pmz).zip $i;
done
cd .. && rm -rf pMetroSetup.exe app/

$DM "https://mrsuperwolf.github.io/download/Moscow.zip" -o "./download/"
$DM "https://mrsuperwolf.github.io/download/Moscow_{Mobile,Next,Next_ST}.zip" -o "./download/Moscow_#1.zip"

md=$(curl -sI $URL | grep '^Last' | grep -oE '[0-9]{2}[[:space:]][a-zA-Z]{3}[[:space:]][0-9]{4}')
d1=$(date -d "$md" +%s)
d2=$(date -d "30 Dec 1899" +%s)
sed -i "s/Date=\".*\"/Date=\"$(( (d1 - d2) / 86400 ))\"/g" Files.xml

#git add .
#git commit -m "$md"
#git push
