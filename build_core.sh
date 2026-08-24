#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Building libdaxda_core.so..."

clang++ -std=c++17 -O3 -fPIC -shared \
    daxda_engine/csrc/governed_authority_gate.cpp \
    daxda_engine/csrc/daxda_core.cpp \
    -o libdaxda_core.so

cp libdaxda_core.so daxda_guard/libdaxda_core.so

echo "Successfully built and deployed libdaxda_core.so!"
