# OrangeFox Recovery Actions Builder

GitHub Actions builder for OrangeFox Recovery, with a ready-to-run preset for the **Samsung Galaxy S10+ Exynos (beyond2lte)**. The workflow remains configurable for other supported recovery trees.

## Default S10+ build

1. Open **Actions → Recovery Build → Run workflow**, select `main`, and use the defaults.
2. The workflow syncs OrangeFox 12.1 and clones both the device and Exynos 9820 common tree.
3. It runs `lunch twrp_beyond2lte-eng` and `mka adbd recoveryimage -j2`.
4. On success, `recovery.img` and any generated `.zip` or `.tar` files are published as a **GitHub prerelease**. On failure, no release is published.

You can also trigger the same default build by pushing to the dedicated `build/beyond2lte` branch. This keeps automatic builds separate from routine changes on `main`.

| Workflow input | Default |
| --- | --- |
| `SYNC_URL` | `https://gitlab.com/OrangeFox/sync.git` |
| `MANIFEST_BRANCH` | `12.1` |
| `DEVICE_TREE_URL` | `https://github.com/Exynos982x-OrangeFox/android_device_samsung_beyond2lte` |
| `DEVICE_TREE_BRANCH` | `fox_12.1` |
| `DEVICE_PATH` | `device/samsung/beyond2lte` |
| `COMMON_TREE_URL` | `https://github.com/Exynos982x-OrangeFox/android_device_samsung_exynos9820-common` |
| `COMMON_PATH` | `device/samsung/exynos9820-common` |
| `DEVICE_NAME` | `beyond2lte` |
| `MAKEFILE_NAME` | `twrp_beyond2lte` |
| `BUILD_TARGET` | `recovery` |

The builder automatically appends `-eng` to the makefile name and `image` to the build target when necessary. It also accepts the full `twrp_beyond2lte-eng` and `recoveryimage` forms and recognizes the old `twrp_beyond2lte_eng` spelling.

## What the workflow checks

- The common tree is cloned only if both optional common-tree inputs are nonempty.
- `FOX_BUILD_DEVICE` is set before sourcing `build/envsetup.sh`.
- The build must produce a nonempty image; failures are not suppressed.
- For S10+ recovery builds, the resulting image must fit the 67,633,152-byte recovery partition.
- Successful artifacts are published as prereleases because compilation does **not** prove on-device compatibility.

## Partition layout

This OrangeFox tree targets the **LineageOS-style retrofitted dynamic partition layout**, including fastbootd and EROFS/ext4 logical partitions. It is not a universal recovery for stock Samsung layouts. Android 17 data decryption and GSI flashing have not been validated on every ROM.

## Upstream and credits

- [OrangeFox synchronization scripts](https://gitlab.com/OrangeFox/sync)
- [S10+ recovery tree](https://github.com/Exynos982x-OrangeFox/android_device_samsung_beyond2lte)
- [Exynos 9820 common recovery tree](https://github.com/Exynos982x-OrangeFox/android_device_samsung_exynos9820-common)
- [Original Action-OFRP-Builder](https://github.com/azwhikaru/Action-OFRP-Builder)

Thanks to the OrangeFox, TWRP and device-tree contributors.
