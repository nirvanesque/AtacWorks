#
# Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import argparse

def check_dependence(
    arg1, arg2, parser, err_msg="Argument mutual inclusive test failed."):
    if arg1 and not arg2:
        parser.error(err_msg)

def check_mutual_exclusive(
    arg1, arg2, parser, err_msg="Argument mutual exclusive test failed."):
    if arg1 and arg2:
        parser.error(err_msg)

def parse_args():
    parser = argparse.ArgumentParser(description='DenoiseNet training script.')

    # General flags
    parser.add_argument('--model', type=str, help='model type', choices=(
        'unet', 'resnet', 'conv', 'linear', 'logistic', 'fc2', 'fc3'), default='unet')
    parser.add_argument('--clip_grad', type=float, default=0.,
                        help='Add grad clipping (at 1.0)? For bad/extreme batches?')
    parser.add_argument('--lr', type=float,
                        help='learning rate', default=0.0001)
    parser.add_argument('--epochs', type=int,
                        help='Number of epochs', default=5)
    parser.add_argument('--afunc', type=str,
                        help='activation', default='relu')
    parser.add_argument('--bn', action='store_true', help='batch norm')
    parser.add_argument('--mse_weight', type=float,
                        help='relative weight of mse loss', default=0.001)
    parser.add_argument('--pearson_weight', type=float,
                        help='relative weight of pearson loss', default=1)

    # For conv or resnet models
    parser.add_argument('--nfilt', type=int,
                        help='number of filters', default=15)
    parser.add_argument('--dil', type=int, help='dilation', default=5)
    parser.add_argument('--width', type=int, help='width', default=50)

    # For resnet model
    parser.add_argument('--nblocks', type=int,
                        help='number of regression blocks for resnet', default=5)
    parser.add_argument('--nblocksc', type=int,
                        help='number of classification blocks for resnet', default=2)

    # For conv model
    parser.add_argument('--field', type=int,
                        help='receptive field', default=1000)
    parser.add_argument('--nconv', type=int,
                        help='number of conv layers for conv model', default=5)


#=========================================================================================
    # experiment args
    parser.add_argument('--label', type=str, default='AtacWorks',
        help='label of the experiment; used for naming output folder')
    parser.add_argument('--out_home', type=str, default='./Cache',
        help='parent directory for the experiment folder')
    parser.add_argument('--train', action='store_true',
        help='training; preempt --infer')
    parser.add_argument('--infer', action='store_true',
        help='inference')
    parser.add_argument('--resume', action='store_true',
        help='resume training')
    parser.add_argument('--eval', action='store_true',
        help='evaluation: inference + result dumping + metrics evaluation')
    parser.add_argument('--infer_files', type=str, default="",
        help='list of data files in the form of [file1, file2, ...];'
             'or a single path to a folder of files')

    parser.add_argument('--weights_path', type=str, default="",
        help="checkpoint path to load the model from for inference or resume training")
    parser.add_argument('--result_fname', type=str, default='infer_results.h5',
        help='filename of the inference results')

    # dataset args
    parser.add_argument('--sample_rate', type=float, default=0.1,
        help='if downsampling, dynamic downsample rate')

    # training args
    parser.add_argument('--task', default='regression', choices=['regression', 'classification', 'both'],
        help='Task can be regression or classification or both. (default: %(default)s)')
    parser.add_argument('--train_files', type=str, default="",
        help='list of data files in the form of [file1, file2, ...];'
             'or a single path to a folder of files')
    parser.add_argument('--print_freq', type=int, default=10,
        help="Logging frequency")
    parser.add_argument('--bs', type=int, default=3,
        help="meta batch_size")
    parser.add_argument('--num_workers', type=int, default=1,
        help="number of workers for dataloader")
    parser.add_argument('--checkpoint_fname', type=str, default="",
        help="checkpoint filename to save the model")
    parser.add_argument('--save_freq', type=int, default=5,
                        help="model checkpoint saving frequency")

    # validation args
    parser.add_argument('--val_files', type=str, default="",
        help='list of data files in the form of [file1, file2, ...];'
             'or a single path to a folder of files')
    parser.add_argument('--eval_freq', type=int, default=2,
        help="evaluation frequency")
    parser.add_argument('--threshold', type=float, default=0.5,
        help="threshold for classification metrics")

    # dist-env args
    parser.add_argument('--gpu', default=0, type=int,
        help='GPU id to use; preempted by --distributed which uses all available gpus ')
    parser.add_argument('--distributed', action='store_true',
        help='Do distributed training across all available gpus on the node')
    parser.add_argument('--dist-url', default='tcp://127.0.0.1:4321', type=str,
        help='url used to set up distributed training')
    parser.add_argument('--dist-backend', default='nccl', type=str,
        help='distributed backend')

    # debug
    parser.add_argument('--debug', action='store_true',
        help='Enable debug prints')

    args = parser.parse_args()

    check_mutual_exclusive(args.train, args.infer, parser, "--train and --infer are mutual exclusive")
    check_mutual_exclusive(args.train, args.eval, parser, "--train and --eval are mutual exclusive")
    check_mutual_exclusive(args.infer, args.eval, parser, "--infer and --eval are mutual exclusive")
    # check_mutual_exclusive(args.infer, args.distributed, parser, "--infer and --distributed are mutual exclusive")

    check_dependence(args.train, args.train_files,  parser, "--train requires --train_files")
    check_dependence(args.train, args.val_files,    parser, "--train requires --val_files")
    check_dependence(args.train, args.checkpoint_fname, parser, "--train requires --checkpoint_fname")

    check_dependence(args.infer, args.infer_files,  parser, "--infer requires --infer_files")
    check_dependence(args.infer, args.weights_path, parser, "--infer requires --weights_path")

    check_dependence(args.eval, args.val_files,  parser, "--eval requires --val_files")
    check_dependence(args.eval, args.weights_path, parser, "--eval requires --weights_path")

    return args

# args = parse_args()
# # if args.train and (not args.train_files):
# #     parser.error("--train requires --train_files")

# # print(locals())