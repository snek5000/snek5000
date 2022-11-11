#!/bin/bash
set -xe
smake() {
   snakemake -j1 --quiet=all "$@" earth space
}
smake
smake --resources="alien=42"
smake --set-resources="space:alien=42"
