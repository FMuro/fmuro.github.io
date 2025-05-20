#!/bin/zsh

# run this script in the project's root directory

for file in src/assets/img/*.jpg
do
  magick $file  -write mpr:img +delete \
    \( mpr:img -resize 576x +write ${file%.*}_576w.webp \) \
    \( mpr:img -resize 768x +write ${file%.*}_768w.webp \) \
    \( mpr:img -resize 992x +write ${file%.*}_992w.webp \) \
    \( mpr:img -resize 1200x +write ${file%.*}_1200w.webp \) \
    \( mpr:img -resize 1400x +write ${file%.*}_1400w.webp \) \
    null:
done

find src/assets/img/ \( -name "*.jpg" -o -name "*.jpeg" \) -execdir mogrify -format webp {} +
