#!/usr/bin/env python3
"""Package recovery.img as a checked Odin AP TAR and OrangeFox-flashable ZIP."""
from __future__ import annotations
import hashlib
import sys
import tarfile
import zipfile
from pathlib import Path

MAX_RECOVERY = 67633152


def create_packages(src: Path, out: Path, prefix: str) -> None:
    src = src.resolve(strict=True)
    out.mkdir(parents=True, exist_ok=True)
    size = src.stat().st_size
    if not (0 < size <= MAX_RECOVERY and size % 512 == 0):
        raise ValueError(f"invalid recovery image size: {size}")
    with src.open("rb") as f:
        if f.read(8) != b"ANDROID!":
            raise ValueError("recovery image is not an Android boot image")
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    installer = f'''#!/sbin/sh
# Installer for the dedicated Samsung Galaxy S10+ Exynos recovery partition.
PATH=/sbin:/system/bin:/system/xbin:$PATH
export PATH
OUTFD="$2"
ARCHIVE="$3"
TMP="/tmp/ofox-flash-$$.img"
TARGET=""
cleanup() {{ rm -f "$TMP"; }}
trap cleanup EXIT HUP INT TERM
ui() {{
  echo "ui_print $*" > "/proc/self/fd/$OUTFD" 2>/dev/null || echo "$*"
  echo "ui_print" > "/proc/self/fd/$OUTFD" 2>/dev/null || :
}}
die() {{ ui "ERROR: $*"; exit 1; }}
ui 'Galaxy S10+ Exynos OrangeFox recovery installer'
ui 'This overwrites recovery only; NO automatic wipe or reboot'
DEV=$(getprop ro.product.device 2>/dev/null || :)
case "$DEV" in ''|beyond2lte) : ;; *) die "Wrong device: $DEV" ;; esac
for P in /dev/block/platform/13d60000.ufs/by-name/recovery /dev/block/by-name/recovery /dev/block/bootdevice/by-name/recovery; do
    if [ -b "$P" ]; then TARGET="$P"; break; fi
done
[ -n "$TARGET" ] || die 'Recovery block device not found'
for CMD in unzip sha256sum blockdev dd; do
    command -v "$CMD" >/dev/null 2>&1 || die "Missing utility $CMD"
done
[ -f "$ARCHIVE" ] || die 'Cannot access ZIP archive'
ui 'Extracting recovery.img'
unzip -p "$ARCHIVE" recovery.img > "$TMP" || die 'Extract failed'
SIZE=$(wc -c < "$TMP" | tr -d '[:space:]')
[ "$SIZE" = '{size}' ] || die "Wrong recovery image size: $SIZE"
SUM=$(sha256sum "$TMP" | cut -d ' ' -f1)
[ "$SUM" = '{digest}' ] || die 'Recovery image hash mismatch'
TARGET_SIZE=$(blockdev --getsize64 "$TARGET") || die 'Cannot determine partition size'
[ "$TARGET_SIZE" -ge "$SIZE" ] || die 'Recovery partition too small'
ui 'Flashing recovery partition...'
dd if="$TMP" of="$TARGET" bs=1048576 || die 'Write failed'
sync
ui 'Checking flashed image...'
COUNT=$((SIZE / 512))
READ_HASH=$(dd if="$TARGET" bs=512 count="$COUNT" 2>/dev/null | sha256sum | cut -d ' ' -f1)
[ "$READ_HASH" = "$SUM" ] || die 'Read-back checksum mismatch - do not reboot normally'
ui 'Recovery image flashed and verified'
exit 0
'''
    info = ("Experimental OrangeFox S10+ Exynos recovery build.\n"
            "Only for unlocked beyond2lte with a compatible recovery partition layout.\n"
            "No system, vendor, data, EFS or modem changes; no wipe/reboot.\n"
            "The image has not been proven bootable on hardware.\n"
            f"SHA256(recovery.img) = {digest}\n")
    tarpath = out / f"{prefix}-Odin.tar"
    zippath = out / f"{prefix}-flashable.zip"
    with tarfile.open(tarpath, "w", format=tarfile.USTAR_FORMAT) as tar:
        ti = tar.gettarinfo(str(src), arcname="recovery.img")
        ti.uid = ti.gid = 0
        ti.uname = ti.gname = "root"
        ti.mtime = 0
        with src.open("rb") as f:
            tar.addfile(ti, f)
    with zipfile.ZipFile(zippath, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        def write(name: str, data: bytes, mode: int = 0o644):
            zi = zipfile.ZipInfo(name, date_time=(2026, 11, 22, 0, 0, 0))
            zi.create_system = 3
            zi.external_attr = (0o100000 | mode) << 16
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=1)
        write("META-INF/com/google/android/update-binary", installer.encode(), 0o755)
        write("META-INF/com/google/android/updater-script",
              b"# Recovery image installer: handled by update-binary\n")
        write("README.txt", info.encode())
        write("SHA256SUMS.txt", f"{digest}  recovery.img\n".encode())
        z.write(src, "recovery.img", compress_type=zipfile.ZIP_STORED)
    with tarfile.open(tarpath, "r") as tar:
        with tar.extractfile("recovery.img") as f:
            assert hashlib.sha256(f.read()).hexdigest() == digest
    with zipfile.ZipFile(zippath, "r") as z:
        assert z.testzip() is None
        assert hashlib.sha256(z.read("recovery.img")).hexdigest() == digest
    print(f"Verified IMG/TAR/ZIP, SHA256 {digest}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit("Usage: package_recovery.py recovery.img OUTPUT_DIR [PREFIX]")
    create_packages(Path(sys.argv[1]), Path(sys.argv[2]),
                    sys.argv[3] if len(sys.argv) > 3 else "OrangeFox-R12.0-Unofficial-beyond2lte")
