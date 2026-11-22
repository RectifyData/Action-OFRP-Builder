# OrangeFox S10+ build request

This branch is the isolated automated build trigger for `beyond2lte`.

- OrangeFox manifest: `12.1`
- Recovery tree: `fox_12.1`
- Target: `twrp_beyond2lte-eng` / `recoveryimage`
- Common tree: `device/samsung/exynos9820-common`
- Target partition: dedicated recovery, maximum image size 67,633,152 bytes

Successful builds are published as prereleases. A build failure must not be represented as a tested recovery release.
