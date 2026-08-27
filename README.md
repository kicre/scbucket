# scbucket

A [Scoop](https://scoop.sh) bucket by kicre.

## Usage

```powershell
scoop bucket add scbucket https://github.com/kicre/scbucket
scoop install sing-box-reF1nd
```

## Apps

| Name              | Description |
| ----------------- | ----------- |
| `sing-box-reF1nd` | [sing-box](https://github.com/reF1nd/sing-box) with custom APIs by [reF1nd](https://github.com/reF1nd), Windows binaries from [sing-box-releases](https://github.com/reF1nd/sing-box-releases). Installs `sing-box.exe` for `64bit` and `arm64`; upstream ships no 32-bit Windows build. |

## Auto-update

Two layers keep you current:

1. **Scoop side (per machine).** The manifest's `checkver` reads the releases
   atom feed (no GitHub API rate limits) and picks the newest stable
   `v<number>-reF1nd` tag; `autoupdate` rewrites url/hash for it. So plain
   `scoop update sing-box-reF1nd` (or `scoop update *`) works even if nobody
   touched this bucket. Pin with `scoop hold sing-box-reF1nd`.

2. **Bucket side (CI).** [.github/workflows/autoupdate.yml](.github/workflows/autoupdate.yml)
   runs [scripts/autoupdate.py](scripts/autoupdate.py) instantly when upstream
   publishes a stable release (`release: published`; beta/rc prereleases never
   trigger it) plus a daily safety-net cron. The script reads SHA-256 digests
   from the GitHub asset metadata — it never downloads the binaries — and
   commits `version`/`hash` bumps back to this repo, so fresh installs always
   resolve to the current stable build.

Run the updater locally:

```console
$ python3 scripts/autoupdate.py --dry-run              # check only
$ GITHUB_TOKEN=<pat> python3 scripts/autoupdate.py     # bump the manifest
$ python3 scripts/autoupdate.py --hash-file file.zip   # local sha256 helper
```
