f=$(basename "$PWD").txt
echo "the thing" > "$f" && git add "$f" && git commit -q -m "stub: $f"
