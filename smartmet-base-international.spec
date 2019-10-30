%define smartmetroot /smartmet

Name:           smartmet-base-international
Version:        19.10.30
Release:        2%{?dist}.fmi
Summary:        SmartMet basic system
Group:          System Environment/Base
License:        MIT
URL:            http://www.weatherproof.fi
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:	noarch
Obsoletes:	smartmet-base-caribbean
Obsoletes:	smartmet-base-pacific

Requires:       smartmet-qdtools
Requires:	smartmet-qdcontour
Requires:	smartmet-shapetools
#Requires:	smartmet-data-meteor
#Requires:	smartmet-data-synop
#Requires:	smartmet-data-sounding
Requires:	smartmet-share-php
#Requires:	smartmet-data-metar
#Requires:	smartmet-data-gfs
#Requires:	smartmet-data-gem
#Requires:	smartmet-brainstorm-backend
#Requires:	smartmet-brainstorm-autocomplete
#Requires:	smartmet-brainstorm-qengine
#Requires:	smartmet-brainstorm-timeseries

Requires:	bc
Requires:	bind-utils
Requires:	bzip2
Requires:	cronie
Requires:       docker-ce
Requires:	emacs-nox
Requires:	fail2ban-firewalld
Requires:	fail2ban-systemd
Requires:	ftp
Requires:	git
Requires:	htop
Requires:	httpd
Requires:	ImageMagick
#Requires:	mail
Requires:	nfs-utils
Requires:	lbzip2
Requires:	libnfsidmap
Requires:	nano
Requires:	ntp
Requires:	openvpn
Requires:	parallel
Requires:	perl
Requires:	php
Requires:	php-gd
Requires:	policycoreutils-python
Requires:	procmail
Requires:	rsync
Requires:	samba
Requires:	samba-client
Requires:	time
Requires:	telnet
Requires:	traceroute
Requires:	vsftpd
Requires:	wget
Requires:	wgrib2
Requires:	xinetd
Requires:	zip
Requires:	unzip
Requires:	man
Requires:	mlocate
Requires:	whois
Requires:       yum-cron
Requires:       net-tools
Requires:       cifs-utils
Requires:       certbot python2-certbot-apache


%description
The filesystem package is one of the basic packages that is installed
on a SmartMet Linux system. Filesystem contains the basic directory
layout for a SmartMet system, including the correct permissions
for the directories.

%prep

%build

%pre
getent passwd smartmet || adduser -m smartmet
getent passwd gts || adduser -m gts
getent passwd gts && usermod -d /smartmet/data/gts gts

%install
rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT
cd $RPM_BUILD_ROOT

mkdir -p %{buildroot}%{_sysconfdir}/cron.d
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
mkdir -p %{buildroot}%{_sysconfdir}/yum.repos.d
mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
mkdir -p %{buildroot}%{_sysconfdir}/php.d
mkdir -p %{buildroot}%{_sysconfdir}/ppp/peers
mkdir -p %{buildroot}%{_sysconfdir}/samba
mkdir -p %{buildroot}%{_sysconfdir}/fail2ban/action.d
mkdir -p .%{smartmetroot}/cnf/cron/{cron.d,cron.10min,cron.hourly,cron.daily,cron.weekly,cron.monthly}
mkdir -p .%{smartmetroot}/cnf/triggers.d/{quick,lazy}
mkdir -p .%{smartmetroot}/editor/{in,out,sat,smartalert}
mkdir -p .%{smartmetroot}/{bin,data,products,run,share,tmp,www,logs}
mkdir -p .%{smartmetroot}/logs/data
mkdir -p .%{smartmetroot}/logs/triggers/output
mkdir -p .%{smartmetroot}/data/gts/{metar,synop,ship,buoy,sounding}/world/querydata
mkdir -p .%{smartmetroot}/data/incoming
mkdir -p .%{smartmetroot}/run/{products,data}
mkdir -p .%{smartmetroot}/tmp/{data,www}
mkdir -p .%{smartmetroot}/share/{maps,fonts,coordinates}
mkdir -p .%{smartmetroot}/share/gis/shapes
mkdir -p .%{smartmetroot}/cnf/misc

cat > %{buildroot}%{_sysconfdir}/profile.d/smartmet.sh <<EOF
PATH=\$PATH:/smartmet/bin
EOF

cat > %{buildroot}%{_sysconfdir}/php.d/smartmet.ini <<EOF
date.timezone = "Etc/UTC"
include_path = ".:/usr/share/pear:/usr/share/php:/smartmet/share/php"
EOF

cat > %{buildroot}%{_sysconfdir}/cron.d/smartmet.cron <<EOF
PATH=/bin:/usr/bin:/usr/local/bin:/smartmet/bin
# SmartMet run-parts
*/10 * * * * smartmet run-parts %{smartmetroot}/cnf/cron/cron.10min
01 * * * * smartmet run-parts %{smartmetroot}/cnf/cron/cron.hourly
00 0 * * * smartmet run-parts %{smartmetroot}/cnf/cron/cron.daily
02 2 * * 0 smartmet run-parts %{smartmetroot}/cnf/cron/cron.weekly
02 3 1 * * smartmet run-parts %{smartmetroot}/cnf/cron/cron.monthly

# Triggers
* * * * * smartmet run-triggers-quick > /dev/null 2>&1
* * * * * smartmet run-triggers-lazy > /dev/null 2>&1

# Cron
* * * * * root mkcron > /dev/null 2>&1
EOF

cat > %{buildroot}%{_sysconfdir}/httpd/conf.d/smartmet.conf <<EOF
Include /smartmet/cnf/httpd.conf
EOF

cat > %{buildroot}%{_sysconfdir}/ppp/chap-secrets.fmi << EOF
smartmet-xx FMI "SmartMetFMI" *
EOF

cat > %{buildroot}%{_sysconfdir}/ppp/peers/FMI << EOF
pty "pptp fmigate.rauhala.net --nolaunchpppd"
lock
noauth
nobsdcomp
nodeflate
name smartmet-ag
remotename FMI
ipparam FMI
persist
maxfail 0
EOF

cat > %{buildroot}%{_sysconfdir}/fail2ban/jail.local <<EOF
[DEFAULT]
findtime  = 5000
[sshd]
enabled = true
EOF

cat > %{buildroot}%{_sysconfdir}/fail2ban/action.d/firewallcmd-ipset.local <<EOF
[Init]
bantime = 10000
EOF

cat > %{buildroot}%{smartmetroot}/cnf/httpd.conf << EOF
ServerName localhost
ServerTokens Prod
Timeout 120
SendBufferSize 131072

<FilesMatch "\.(inc|cnf|conf|bak|old|php~|pl~)$">
        Order allow,deny
        Deny from all
</FilesMatch>

<Directory "/smartmet/www">
    Options Indexes FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>

NameVirtualHost *:80
<VirtualHost *:80>
	ServerName	smartmetsrv
	DocumentRoot    /smartmet/www
	ErrorLog        /var/log/httpd/smartmet-error_log
	TransferLog     /var/log/httpd/smartmet-access_log
	ScriptAlias     /cgi-bin/cropper /usr/bin/cropper
	ScriptAlias     /cgi-bin/cropper_auth /usr/bin/cropper_auth
</VirtualHost>
EOF

cat > %{buildroot}%{smartmetroot}/cnf/smartmet.conf << EOF
# ----------------------------------------------------------------------
# qdarea
# ----------------------------------------------------------------------

qdarea::querydata = /smartmet/data/gfs/pacific/surface/querydata
qdarea::timezone = local


imagine::font_path      = /smartmet/share/fonts:/usr/lib/X11/fonts:/usr/share/X11/fonts:/usr/share/fonts/X11
imagine::hershey_path   = /smartmet/share/fonts/hershey:/var/www/share/hershey
imagine::truetype_path  = /smartmet/share/fonts/ttf:/var/www/share/fonts
imagine::type1_path     = /smartmet/share/fonts/type1:/var/www/share/type1
imagine::gshhs_path     = /smartmet/share/gis/gshhs

# ----------------------------------------------------------------------
# qdpoint
# ----------------------------------------------------------------------
qdpoint::timezone = local
qdpoint::querydata_file = /smartmet/data/gfs/pacific/surface/querydata
EOF

cat > %{buildroot}%{smartmetroot}/cnf/palcrypt.conf << EOF
-/0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz
KdJNvMzl_SFY2HtBTQpPIOGiuVkg8Eeb-yxsCwhqL0WUADmnjZ54/aro1XR739f6c
EOF

cat > %{buildroot}%{smartmetroot}/cnf/misc/arrow.path << EOF
# This is a northern wind arrow:
#
#   *
#   *
#   *
#  ***
#   *
M0,-60 L-30,-20 -10,-20 -10,40 10,40 10,-20 30,-20 0,-60
EOF

# TODO robots.txt

install -m 755 %_topdir/SOURCES/smartmet-base-international/unixtools/mkcron %{buildroot}%{smartmetroot}/bin/
install -m 755 %_topdir/SOURCES/smartmet-base-international/unixtools/cleaner %{buildroot}%{smartmetroot}/bin/
install -m 755 %_topdir/SOURCES/smartmet-base-international/unixtools/run-triggers-quick %{buildroot}%{smartmetroot}/bin/
install -m 755 %_topdir/SOURCES/smartmet-base-international/unixtools/run-triggers-lazy %{buildroot}%{smartmetroot}/bin/
install -m 755 %_topdir/SOURCES/smartmet-base-international/unixtools/trigger %{buildroot}%{smartmetroot}/bin/
install -m 755 %_topdir/SOURCES/smartmet-base-international/unixtools/utcrun %{buildroot}%{smartmetroot}/bin/

%post
# Enable smartmet user to run sudo commands
gpasswd -a smartmet wheel

# Enable firewalld
systemctl enable firewalld
systemctl start firewalld

# Enable fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Enable nfs
systemctl enable rpcbind 
systemctl start rpcbind
systemctl enable nfs-server
systemctl start nfs-server
systemctl start rpc-statd
systemctl start nfs-idmapd
firewall-cmd --permanent --add-service=mountd
firewall-cmd --permanent --add-service=rpc-bind
firewall-cmd --permanent --add-service=nfs

# Enable ntpd
systemctl enable ntpd
systemctl start ntpd

# Enable httpd
semanage fcontext --add --type httpd_sys_content_t "/smartmet/www(/.*)?"
semanage fcontext --add --type httpd_sys_content_t "/smartmet/editor/smartalert(/.*)?"
semanage fcontext --add --type httpd_sys_content_t "/smartmet/cnf/httpd.conf"
restorecon -Rv /smartmet/www /smartmet/editor/smartalert /smartmet/cnf/httpd.conf
setsebool -P httpd_can_network_relay on
systemctl enable httpd
systemctl start httpd
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https

# Enable samba
systemctl enable smb
systemctl start smb
firewall-cmd --permanent --zone=public --add-service=samba
setsebool -P samba_export_all_rw=1

# Enable rsyncd
systemctl enable rsyncd
systemctl start rsyncd

# Enable yum-cron
systemctl enable yum-cron
systemctl start yum-cron

# Enable vsftpd
systemctl enable vsftpd 
systemctl start vsftpd
firewall-cmd --permanent --zone=public --add-service=ftp

# Enable access from FMI
firewall-cmd --permanent --zone=public --add-source=193.166.207.129
firewall-cmd --permanent --zone=public --add-source=193.166.223.108

# Reload firewalld
firewall-cmd --reload

cat > %{_sysconfdir}/samba/smb.conf << EOF
[global]
    workgroup = SAMBA
    unix extensions = No
    security = USER
    idmap config * : backend = tdb
    ntlm auth = yes

[smartmet]
    comment = SmartMet data
    path = /smartmet/editor
    wide links = Yes
    guest ok = Yes
    read only = No
    valid users = smartmet
EOF



%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/cron.d/smartmet.cron
%config(noreplace) %{_sysconfdir}/httpd/conf.d/smartmet.conf
%config(noreplace) %{_sysconfdir}/profile.d/smartmet.sh
%config(noreplace) %{_sysconfdir}/php.d/smartmet.ini
%config(noreplace) %{_sysconfdir}/ppp/peers/FMI
%config(noreplace) %{_sysconfdir}/ppp/chap-secrets.fmi
%config(noreplace) %{_sysconfdir}/fail2ban/jail.local
%config(noreplace) %{_sysconfdir}/fail2ban/action.d/firewallcmd-ipset.local
%config(noreplace) %{smartmetroot}/cnf/httpd.conf
%config(noreplace) %{smartmetroot}/cnf/smartmet.conf
%config(noreplace) %{smartmetroot}/cnf/palcrypt.conf
%attr(2775,smartmet,smartmet)  %dir %{smartmetroot}
%attr(-,smartmet,smartmet) %{smartmetroot}/*
%attr(2775,smartmet,apache)  %dir %{smartmetroot}/tmp/www

%changelog
* Wed Oct 30 2019 Mikko Rauhala <mikko.rauhala@fmi.fi> 18.10.30-2.el7.fmi
- add smartmet unixtools
* Wed Oct 30 2019 Mikko Rauhala <mikko.rauhala@fmi.fi> 18.10.30-1.el7.fmi
- add cift-utils, net-tools, certbot, se config for smartalert
* Wed Oct 10 2018 Mikko Rauhala <mikko.rauhala@fmi.fi> 18.10.10-1.el7.fmi
- added docker and traceroute
* Thu Nov 16 2017 Mikko Rauhala <mikko.rauhala@fmi.fi> 17.11.16-1.el7.fmi
- Fixed samba confs
* Thu Jun 29 2017 Mikko Rauhala <mikko.rauhala@fmi.fi> 17.6.29-1.el7.fmi
- Added samba confs
* Wed Jun 28 2017 Mikko Rauhala <mikko.rauhala@fmi.fi> 17.6.28-1.el7.fmi
- Changed %post to enable services
* Tue Jan 17 2017 Mikko Rauhala <mikko.rauhala@fmi.fi> 17.1.17-1.el7.fmi
- Changed requirements to correspond with current package naming
* Fri Aug 26 2016 Mikko Rauhala <mikko.rauhala@fmi.fi> 16.8.26-1.el7.fmi
- Removed postgresql requirement
* Wed Jun  3 2015 Santeri Oksman <santeri.oksman@fmi.fi> 15.6.3-1.el7.fmi
- Removed mail requirement
* Thu Nov 20 2014 Mikko Rauhala <mikko.rauhala@fmi.fi> 14.11.20-1.el6.fmi
- Initial build 
