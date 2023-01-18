%global commit cc0b859daeb5fdcdf23ed066ce0b6e313225fbb1
%global commitdate 20221112
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           ipu6-camera-hal
Summary:        Hardware abstraction layer for Intel IPU6
URL:            https://github.com/intel/ipu6-camera-hal
Version:        0.0
Release:        3.%{commitdate}git%{shortcommit}%{?dist}
License:        Apache-2.0

Source0:        https://github.com/intel/%{name}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Source1:        60-ipu6-tgl-adl.rules
Source2:        ipu-setlink

BuildRequires:  systemd-rpm-macros
BuildRequires:  chrpath
BuildRequires:  ipu6-camera-bins
BuildRequires:  ipu6-camera-bins-devel
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  g++
BuildRequires:  expat-devel

ExclusiveArch:  x86_64

Requires:       ipu6-camera-bins

%description
ipu6-camera-hal provides the basic hardware access APIs for IPU6.

%package devel
Summary:        IPU6 header files for HAL.
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       ipu6-camera-bins-devel

%description devel
This provides the necessary header files for IPU6 HAL development.

%prep

%setup -q -c
cp -rp %{name}-%{commit} ipu6
cp -rp %{name}-%{commit} ipu6ep

%build
# Build ipu6
cd ipu6
cp LICENSE ../
export PKG_CONFIG_PATH=/usr/lib64/ipu6/pkgconfig/
mkdir -p ./build/out/install/usr && cd ./build/
cmake -DCMAKE_BUILD_TYPE=Release \
-DIPU_VER=ipu6 \
-DENABLE_VIRTUAL_IPU_PIPE=OFF \
-DUSE_PG_LITE_PIPE=ON \
-DUSE_STATIC_GRAPH=OFF \
-DCMAKE_INSTALL_PREFIX=/usr ..

make -j`nproc`

# Build ipu6ep
cd ../../ipu6ep
export PKG_CONFIG_PATH=/usr/lib64/ipu6ep/pkgconfig/
mkdir -p ./build/out/install/usr && cd ./build/
cmake -DCMAKE_BUILD_TYPE=Release \
-DIPU_VER=ipu6ep \
-DENABLE_VIRTUAL_IPU_PIPE=OFF \
-DUSE_PG_LITE_PIPE=ON \
-DUSE_STATIC_GRAPH=OFF \
-DCMAKE_INSTALL_PREFIX=/usr ..

make -j`nproc`

%install
mkdir -p %{buildroot}/lib/udev/rules.d/
for i in ipu6 ipu6ep; do
  mkdir -p %{buildroot}%{_libdir}/$i
  mkdir -p %{buildroot}%{_libdir}/$i/pkgconfig
  mkdir -p %{buildroot}%{_datarootdir}/defaults/etc/$i
  mkdir -p %{buildroot}%{_includedir}/$i
  # lib
  cp -pr $i/build/libcamhal.a %{buildroot}%{_libdir}/$i/libcamhal.a
  cp -pr $i/build/libcamhal.so %{buildroot}%{_libdir}/$i/libcamhal.so
  chrpath --replace %{_libdir}/$i %{buildroot}%{_libdir}/$i/libcamhal.so
  # include
  cp -rp $i/include/* %{buildroot}%{_includedir}/$i
  # config
  cp -rp $i/config/linux/$i/* %{buildroot}%{_datarootdir}/defaults/etc/$i
  #pkgconfig
  cp -pr $i/libcamhal.pc %{buildroot}%{_libdir}/$i/pkgconfig
  sed -i \
    -e "s|libdir=\${prefix}/lib64|libdir=%{_libdir}/$i|g" \
    -e "s|includedir=\${prefix}/include/libcamhal|includedir=%{_includedir}/$i|g" \
    %{buildroot}%{_libdir}/$i/pkgconfig/*.pc
done

# symbolic link is used to resolve the library name conflict. 
ln -sf %{_rundir}/libcamhal.so %{buildroot}%{_libdir}/libcamhal.so
ln -sf %{_rundir}/camera %{buildroot}%{_datadir}/defaults/etc/camera

# udev
mkdir -p %{buildroot}/usr/lib/udev/rules.d
cp -rp %{SOURCE1} %{buildroot}/usr/lib/udev/rules.d
install -p -D -m 0755 %{SOURCE2} %{buildroot}/usr/lib/udev

%files
%license LICENSE
%dir %{_libdir}/ipu6
%dir %{_libdir}/ipu6ep
%{_libdir}/ipu6/*.so*
%{_libdir}/ipu6ep/*.so*
%{_libdir}/libcamhal.so
%{_datarootdir}/defaults/etc/*
/usr/lib/udev/rules.d/*
/usr/lib/udev/*

%files devel
%dir %{_includedir}/ipu6
%dir %{_includedir}/ipu6ep
%{_includedir}/ipu6/*
%{_includedir}/ipu6ep/*
%{_libdir}/ipu6/*.a
%{_libdir}/ipu6ep/*.a*
%dir %{_libdir}/ipu6/pkgconfig
%dir %{_libdir}/ipu6ep/pkgconfig
%{_libdir}/ipu6/pkgconfig/*
%{_libdir}/ipu6ep/pkgconfig/*

%post
/usr/bin/udevadm control --reload
/usr/bin/udevadm trigger

%changelog
* Tue Jan 17 2023 Kate Hsuan <hpa@redhat.com> - 0.0-3.20221112gitcc0b859
- Add symbolic link for camera configuration files

* Fri Nov 25 2022 Kate Hsuan <hpa@redhat.com> - 0.0-2.20221112gitcc0b859
- push udev rules
- format and style fixes

* Fri Nov 25 2022 Kate Hsuan <hpa@redhat.com> - 0.0-1.20221112gitcc0b859
- First commit
