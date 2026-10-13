#!/usr/bin/env bash
# Usage: tools/package.sh <produit>  -> livraison/<name>_OBJ.zip (OBJ + MTL + texture + LISEZ-MOI + aperçus)
set -euo pipefail
cd "$(dirname "$0")/.."
P="$1"; NAME=$(python3 -c "import json;print(json.load(open('tools/products.json'))['$P']['name'])")
D="livraison/$P"; rm -rf "$D"; mkdir -p "$D/apercus"
cp "build/$P/$NAME.obj" "build/$P/$NAME.mtl" build/$P/${P}_face-*.png "build/$P/LISEZ-MOI.txt" "$D/"
cp renders/$P/apercu_*.png "$D/apercus/"
rm -f "livraison/${NAME}_OBJ.zip"
(cd "$D" && zip -q -9 -r "../${NAME}_OBJ.zip" .)
ls -la "livraison/${NAME}_OBJ.zip"
