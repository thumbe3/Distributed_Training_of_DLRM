node0=ushmal@c4130-110133
node1=ushmal@c4130-110233

####### Argumetmts ##########
# size of mlps tried 
# bt-mlp  512-256-64-16 and 256-128-64-16
# top-mlp 512-256-1 and 256-128-1
# 1 cluster mode (single vs cluster)
# 2 number of gpus
# 3 batch size

PATH1="~/yelp_dlrm/CS744Project/dlrm/" 

function start_cluster() {
    if [ -z $1 ]; then
        echo "Usage: start_cluster <cluster mode>"
    else
        echo "Create "
        echo "Copying the script to all the remote hosts."
        mkdir -p $7
        echo "The output is logged to output/outpuslog-i.out, where i = 0,..2 are the VM numbers."

        CMD="python3 dlrm_s_pytorch.py --arch-sparse-feature-size=16 --arch-mlp-bot="13-512-256-64-16" --arch-mlp-top="512-256-1" --data-generation=dataset --data-set=kaggle --raw-data-file=/users/ushmal/train.txt --processed-data-file=/users/ushmal/kaggleAdDisplayChallenge_processed.npz --loss-function=bce --round-targets=True --learning-rate=0.1 --rank 0 --master_ip 10.10.1.1  --test-freq 100001 --print-freq=1024 --print-time --use-gpu"

        ARGS="--ngpus $2 --async-mode $3 --mini-batch-size $4  --arch-interaction-op $5 --nepochs $6"

        if [ "$1" = "single" ]; then
        
            new_cmd="${CMD} --world-size=1 --master_ip 10.10.1.1 --rank 0  ${ARGS}"
            nohup ssh $node0 "killall -9 python3; cd $PATH1; $new_cmd"> $7/$1-$2-$3-$4-$5-0.out 2>&1&
        else
            new_cmd="${CMD} --world-size=2 --master_ip 10.10.1.1 --rank 0  ${ARGS}"
            nohup ssh $node0  "killall -9 python3; cd $PATH1; $new_cmd"> $7/$1-$2-$3-$4-$5-0.out 2>&1&
            new_cmd="${CMD} --world-size=2 --master_ip 10.10.1.1 --rank 1  ${ARGS}"
            nohup ssh $node1  "killall -9 python3; cd $PATH1; $new_cmd"> $7/$1-$2-$3-$4-$5-1.out 2>&1&
        fi
    fi
}
