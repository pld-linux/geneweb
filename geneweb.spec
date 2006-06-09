# TODO:
# - better logrorate (create logs with proper rights)
# - check if it even works...
# - fix init script to be more granular (each daemon should have own status)
# - move gwd.arg to /etc
Summary:	Genealogy software with a Web interface
Summary(de):	Eine genealogische Software mit einem Web-Interface
Summary(fr):	Un logiciel de généalogie doté d'une interface Web
Summary(nl):	Een genealogisch programma met een WWW-interface
Summary(pl):	Oprogramowanie do genealogii z interfejsem WWW
Summary(sv):	Ett genealogi program med ett webbinterface
Name:		geneweb
Version:	4.09
Release:	0.6
Group:		Applications/Databases
License:	GPL v2
Source0:	ftp://ftp.inria.fr/INRIA/Projects/cristal/geneweb/Src/%{name}-%{version}.tar.gz
# Source0-md5:	342eb7dd34bf82fb7e3a89de0379405f
Source1:	%{name}.init
URL:		http://cristal.inria.fr/~ddr/GeneWeb/
BuildRequires:	ocaml
BuildRequires:	ocaml-camlp4
BuildRequires:	rpmbuild(macros) >= 1.202
PreReq:		rc-scripts
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(post):	fileutils
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Provides:	group(geneweb)
Provides:	user(geneweb)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
GeneWeb is a genealogy software with a Web interface. It can be used
off-line or as a Web service.

%description -l de
GeneWeb ist eine genealogische Software mit einem Web-Interface. Sie
kann off-line oder als ein Web-Service genutzt werden.

%description -l fr
GeneWeb est un logiciel de généalogie doté d'une interface Web. Il
peut être utilisé non connecté au réseau ou comme un service Web.

%description -l nl
GeneWeb is een genealogisch programma met een WWW-interface, dat kan
gebruikt worden op computers met of zonder permanente verbinding met
het Internet.

%description -l pl
GeneWeb to oprogramowanie do genealogii z interfejsem WWW. Mo¿na go
u¿ywaæ offline albo jako us³uga sieciowa.

%description -l sv
GeneWeb är ett genealogi program med ett webbinterface. Det kan
användas nedkopplad eller som en webbtjänst.

%prep
%setup -q

%build
%{__make} opt
%{__make} distrib

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/var/{log,lib/%{name}},%{_sysconfdir}/%{name},/etc/{rc.d/init.d,logrotate.d}} \
	$RPM_BUILD_ROOT%{_datadir}/%{name}/setup/lang

%{__make} install \
	PREFIX=$RPM_BUILD_ROOT%{_prefix} \
	MANDIR=$RPM_BUILD_ROOT%{_mandir}/man1 \
	DOCDIR=$RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

# move configs into better place:
mv -f $RPM_BUILD_ROOT%{_datadir}/%{name}%{_sysconfdir}/* $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
rm -rf $RPM_BUILD_ROOT%{_datadir}/%{name}%{_sysconfdir}
ln -sf %{_sysconfdir}/%{name} $RPM_BUILD_ROOT%{_datadir}/%{name}%{_sysconfdir}
# install gwsetup:
install setup/gwsetup $RPM_BUILD_ROOT%{_bindir}
install setup/lang/*.htm $RPM_BUILD_ROOT%{_datadir}/%{name}/setup/lang
install setup/intro.txt $RPM_BUILD_ROOT%{_datadir}/%{name}/setup

# init-script (included is ugly...):
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install rpm/geneweb-logrotate $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}

# logs:
touch $RPM_BUILD_ROOT/var/log/gwd.log
touch $RPM_BUILD_ROOT/var/log/gwsetup.log

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 129 geneweb
%useradd -u 129 -d /var/lib/geneweb -s /bin/false -c "Genealogy Software" -g geneweb geneweb

%post
/sbin/chkconfig --add %{name}
touch /var/log/gwd.log /var/log/gwsetup.log
chown %{name}:%{name} /var/log/gwd.log /var/log/gwsetup.log
chmod 640 /var/log/{gwd.log,gwsetup.log}
if [ -f %{_var}/lock/subsys/%{name} ]; then
	/etc/rc.d/init.d/%{name} restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/%{name} start\" to start %{name} daemon."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f %{_var}/lock/subsys/%{name} ]; then
		/etc/rc.d/init.d/%{name} stop 1>&2
	fi
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
	%userremove geneweb
	%groupremove geneweb
fi

%files
%defattr(644,root,root,755)
%{_docdir}/%{name}-%{version}
%dir %{_sysconfdir}/%{name}
%attr(644,geneweb,geneweb) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/*
%{_datadir}/%{name}%{_sysconfdir}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/logrotate.d/%{name}
%attr(755,root,root) %{_bindir}/*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/images
%{_datadir}/%{name}/images/*.gif
%{_datadir}/%{name}/images/*.jpg
%dir %{_datadir}/%{name}/lang
%{_datadir}/%{name}/lang/*.txt
%dir %{_datadir}/%{name}/setup
%{_datadir}/%{name}/setup/*.txt
%dir %{_datadir}/%{name}/setup/lang
%{_datadir}/%{name}/setup/lang/*.htm
%{_mandir}/man1/*
%attr(644,geneweb,geneweb) %ghost /var/log/*.log
%attr(750,geneweb,geneweb) %dir /var/lib/geneweb
