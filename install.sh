#! /bin/sh

die () {
    while test -n "$1"
    do
	echo "$1"
	shift
    done
    echo "You will have to install this manually.  Sorry."
    exit 1
}

# First, find pkg-config
PKGCONFIG=`which pkg-config`
test -z "${PKGCONFIG}" && die "pkg-config not installed"

# Now, we need to know the directory where modules go
MODDIR=`$PKGCONFIG --variable=moddir znc`
test -z "${MODDIR}" && die "Can not determine module directory"

# Next, we get the data directory for modules
MODDATADIR=`$PKGCONFIG --variable=moddatadir znc`
test -z "${MODDATADIR}" && die "Can not determine module directory"

# Now (yeah, it's probably late, but still) confirm modpython support
test -f "${MODDIR}/modpython.so" || die "Python support doesn't seem to be available in this ZNC installation"

# Finally, we can do the installation
cp filter.py "${MODDIR}"
mkdir -p "${MODDATADIR}/modules/filter/tmpl"
cp index.tmpl "${MODDATADIR}/modules/filter/tmpl"
