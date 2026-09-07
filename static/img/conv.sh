for f in *.svg; do
    inkscape "$f" \
        --export-width=1024 \
        --export-height=1536 \
        --export-filename="${f%.svg}.png"
done