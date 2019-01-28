#!/bin/sh
d1=$(date -d "now" +%s)
d2=$(date -d "30 Dec 1899" +%s)
sed -i "s/Date=\".*\"/Date=\"$(( (d1 - d2) / 86400 ))\"/g" Files.xml

rm -f pMetroSetup.exe app/* download/*
aria2c.exe 'http://pmetro.su/download/pMetroSetup.exe'
./innoextract.exe -e pMetroSetup.exe # innoextract (http://constexpr.org/innoextract/)

cd app
for i in *.pmz; do
7z.exe a -tzip -bb0 ../download/$(basename.exe "$i" .pmz).zip $i;
done

git add .
git commit -m $(date -d now +%F)
git push
