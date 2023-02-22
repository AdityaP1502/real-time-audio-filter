FFT_REPO_URL=https://github.com/AdityaP1502/fft-c
REPO_FOLDER="fft-c"
INSTALL_DIR=libs

if [ ! -d "$INSTALL_DIR" ];
then
	echo "Creating install directory"
	mkdir $INSTALL_DIR
fi

pushd $INSTALL_DIR

# now at INStALL DIR 
git clone $FFT_REPO_URL

pushd $REPO_FOLDER

# bulld the libs
source scripts/build.sh
if [ ! -d "../shared" ];
then
	echo "Creating install directory"
	mkdir ../shared
fi
cp libs/libconv.so libs/libitfft.so ../shared

popd
rm -rf $REPO_FOLDER
popd

if [ $? -eq 0 ]; then
	echo "OK"

else
	echo "FAIL"
	exit $?

fi

