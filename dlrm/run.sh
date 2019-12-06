source cluster_utils.sh
cluster_mode=("single", "cluster")
batch_size=( "128" "512")
interaction=("dot" "cat")
ngpus=(1 2)
async_mode=("True" "False")
epochs=10
dataset=$1

mkdir -p $dataset
for c_mode in "${cluster_mode[@]}"; do
for bsize in "${batch_size[@]}"; do
for inter in "${interaction[@]}"; do
for gpu in "${ngpus[@]}"; do
for s_mode in "${async_mode[@]}"; do
  num_line="$(grep -nr 'Finished the program' $dataset|wc -l)"
  new_num_line=num_line
  
  start_cluster $c_mode $gpu $s_mode $bsize $inter $epochs $dataset 
  if [ $c_mode == "single" ]; then
	  change=1
	  else
	  change=2
  fi


  while [ $(($new_num_line-$num_line)) -lt $change ];
  do
  sleep 1
  new_num_line="$(grep -nr 'Finished the program' $dataset|wc -l)"
  done

  git add $dataset
  git commit -m "Periodic commit for $dataset"
  git push
  echo "GIT PUSHED"
  
done
done
done
done
done

