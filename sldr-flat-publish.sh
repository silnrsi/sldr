#!/bin/sh

help () {
cat << EOT
$(basename $0) [-h | [-d] [-p] [-s]] TARGET
	TARGET may be of the form:
	  user@host -- for default document root based on hostname
	  user@host:docroot -- for a custom docroot
	  :/local/path -- for rsyncing to a local path 
	-h Print this help.
	-d Dry-run print the commands executed and what this would change on
	   the server.
	-s Skip flattening phase.
	-p Disable default sysops prefix to hostname.
EOT
}

PREFIX=sysops.
RSYNC_OPTS="-aP --no-p --no-g"

while getopts dhps f
do
  case $f in
    s)		SKIPFLAT=1;;
    d)		DRYRUN="--dry-run -i";;
    p)		PREFIX=;;
    \?|h)	help; exit 1;;
  esac
done
shift `expr $OPTIND - 1`

if [ $# -lt 1 ]
then
  help; exit 1
fi

SITE=${1%%:*}
DUCROOT=${1#*:}

USER=${SITE%%@*}
HOST=${SITE#*@}

if [ -z "$SITE" ]
then
  TARGET=${1#:}
else
  [ "$USER" = "$HOST" ] && USER= 
  [ "$SITE" = "$DUCROOT" ] && DUCROOT=/var/www/${HOST}/html
  TARGET=${USER}${USER:+@}${PREFIX}${HOST}:${DUCROOT}/cms
fi


shift 1

if [ -z "$SKIPFLAT" ]
then
  echo "Make flattened sldr"
  /usr/bin/time -v python3 bin/ldmlflatten -o flat -i sldr -a -A -g
  echo "Completed flattened sldr"

  echo "Make unflattened sldr"
  /usr/bin/time -v python3 bin/ldmlflatten -o unflat -i sldr -a -c -g
  echo "Completed unflatened sldr"
fi

echo "Uploading SLDR to $TARGET/local/ldml/sldr/sldr/"
rsync ${RSYNC_OPTS} ${DRYRUN} extras sldr $TARGET/local/ldml/sldr/
echo "Uploading flattened SLDR to $TARGET/sites/s/ldml-api/data/sldr/"
rsync ${RSYNC_OPTS} ${DRYRUN} --chmod=Dug=rwx flat unflat $TARGET/sites/s/ldml-api/data/sldr/
