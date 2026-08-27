# scbucket

A [Scoop](https://scoop.sh) bucket by kicre.

## Usage

```powershell
scoop bucket add scbucket https://github.com/kicre/scbucket
```

## Apps

| Name        | Description                                             |
| ----------- | ------------------------------------------------------- |
| `sing-box`  | [sing-box](https://github.com/reF1nd/sing-box) with custom APIs by [reF1nd](https://github.com/reF1nd) (binaries from [sing-box-releases](https://github.com/reF1nd/sing-box-releases)) |

Install / update:

```powershell
scoop install sing-box
scoop update sing-box
```

Available architectures: `64bit` (windows-amd64) and `arm64` (windows-arm64).
32-bit Windows is not provided by upstream releases, so it is not installable via this bucket.
