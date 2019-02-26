DELTA=$1

X1=0
for i in $(seq 300000); do 
    let "X1+=i+DELTA"; 
done; 
echo "$DELTA $X1"