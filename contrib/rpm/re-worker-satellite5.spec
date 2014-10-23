%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%global _pkg_name replugin
%global _src_name reworkersatellite5

Name: re-worker-satellite5
Summary: Winternewt Satellite5 Worker
Version: 0.1.0
Release: 2%{?dist}

Group: Applications/System
License: AGPLv3
Source0: %{_src_name}-%{version}.tar.gz
Url: https://github.com/rhinception/re-worker-satellite5

BuildArch: noarch
BuildRequires: python2-devel
BuildRequires: python-setuptools
Requires: re-worker
Requires: python-setuptools

%description
Worker capable of promoting RPMs between different channels in Red Hat
Satellite 5.

%prep
%setup -q -n %{_src_name}-%{version}

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --root=$RPM_BUILD_ROOT --record=re-worker-satellite5-files.txt

%files -f re-worker-satellite5-files.txt
%defattr(-, root, root)
%doc README.md LICENSE AUTHORS
%dir %{python2_sitelib}/%{_pkg_name}
%exclude %{python2_sitelib}/%{_pkg_name}/__init__.py*

%changelog
* Thu Oct 23 2014 Tim Bielawa <tbielawa@redhat.com> - 0.1.0-2
- Fix missing 'session key' parameter in mergePackages call

* Tue Oct 21 2014 Tim Bielawa <tbielawa@redhat.com> - 0.1.0-1
- Code-complete

* Mon Oct 20 2014 Tim Bielawa <tbielawa@redhat.com> - 0.0.1-1
- First release
