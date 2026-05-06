# smartmet-base-international

Meta-package that turns a fresh AlmaLinux/Rocky/RHEL host into a SmartMet
server. Pulls in the SmartMet runtime (`smartmet-qdtools`, `smartmet-qdcontour`,
`smartmet-shapetools`), the system services SmartMet relies on (PostgreSQL,
Samba, NFS, Docker, fail2ban, firewalld, …), creates the `smartmet` and `gts`
system users, lays out `/smartmet/{bin,cnf,data,run,share,tmp,www,logs,…}`,
drops in cron entries, and configures firewalld + SELinux so a containerised
SmartMet web frontend can serve `/smartmet/www`.

## Supported OS

Built and released for:

- AlmaLinux / Rocky / RHEL **8**
- AlmaLinux / Rocky / RHEL **9**
- AlmaLinux / Rocky / RHEL **10**

CI builds noarch + src RPMs against `rockylinux/rockylinux:{8,9,10}`.

## Install

End users do **not** clone this repo. They install via dnf, which is wired up
by [`smartmet-install`](https://github.com/fmidev/smartmet-install):

```sh
curl -O https://raw.githubusercontent.com/fmidev/smartmet-install/master/smartmet-install-10.sh
chmod +x smartmet-install-10.sh
./smartmet-install-10.sh
```

The `smartmet-install` script enables the FMI smartmet-open repo and
`dnf install`s `smartmet-base-international` from there.

## What `%post` configures

- Adds `smartmet` to the `wheel` and `docker` groups
- Enables and starts `docker`, `firewalld`, `fail2ban`, `nfs-server`, `smb`,
  `rsyncd`, `yum-cron`, `vsftpd`
- Opens firewall services: `http`, `https`, `samba`, `nfs`, `mountd`,
  `rpc-bind`, `ftp` (review with `firewall-cmd --list-all` for an
  internet-facing host)
- Labels `/smartmet/www` and `/smartmet/editor/smartalert` with
  `httpd_sys_content_t` so a containerised web server can bind-mount them
- Sets `samba_export_all_rw=1` and writes a default `/etc/samba/smb.conf`
  exposing `/smartmet/editor` as the `[smartmet]` share

## Release process

Releases are **fully automated** — there is no manual `git tag` step.

1. Edit `Version:` and add a `%changelog` entry in
   `smartmet-base-international.spec`.
2. Commit and push to `master`.
3. CI (`.github/workflows/main.yml`) does:
   - reads `Version:` from the spec
   - builds noarch + src RPMs in parallel on Rocky 8 / 9 / 10
   - creates (or replaces, idempotently) GitHub release `v<Version>` with
     all six RPMs attached
4. The `smartmet-open` repo signing/mirroring pipeline (run by FMI) picks
   the release artifacts up.

If a release for the spec version already exists, CI re-uploads the RPMs
with `gh release upload --clobber`. To re-trigger a release after a CI
infrastructure issue, push an empty commit (no spec change) — same
`Version:`, same tag, assets refreshed.

## Build locally (optional, for development)

```sh
podman run --rm -it -v "$PWD":/src -w /src rockylinux/rockylinux:10 bash
dnf -y install rpm-build rpmdevtools gcc make rpm-devel tree
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
mkdir -p ~/rpmbuild/SOURCES/smartmet-base-international
cp ./*.spec ~/rpmbuild/SPECS/
cp -r ./* ~/rpmbuild/SOURCES/smartmet-base-international/
rpmbuild -ba ~/rpmbuild/SPECS/*.spec
```

## License

MIT — see `LICENSE`.
