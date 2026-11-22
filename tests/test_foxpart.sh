#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
BIN=tools/foxpart
TESTROOT=$(mktemp -d)
trap 'rm -rf "$TESTROOT"' EXIT
mkdir -p "$TESTROOT/physical" "$TESTROOT/logical"
printf 'test%012d' 1234 > "$TESTROOT/physical/boot"
dd if=/dev/zero bs=1024 count=128 2>/dev/null >> "$TESTROOT/physical/boot"
cp "$TESTROOT/physical/boot" "$TESTROOT/logical/system"
export FOX_PHYSICAL_BY_NAME="$TESTROOT/physical" FOX_LOGICAL_BY_NAME="$TESTROOT/logical" FOX_TEST_REGULAR_FILES=1
sh "$BIN" list | grep -q 'l:system'
sh "$BIN" backup "$TESTROOT/backup" --all
sh "$BIN" verify "$TESTROOT/backup"
if sh "$BIN" restore "$TESTROOT/backup" l:system >/dev/null 2>&1; then echo 'FAIL: restore without acknowledgement'; exit 1; fi
original=$(sha256sum "$TESTROOT/logical/system" | cut -d' ' -f1)
dd if=/dev/zero bs=1 count=16 conv=notrunc of="$TESTROOT/logical/system" 2>/dev/null
sh "$BIN" restore "$TESTROOT/backup" l:system --confirm
[ "$(sha256sum "$TESTROOT/logical/system" | cut -d' ' -f1)" = "$original" ]
if sh "$BIN" restore "$TESTROOT/backup" p:boot --confirm >/dev/null 2>&1; then echo 'FAIL: critical restore'; exit 1; fi
printf 'tamper' >> "$TESTROOT/backup/l-system.img.zst"
if sh "$BIN" verify "$TESTROOT/backup" >/dev/null 2>&1; then echo 'FAIL: corrupt image'; exit 1; fi
if sh "$BIN" restore "$TESTROOT/backup" l:system --confirm >/dev/null 2>&1; then echo 'FAIL: corrupt restore'; exit 1; fi
echo 'foxpart tests: PASS'
