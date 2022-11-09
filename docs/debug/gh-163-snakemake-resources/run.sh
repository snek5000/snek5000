#!/bin/bash
set -xe
snakemake -j1 earth space
snakemake -j1 --resources="alien=42" earth space
snakemake -j1 --set-resources="space:alien=42" earth space
