# scbucket

[![Tests](https://github.com/kicre/scbucket/actions/workflows/ci.yml/badge.svg)](https://github.com/kicre/scbucket/actions/workflows/ci.yml) [![Excavator](https://github.com/kicre/scbucket/actions/workflows/excavator.yml/badge.svg)](https://github.com/kicre/scbucket/actions/workflows/excavator.yml)

My [Scoop](https://scoop.sh) bucket, built on the official
[BucketTemplate](https://github.com/ScoopInstaller/BucketTemplate).

## Apps

| Name              | Description |
| ----------------- | ----------- |
| `sing-box-reF1nd` | [sing-box](https://github.com/reF1nd/sing-box) with custom APIs by [reF1nd](https://github.com/reF1nd); Windows builds from [sing-box-releases](https://github.com/reF1nd/sing-box-releases). Installs `sing-box.exe` for `64bit`/`arm64` (upstream has no 32-bit build). |

## Usage

```pwsh
scoop bucket add scbucket https://github.com/kicre/scbucket
scoop install scbucket/sing-box-reF1nd
```

## Maintained by Excavator 🤖

Manifests are kept current by the official Scoop
[Excavator](https://github.com/ScoopInstaller/GithubActions) bot
([`.github/workflows/excavator.yml`](.github/workflows/excavator.yml)),
running every 4 hours: it runs `checkver` on every manifest, downloads new
builds to compute hashes via `autoupdate`, and commits
`sing-box-reF1nd: Update to version X` itself. Nothing to do.

Per machine, a plain `scoop update sing-box-reF1nd` (or `scoop update *`)
always tracks upstream too; pin with `scoop hold sing-box-reF1nd`.

## For maintainers

- New app: copy `bucket/app-name.json.template` to `bucket/<app>.json`.
- Locally check every manifest: `bin/checkver.ps1 -Update`
- Batch hash fixes: `bin/checkhashes.ps1`, formatting: `bin/formatjson.ps1`
- Tests (what CI runs): `bin/test.ps1`

## License

Public domain (as in the upstream template). App binaries keep their own
licenses (sing-box-reF1nd: GPL-3.0-or-later).
