# Lossless full-partition backup and recovery install formats — S10+ OrangeFox

The optional recovery-terminal command \`foxpart\` archives physical (\`p:\`) and retrofitted logical (\`l:\`) block partitions losslessly, without reformatting them or changing OrangeFox's native GUI backup implementation.

## Commands

\`\`\`sh
foxpart list
foxpart backup /external_sd/fox-full-001 --all
foxpart verify /external_sd/fox-full-001
\`\`\`

Select partitions to avoid duplicating the physical \`system\` container and mapped logical partitions:

\`\`\`sh
foxpart backup /external_sd/my-backup p:boot l:system l:vendor l:product
foxpart verify /external_sd/my-backup
\`\`\`

**Codec compatibility:** \`FOX_BACKUP_CODEC=auto\` (default) uses Zstandard where an executable is installed and transparently falls back to the recovery's built-in **gzip** where it is not. Set \`FOX_BACKUP_CODEC=gzip\` or \`FOX_BACKUP_CODEC=zstd\` explicitly to force a format. Compression level \`FOX_ZSTD_LEVEL=1..9\` (default 3) applies to the selected codec. Files end in \`.img.gz\` or \`.img.zst\`. Existing legacy \`#FOX1\` Zstandard archives remain readable.

## Restore safeguards

\`foxpart verify DEST\` checks each archive's SHA-256 hash, compressed stream integrity, decompressed SHA-256 and original byte size before accepting it. Restore operates **one partition at a time**: \`foxpart restore DEST l:vendor --confirm\`. Boot, recovery, modem, EFS, userdata and other protected partitions additionally require \`--critical\`, and matching target sizes are mandatory. The tool refuses mounted targets and path mismatches.

Never write backups to the internal \`/data\`, \`/sdcard\` or a filesystem whose block device is being backed up. Use a real externally mounted SD card or USB drive with enough free space. For very large partitions use exFAT or another filesystem supporting files above 4 GiB. Backup of mounted /data is blocked; encryption keys and metadata can make cross-ROM or reformatted raw-data restores unusable.

**A recovery image build is not proof of bootability or recoverability.** Keep independent partition backups before flashing an experimental image.

## GitHub release formats

Successful S10+ recovery builds publish \`recovery.img\`, \`*-Odin.tar\` for Odin's AP selection, and \`*-flashable.zip\` for flashing from an existing compatible recovery. The flashable ZIP verifies the image before writing the **dedicated recovery** partition and verifies a read-back checksum; it does not wipe or reboot the device. Only install on unlocked Samsung Galaxy S10+ Exynos (\`beyond2lte\`) with the matching recovery layout. None of the internal \`FFiles/\` ZIP utilities bundled within the recovery ramdisk must be installed separately.

Run \`sh tests/test_foxpart.sh\` (requires \`zstd\` and \`gzip\` on the host) to test both compression formats. Hardware verification is still outstanding.
