cd vendor
mkdir node
mkdir tmp
tar -xvf ./node-v16.13.1-darwin-x64.tar.gz -C tmp
for dir in tmp/*; do
    mv $dir/* node
done
rm -r tmp
cd ..
