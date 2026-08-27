#!/usr/bin/env python3
"""Bump a Scoop manifest to the latest stable reF1nd/sing-box-releases build.

Only touches "version" and the per-architecture "hash" fields; url/extract_dir
keep their $version placeholders and need no edits.

Hashes come from the GitHub asset `digest` field (SHA-256), so nothing is
downloaded. Authenticated requests (GITHUB_TOKEN / GH_TOKEN env) are used when
available, since unauthenticated API access is easily rate-limited; if the API
is unreachable the script falls back to scraping the release pages and computes
hashes by downloading the two Windows assets.

Usage:
    python3 scripts/autoupdate.py [--dry-run] [manifest-path]
    python3 scripts/autoupdate.py --hash-file <file>...   # compute sha256 locally
Exit codes: 0 = no change (or dry-run), 1 = manifest updated or error.
"""
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = "reF1nd/sing-box-releases"
DEFAULT_MANIFEST = Path(__file__).resolve().parent.parent / "bucket" / "sing-box-reF1nd.json"
# e.g. sing-box-1.13.19-reF1nd-windows-amd64.zip
ASSET_RE = re.compile(r"^sing-box-.+-reF1nd-windows-(amd64|arm64)\.zip$")
# e.g. v1.13.19-reF1nd ; rc/beta tags are prereleases and filtered by GitHub's
# /releases/latest endpoint, so they never reach this point.
TAG_RE = re.compile(r"^v(.+)-reF1nd$")


def api(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "scbucket-autoupdate",
            **({"Authorization": f"Bearer {tok}"} if (tok := (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))) else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 429):
            print("note: GitHub API rate limited (403/429); falling back to HTML scraping",
                  file=sys.stderr)
            return None
        sys.exit(f"error: GitHub API returned HTTP {exc.code} for {path}")


def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "scbucket-autoupdate"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", "replace")


TAG_LINK_RE = re.compile(r"releases/tag/([^\"?>]+)")


def from_html():
    """Fallback when the API is unavailable: scrape the releases pages.

    Mirrors the manifest's checkver: the first `v<digits>-reF1nd` tag in
    newest-first order (GitHub's /releases lists stable releases, not
    drafts/prereleases), then read asset links from the expanded-assets fragment.
    Returns the same shape as /repos/.../releases/latest, minus digests.
    """
    for page in ("", "?page=2", "?page=3"):
        tags = [t for t in TAG_LINK_RE.findall(http_get(f"https://github.com/{REPO}/releases{page}"))
                if re.fullmatch(r"v[\d.]+-reF1nd", t)]
        if tags:
            tag = tags[0]
            html = http_get(f"https://github.com/{REPO}/releases/expanded_assets/{tag}")
            names = re.findall(
                rf'href="/{REPO}/releases/download/{re.escape(tag)}/([^"]+)"', html)
            if not names:
                print(f"debug: expanded_assets is {len(html)} bytes, "
                      f"contains 'download' {html.count('download')}x", file=sys.stderr)
            assets = [{"name": n, "digest": None} for n in names]
            print(f"note: resolved {tag} via HTML (hashes will be computed by downloading assets)",
                  file=sys.stderr)
            return {"tag_name": tag, "assets": assets}
    sys.exit("error: no stable v*-reF1nd tag found on releases pages")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_download(url):
    h = hashlib.sha256()
    req = urllib.request.Request(url, headers={"User-Agent": "scbucket-autoupdate"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        for chunk in iter(lambda: resp.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    argv = sys.argv[1:]
    if "--hash-file" in argv:
        for p in [a for a in argv if not a.startswith("-")]:
            print(f"{sha256_of(p)}  {p}")
        return 0
    dry = "--dry-run" in argv
    positional = [a for a in argv if not a.startswith("-")]
    manifest_path = Path(positional[0]) if positional else DEFAULT_MANIFEST

    release = api(f"/repos/{REPO}/releases/latest") or from_html()
    m = TAG_RE.match(release["tag_name"])
    if not m:
        sys.exit(f"error: unexpected tag {release['tag_name']!r}")
    version = m.group(1)

    hashes = {}
    for asset in release["assets"]:
        am = ASSET_RE.match(asset["name"])
        if not am:
            continue
        if (digest := asset.get("digest")) and digest.startswith("sha256:"):
            hashes[am.group(1)] = digest.removeprefix("sha256:")
        else:
            # HTML fallback: no digest available, compute it from the asset
            url = f"https://github.com/{REPO}/releases/download/{release['tag_name']}/{asset['name']}"
            print(f"downloading {asset['name']} to compute hash ...", file=sys.stderr)
            hashes[am.group(1)] = sha256_download(url)
    for arch in ("amd64", "arm64"):
        if arch not in hashes:
            sys.exit(f"error: release {release['tag_name']} has no windows-{arch} asset")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    changes = []
    if manifest["version"] != version:
        changes.append(f"version: {manifest['version']} -> {version}")
        manifest["version"] = version
    arch_map = {"64bit": "amd64", "arm64": "arm64"}
    for s_arch, d_arch in arch_map.items():
        block = manifest["architecture"][s_arch]
        if block["hash"] != hashes[d_arch]:
            changes.append(f"hash[{s_arch}]: {block['hash'][:12]}... -> {hashes[d_arch][:12]}...")
            block["hash"] = hashes[d_arch]

    if not changes:
        print(f"up to date: sing-box-reF1nd {version}")
        return 0
    for line in changes:
        print(line)
    if dry:
        print("dry run: manifest not modified")
        return 0
    manifest_path.write_text(json.dumps(manifest, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"updated {manifest_path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
