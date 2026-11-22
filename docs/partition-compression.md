# Lossless partition compression for the S10+ OrangeFox recovery

The `foxpart` command adds an **opt-in, lossless Zstandard raw-image backup** for all discoverable physical (`p:`) and mapped logical (`l:`) partitions. This is separate from TWRP's native `.win` GUI backup format, boot ramdisk LZMA, and F2FS filesystem compression.

From the OrangeFox Terminal:

```sh
foxpart list
foxpart backup /external_sd/fox-full-001 --all
foxpart verify /external_sd/fox-full-001
```

For a selected subset:

```sh
foxpart backup /external_sd/fox-selected p:boot l:system l:vendor
foxpart verify /external_sd/fox-selected
```

To use greater compression: `FOX_ZSTD_LEVEL=7 foxpart backup /external_sd/high-ratio p:boot l:vendor`. Levels 1–9 are supported (default 3); Zstandard uses one thread to limit RAM use.

Every archive uses `p-NAME.img.zst` or `l-NAME.img.zst` with SHA-256 checksums and original partition size recorded in `manifest.txt`. Back up to a **separate external SD card or USB drive**, not internal `/data` or `/sdcard`, particularly when backing up userdata. `--all` also includes the physical `system` container and mapped logical partitions on retrofitted-super devices, so space requirements can be high. The helper refuses backups of mounted partitions.

**Restore is explicitly opt-in, one partition at a time.** Verify the archive and exact partition layout, unmount the target, then use `foxpart restore /external_sd/fox-selected l:vendor --confirm`. Sensitive partitions (boot, vbmeta, modem, userdata, EFS and similar) additionally require `--critical` and independent hardware verification. Incorrect restores can brick the device. The tool verifies both compressed and decompressed SHA-256 hashes and refuses a target-size mismatch.

Android FBE/metadata encryption can make raw userdata restores unusable across device reformatting or key changes. Do not treat this script as a verified complete-device restore plan. It is a **recovery terminal feature**; a GUI integration is not included.

## Build integration

The builder copies `tools/foxpart` into `device/samsung/exynos9820-common/recovery/root/system/bin/foxpart`, enables `FOX_USE_ZSTD_BINARY=1`, and checks that the resulting `recovery.img` fits the 67,633,152-byte recovery partition and the script is staged in the ramdisk. It publishes only successful build outputs as GitHub prereleases. The first release remains unchanged.

The separate `Audit first OrangeFox recovery image` workflow fetches release `45036207179`'s `.img` in GitHub Actions, validates its boot magic, SHA-256 and size, then uploads a text audit report to that original release.

## Source and validation

Run `sh tests/test_foxpart.sh` on Ubuntu with `zstd` installed to exercise backup, hash verification, restore, tamper rejection, and critical-restore safeguards. Hardware testing remains necessary before treating a recovery build as stable.
