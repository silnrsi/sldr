#!/bin/sh

help () {
cat << EOT
$(basename $0) [-h | [-d] [-p] [-s] -S] TARGET
	TARGET may be of the form:
	  user@host -- for default document root based on hostname
	  user@host:docroot -- for a custom docroot
	  :/local/path -- for rsyncing to a local path 
	-h Print this help.
	-d Dry-run print the commands executed and what this would change on
	   the server.
	-s Skip flattening phase.
	-p Disable default sysops prefix to hostname.
	-t Time the flatten and unflatten commands
	-S Upload to staging area.
	-I Iana file to upload
	-L langtags.txt to upload
EOT
}

STAGE=sldr
PREFIX=sysops.
RSYNC_OPTS="-aP --no-p --no-g --no-t --compress --del"
TARGET_SLDR="sldr"

while getopts "dhpstSI:L:" f
do
  case $f in
    s)		SKIPFLAT=1;;
    d)		DRYRUN="--dry-run -i";;
    p)		PREFIX=;;
    t)    TIMECMD="/usr/bin/time -v";;
    S)    STAGE=sldr-staging;;
    I)    IANA=${OPTARG};;
    L)    LANGTAGS=${OPTARG};;
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
  rm -fr flat
  ${TIMECMD} python3 bin/ldmlflatten -o flat -i sldr -a -A -g
  echo "Completed flattened sldr"

  echo "Make unflattened sldr"
  rm -fr unflat
  ${TIMECMD} python3 bin/ldmlflatten -o unflat -i sldr -a -c -g
  echo "Completed unflatened sldr"
fi

echo "Uploading SLDR to $TARGET/local/ldml/$STAGE/sldr/"
rsync ${RSYNC_OPTS} ${DRYRUN} extras sldr $TARGET/local/ldml/$STAGE/
echo "Uploading flattened SLDR to $TARGET/sites/s/ldml-api/data/$STAGE/"
rsync ${RSYNC_OPTS} ${DRYRUN} --chmod=Dug=rwx flat unflat $TARGET/sites/s/ldml-api/data/$STAGE/
if [ -n "$IANA" ]
then
  rsync ${RSYNC_OPTS} ${DRYRUN} $IANA $TARGET/sites/s/ldml-api/data/IanaRegistry.txt
fi
if [ -n "$LANGTAGS" ]
then
  rsync ${RSYNC_OPTS} ${DRYRUN} $LANGTAGS $TARGET/sites/s/ldml-api/data/langtags.txt
fi


