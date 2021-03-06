%define theme sailfish-default

%{!?qtc_qmake:%define qtc_qmake %qmake}
%{!?qtc_qmake5:%define qtc_qmake5 %qmake5}
%{!?qtc_make:%define qtc_make make}
%{?qtc_builddir:%define _builddir %qtc_builddir}

Name:       patchmanager

Summary:    Patchmanager allows you to manage Sailfish OS patches
Version:    3.0.1
Release:    1
Group:      Qt/Qt
License:    TODO
URL:        https://github.com/sailfishos-patches/patchmanager
Source0:    %{name}-%{version}.tar.bz2
Requires:   unzip
Requires:   patch
Conflicts:  jolla-settings-%{name}
Obsoletes:  jolla-settings-%{name}
Conflicts:  %{name}-ui
Obsoletes:  %{name}-ui
Conflicts:  prepatch
Obsoletes:  prepatch
BuildRequires:  pkgconfig(Qt5Core)
BuildRequires:  pkgconfig(Qt5DBus)
BuildRequires:  pkgconfig(Qt5Qml)
BuildRequires:  pkgconfig(Qt5Quick)
BuildRequires:  pkgconfig(mlite5)
BuildRequires:  pkgconfig(sailfishapp) >= 0.0.10
BuildRequires:  sailfish-svg2png >= 0.1.5
BuildRequires:  pkgconfig(nemonotifications-qt5)
BuildRequires:  qt5-qtdeclarative-devel-tools
BuildRequires:  pkgconfig(libsystemd-journal)
BuildRequires:  qt5-qttools-linguist
BuildRequires:  pkgconfig(rpm)

%description
patchmanager allows managing Sailfish OS patches
on your device easily.

%prep
%setup -q -n %{name}-%{version}

%build

%qtc_qmake5 "PROJECT_PACKAGE_VERSION=%{version}"
%qtc_make %{?_smp_mflags}

%install
rm -rf %{buildroot}

%qmake5_install

/usr/lib/qt5/bin/qmlplugindump -v -noinstantiate -nonrelocatable org.SfietKonstantin.patchmanager 2.0 %{buildroot}%{_libdir}/qt5/qml > %{buildroot}%{_libdir}/qt5/qml/org/SfietKonstantin/%{name}/plugin.qmltypes |:
sed -i 's#%{buildroot}##g' %{buildroot}%{_libdir}/qt5/qml/org/SfietKonstantin/%{name}/plugin.qmltypes

mkdir -p %{buildroot}/lib/systemd/system/multi-user.target.wants/
ln -s ../dbus-org.SfietKonstantin.patchmanager.service %{buildroot}/lib/systemd/system/multi-user.target.wants/

mkdir -p %{buildroot}/lib/systemd/system/timers.target.wants/
ln -s ../checkForUpdates-org.SfietKonstantin.patchmanager.timer %{buildroot}/lib/systemd/system/timers.target.wants/

mkdir -p %{buildroot}/usr/lib/systemd/user/lipstick.service.wants/
ln -s ../lipstick-patchmanager.service %{buildroot}/usr/lib/systemd/user/lipstick.service.wants/

mkdir -p %{buildroot}%{_datadir}/%{name}/patches

%pre
export NO_PM_PRELOAD=1
case "$*" in
1)
echo Installing package
;;
2)
echo Upgrading package
// unapply patches if pm2 is installed
if [ "$(rpm -q --qf "%{VERSION}" patchmanager | head -c 1)" == "2" ]
then
    if [ ! -d /var/lib/patchmanager/ausmt/patches/ ]
    then
        exit 0
    fi
    if [ "$(ls -A /var/lib/patchmanager/ausmt/patches/)" ]
    then
        echo "Unapply all patches before upgrade!"
        exit 1
    fi
fi
;;
*) echo case "$*" not handled in pre
esac

%preun
export NO_PM_PRELOAD=1
case "$*" in
0)
echo Uninstalling package
#if [ -d /var/lib/patchmanager/ausmt/patches/sailfishos-patchmanager-unapplyall ]; then
#/usr/sbin/patchmanager -u sailfishos-patchmanager-unapplyall || true
#fi

systemctl stop dbus-org.SfietKonstantin.patchmanager.service
;;
1)
echo Upgrading package
;;
*) echo case "$*" not handled in preun
esac

%post
export NO_PM_PRELOAD=1
case "$*" in
1)
echo Installing package
#/usr/sbin/patchmanager -a sailfishos-patchmanager-unapplyall || true
;;
2)
echo Upgrading package
#/usr/sbin/patchmanager -a sailfishos-patchmanager-unapplyall || true
;;
*) echo case "$*" not handled in post
esac
if grep libpreloadpatchmanager /etc/ld.so.preload > /dev/null; then
    echo "Preload already exists"
else
    echo /usr/lib/libpreloadpatchmanager.so >> /etc/ld.so.preload
fi
/sbin/ldconfig
dbus-send --system --type=method_call \
--dest=org.freedesktop.DBus / org.freedesktop.DBus.ReloadConfig
systemctl daemon-reload
systemctl-user daemon-reload
systemctl restart dbus-org.SfietKonstantin.patchmanager.service
systemctl restart checkForUpdates-org.SfietKonstantin.patchmanager.timer

%postun
export NO_PM_PRELOAD=1
case "$*" in
0)
echo Uninstalling package
sed -i "/libpreloadpatchmanager/ d" /etc/ld.so.preload
rm -rf /tmp/patchmanager |:
rm -f /tmp/patchmanager-socket |:
;;
1)
echo Upgrading package
;;
*) echo case "$*" not handled in postun
esac
/sbin/ldconfig
dbus-send --system --type=method_call \
--dest=org.freedesktop.DBus / org.freedesktop.DBus.ReloadConfig
systemctl daemon-reload
systemctl-user daemon-reload

%files
%defattr(-,root,root,-)
%{_bindir}/%{name}-dialog
%{_sbindir}/%{name}
%dir %{_datadir}/%{name}/patches
%{_datadir}/%{name}/tools
%{_datadir}/dbus-1/
%{_sysconfdir}/dbus-1/system.d/
/lib/systemd/system/dbus-org.SfietKonstantin.patchmanager.service
/lib/systemd/system/multi-user.target.wants/dbus-org.SfietKonstantin.patchmanager.service
/lib/systemd/system/checkForUpdates-org.SfietKonstantin.patchmanager.service
/lib/systemd/system/checkForUpdates-org.SfietKonstantin.patchmanager.timer
/lib/systemd/system/timers.target.wants/checkForUpdates-org.SfietKonstantin.patchmanager.timer
%{_sharedstatedir}/environment/patchmanager/10-dbus.conf
#%{_datadir}/patchmanager/patches/sailfishos-patchmanager-unapplyall/patch.json
#%{_datadir}/patchmanager/patches/sailfishos-patchmanager-unapplyall/unified_diff.patch
%{_libdir}/systemd/user/dbus-org.SfietKonstantin.patchmanager.service
%{_libdir}/systemd/user/lipstick-patchmanager.service
%{_libdir}/systemd/user/lipstick.service.wants/lipstick-patchmanager.service
%{_libdir}/libpreload%{name}.so

%attr(0755,root,root-) %{_libexecdir}/pm_apply
%attr(0755,root,root-) %{_libexecdir}/pm_unapply

%{_libdir}/qt5/qml/org/SfietKonstantin/%{name}
%{_datadir}/%{name}/data
%{_datadir}/translations
%{_datadir}/jolla-settings/pages/%{name}
%{_datadir}/jolla-settings/entries/%{name}.json
%{_datadir}/%{name}/icons/icon-m-patchmanager.png
%attr(644,nemo,nemo) %ghost /home/nemo/.config/patchmanager2.conf

%{_datadir}/themes/%{theme}/meegotouch/z1.0/icons/*.png
%{_datadir}/themes/%{theme}/meegotouch/z1.25/icons/*.png
%{_datadir}/themes/%{theme}/meegotouch/z1.5/icons/*.png
%{_datadir}/themes/%{theme}/meegotouch/z1.5-large/icons/*.png
%{_datadir}/themes/%{theme}/meegotouch/z1.75/icons/*.png
%{_datadir}/themes/%{theme}/meegotouch/z2.0/icons/*.png
