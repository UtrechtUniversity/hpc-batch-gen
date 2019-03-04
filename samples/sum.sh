DELTA=$1
OUT_DIR=$2

X1=0
for i in $(seq 300000); do 
    let "X1+=i+DELTA"; 
done; 
echo "$DELTA $X1" > "${OUT_DIR}/sum_${DELTA}.dat"