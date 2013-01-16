Summary: Initial system configuration utility
Name: inital-setup
URL: http://fedoraproject.org/wiki/FirstBoot
Version: 0.1
Release: 1%{?dist}
BuildArch: noarch

# This is a Red Hat maintained package which is specific to
# our distribution.
#
# The source is thus available only from within this SRPM
# or via direct git checkout:
# git clone http://
Source0: %{name}-%{version}.tar.gz

License: GPLv2+
Group: System Environment/Base
ExclusiveOS: Linux
BuildRequires: gettext
BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: python-nose
BuildRequires: systemd-units
BuildRequires: gtk3-devel
BuildRequires: gtk-doc
BuildRequires: gobject-introspection-devel
BuildRequires: glade-devel
BuildRequires: pygobject3
BuildRequires: python-babel
Requires: gtk3
Requires: python
Requires: anaconda >= 18.40
Requires(post): systemd-units systemd-sysv chkconfig
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires: firstboot(windowmanager)
Requires: libreport-python

%global debug_package %{nil}

%description
The inital-setup utility runs after installation.  It guides the user through
a series of steps that allows for easier configuration of the machine.

%prep
%setup -q

# remove upstream egg-info
rm -rf *.egg-info

%build
%{__python} setup.py build
%{__python} setup.py compile_catalog -D %{name} -d locale

%check
%{__python} setup.py nosetests

%install
rm -rf ${buildroot}

%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
%find_lang %{name}

%post
if [ $1 -ne 2 -a ! -f /etc/sysconfig/inital-setup ]; then
  platform="$(arch)"
  if [ "$platform" = "s390" -o "$platform" = "s390x" ]; then
    echo "RUN_INITAL_SETUP=YES" > /etc/sysconfig/inital-setup
  else
    %systemd_post inital-setup-graphical.service
    %systemd_post inital-setup-text.service
    %systemd_post inital-setup-xserver.service
  fi
fi

%preun
if [ $1 = 0 ]; then
  rm -rf /usr/share/inital-setup/*.pyc
  rm -rf /usr/share/inital-setup/modules/*.pyc
fi
%systemd_preun inital-setup-graphical.service
%systemd_preun inital-setup-text.service
%systemd_preun inital-setup-xserver.service

%postun
%systemd_postun_with_restart inital-setup-graphical.service
%systemd_postun_with_restart inital-setup-text.service
%systemd_postun_with_restart inital-setup-xserver.service

%files -f %{name}.lang
%defattr(-,root,root,-)
%dir %{_datadir}/inital-setup/
%dir %{_datadir}/inital-setup/modules/
%{python_sitelib}/*
%{_bindir}/inital-setup
%{_datadir}/inital-setup/modules/*

/lib/systemd/system/inital-setup-graphical.service
/lib/systemd/system/inital-setup-text.service
/lib/systemd/system/inital-setup-xserver.service

%ifarch s390 s390x
%dir %{_sysconfdir}/profile.d
%{_sysconfdir}/profile.d/inital-setup.sh
%{_sysconfdir}/profile.d/inital-setup.csh
%endif


%changelog
* Tue Nov 06 2012 Martin Sivak <msivak@redhat.com> 0.1-1
- Inital release
