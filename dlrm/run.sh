source cluster_utils.sh
cluster_mode=("cluster" "single" )
batch_size=("32" "64" "128" "512")
interaction=("dot" "cat")
ngpus=(2 3)
async_mode=("True" "False")
epochs=10



for c_mode in "${cluster_mode[@]}"; do
for bsize in "${batch_size[@]}"; do
for inter in "${interaction[@]}"; do
for gpu in "${ngpus[@]}"; do
for s_mode in "${async_mode[@]}"; do
  num_line="$(grep -nr 'Finished the program' output|wc -l)"
  new_num_line=num_line
  
  start_cluster $c_mode $gpu $s_mode $bsize $inter $epochs
  if [ $c_mode == "single" ]; then
	  change=1
	  else
	  change=2
  fi


  while [ $(($new_num_line-$num_line)) -lt $change ];
  do
  sleep 1
  new_num_line="$(grep -nr 'Finished the program' output|wc -l)"
  done
  killall -9 python3

  git add output
  git commit -m "Periodic commit"
  git push
  echo "GIT PUSHED"
  break
  
done
 break
done
 break
done
 break
done
break
done

