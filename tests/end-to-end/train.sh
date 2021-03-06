#!/bin/bash

#
# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
source $utils_dir/utils.sh
echo ""
echo "Train "
echo ""
python $root_dir/main.py --train \
    --train_files $out_dir/train_data.h5 \
    --val_files $out_dir/val_data.h5 \
    --out_home $out_dir --label model \
    --checkpoint_fname checkpoint.pth.tar \
    --distributed --epochs 1
# Training is not deterministic, so we are not comparing results.
check_status $? "Training run not succesful!"
