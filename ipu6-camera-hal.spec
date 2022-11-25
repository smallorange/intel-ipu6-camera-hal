%global commit cc0b859daeb5fdcdf23ed066ce0b6e313225fbb1
%global commitdate 20221112
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           ipu6-camera-hal
Summary:        Hardware abstraction layer for Intel IPU6
Version:        0.0
Release:        1.%{commitdate}git%{shortcommit}%{?dist}
License:        Apache-2.0

Source0: https://github.com/intel/%{name}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

BuildRequires:  systemd-rpm-macros
BuildRequires:  chrpath
BuildRequires:  ipu6-camera-bins
BuildRequires:  ipu6-camera-bins-devel
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  g++
BuildRequires:  expat-devel

Requires:       ipu6-camera-bins

ExclusiveArch:  x86_64

%description
ipu6-camera-hal provides the basic hardware access APIs for IPU6.

%package devel
Summary:        IPU6 header files for HAL.

%description devel
This provides the necessary header files for IPU6 HAL development.

Requires:       ipu6-camera-bins-devel

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
  mkdir -p %{buildroot}%{_datarootdir}/defaults/etc/$i
  mkdir -p %{buildroot}%{_includedir}/$i
  # lib
  cp -pr $i/build/lib* %{buildroot}%{_libdir}/$i
  chrpath --replace %{_libdir}/$i %{buildroot}%{_libdir}/$i/libcamhal.so
  # include
  cp -rp $i/include/* %{buildroot}%{_includedir}/$i
  # config
  cp -rp $i/config/linux/$i/* %{buildroot}%{_datarootdir}/defaults/etc/$i
  # udev
  cp -rp $i/config/linux/rules.d/* %{buildroot}/lib/udev/rules.d/
done

%files
%license LICENSE
%dir %{_libdir}/ipu6
%dir %{_libdir}/ipu6ep
%{_libdir}/ipu6/*.so*
%{_libdir}/ipu6/*.a
%dir %{_libdir}/ipu6ep
%{_libdir}/ipu6ep/*.so*
%{_libdir}/ipu6ep/*.a
%{_datarootdir}/defaults/etc/*
/lib/udev/rules.d/*

%files devel
%{_includedir}/ipu6
%{_includedir}/ipu6ep

%changelog
* Fri Nov 25 2022 Kate Hsuan <hpa@redhat.com> - 0.0-1.20221112gitcc0b859
- First commit