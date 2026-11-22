#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
TESTROOT=$(mktemp -d)
trap 'rm -rf "$TESTROOT"' EXIT
mkdir -p "$TESTROOT/physical" "$TESTROOT/logical"
printf 'test%012d' 1234 > "$TESTROOT/physical/boot"
dd if=/dev/zero bs=1024 count=128 2>/dev/null >> "$TESTROOT/physical/boot"
cp "$TESTROOT/physical/boot" "$TESTROOT/logical/system"
export FOX_PHYSICAL_BY_NAME="$TESTROOT/physical"
export FOX_LOGICAL_BY_NAME="$TESTROOT/logical"
export FOX_TEST_REGULAR_FILES=1
sh tools/foxpart list | grep -q 'l:system'
for CODEC in gzip zstd; do
    export FOX_BACKUP_CODEC="$CODEC"
    DIR="$TESTROOT/backup-$CODEC"
    sh tools/foxpart backup "$DIR" --all
    case "$CODEC" in zstd) test -f "$DIR/l-system.img.zst" ;; gzip) test -f "$DIR/l-system.img.gz" ;; esac
    sh tools/foxpart verify "$DIR"
    if sh tools/foxpart restore "$DIR" l:system >/dev/null 2>&1; then
        echo 'FAIL: restore without confirmation'
        exit 1
    fi
    original=$(sha256sum "$TESTROOT/logical/system" | cut -d' ' -f1)
    dd if=/dev/zero bs=1 count=16 conv=notrunc of="$TESTROOT/logical/system" 2>/dev/null
    sh tools/foxpart restore "$DIR" l:system --confirm
    [ "$(sha256sum "$TESTROOT/logical/system" | cut -d' ' -f1)" = "$original" ]
    if sh tools/foxpart restore "$DIR" p:boot --confirm >/dev/null 2>&1; then
        echo 'FAIL: unapproved critical restore'
        exit 1
    fi
    printf tamper >> "$DIR/l-system.img.$(test "$CODEC" = zstd && echo zst || echo gz)"
    if sh tools/foxpart verify "$DIR" >/dev/null 2>&1; then
        echo 'FAIL: corrupted archive accepted'
        exit 1
    fi
    if sh tools/foxpart restore "$DIR" l:system --confirm >/dev/null 2>&1; then
        echo 'FAIL: corrupted archive restored'
        exit 1
    fi
done
echo 'foxpart backup/restore tests (gzip + zstd): PASS'
