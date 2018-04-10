
FILES=/01_preprocessed/*
for dir in $FILES;do
   a=${dir%%/}
   name=$(echo $a |  grep -o '[^/]*$')
   echo $name
done