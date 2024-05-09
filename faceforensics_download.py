#!/usr/bin/env python
"""Downloads FaceForensics++ and Deep Fake Detection public data release
Example usage:
    see -h or https://github.com/ondyari/FaceForensics
"""
# -*- coding: utf-8 -*-
import argparse
import os
import urllib.request
import tempfile
import time
import sys
import json
from tqdm import tqdm
from os.path import join

# URLs and filenames
FILELIST_URL = 'misc/filelist.json'
DEEPFEAKES_DETECTION_URL = 'misc/deepfake_detection_filenames.json'
DEEPFAKES_MODEL_NAMES = ['decoder_A.h5', 'decoder_B.h5', 'encoder.h5']

# Parameters
DATASETS = {
    'original_youtube_videos': 'misc/downloaded_youtube_videos.zip',
    'original_youtube_videos_info': 'misc/downloaded_youtube_videos_info.zip',
    'original': 'original_sequences/youtube',
    'DeepFakeDetection_original': 'original_sequences/actors',
    'Deepfakes': 'manipulated_sequences/Deepfakes',
    'DeepFakeDetection': 'manipulated_sequences/DeepFakeDetection',
    'Face2Face': 'manipulated_sequences/Face2Face',
    'FaceSwap': 'manipulated_sequences/FaceSwap',
    'NeuralTextures': 'manipulated_sequences/NeuralTextures'
}
ALL_DATASETS = ['original', 'DeepFakeDetection_original', 'Deepfakes',
                'DeepFakeDetection', 'Face2Face', 'FaceSwap',
                'NeuralTextures']
COMPRESSION = ['raw', 'c23', 'c40']
TYPE = ['videos', 'masks', 'models']
SERVERS = ['EU', 'EU2', 'CA']


def parse_args():
    parser = argparse.ArgumentParser(
        description='Downloads FaceForensics v2 public data release.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('output_path', type=str, help='Output directory.')
    parser.add_argument('-d', '--dataset', type=str, default='all',
                        help='Which dataset to download.',
                        choices=list(DATASETS.keys()) + ['all'])
    parser.add_argument('-c', '--compression', type=str, default='raw',
                        help='Compression degree.', choices=COMPRESSION)
    parser.add_argument('-t', '--type', type=str, default='videos',
                        help='File type.', choices=TYPE)
    parser.add_argument('-n', '--num_videos', type=int, default=None,
                        help='Number of videos to download.')
    parser.add_argument('--server', type=str, default='EU',
                        help='Server to download from.', choices=SERVERS)
    args = parser.parse_args()

    # URLs
    server = args.server
    if server == 'EU':
        server_url = 'http://canis.vc.in.tum.de:8100/'
    elif server == 'EU2':
        server_url = 'http://kaldir.vc.in.tum.de/faceforensics/'
    elif server == 'CA':
        server_url = 'http://falas.cmpt.sfu.ca:8100/'
    else:
        raise ValueError('Wrong server name. Choices: {}'.format(str(SERVERS)))
    args.tos_url = server_url + 'webpage/FaceForensics_TOS.pdf'
    args.base_url = server_url + 'v3/'
    args.deepfakes_model_url = server_url + 'v3/manipulated_sequences/' + \
                               'Deepfakes/models/'

    return args


def download_files(filenames, base_url, output_path):
    os.makedirs(output_path, exist_ok=True)
    for filename in tqdm(filenames):
        download_file(base_url + filename, join(output_path, filename))


def download_file(url, out_file):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    if not os.path.isfile(out_file):
        with urllib.request.urlopen(url) as response, open(out_file, 'wb') as out_f:
            out_f.write(response.read())
    else:
        tqdm.write('WARNING: skipping download of existing file ' + out_file)


def main(args):
    c_datasets = [args.dataset] if args.dataset != 'all' else ALL_DATASETS
    c_type = args.type
    c_compression = args.compression
    num_videos = args.num_videos
    output_path = args.output_path

    for dataset in c_datasets:
        dataset_path = DATASETS[dataset]

        if 'original_youtube_videos' in dataset:
            print('Downloading original youtube videos.')
            download_file(args.base_url + '/' + dataset_path,
                          out_file=join(output_path,
                                        'downloaded_videos.zip'))
            return

        print('Downloading {} of dataset "{}"'.format(c_type, dataset_path))

        if num_videos is not None and num_videos > 0:
            print('Downloading the first {} videos'.format(num_videos))

        file_pairs = json.loads(urllib.request.urlopen(args.base_url + '/' +
                                                       FILELIST_URL).read().decode("utf-8"))
        filelist = []
        for pair in file_pairs:
            filelist += pair

        if num_videos is not None and num_videos > 0:
            filelist = filelist[:num_videos]

        if c_type == 'videos':
            dataset_output_path = join(output_path, dataset_path, c_compression,
                                       c_type)
            print('Output path: {}'.format(dataset_output_path))
            filelist = [filename + '.mp4' for filename in filelist]
            download_files(filelist, args.base_url + '{}/{}/{}/'.format(
                dataset_path, c_compression, c_type), dataset_output_path)
        elif c_type == 'masks':
            dataset_output_path = join(output_path, dataset_path, c_type,
                                       'videos')
            print('Output path: {}'.format(dataset_output_path))
            filelist = [filename + '.mp4' for filename in filelist]
            download_files(filelist, args.base_url + '{}/{}/videos/'.format(
                dataset_path, 'masks'), dataset_output_path)
        else:
            if dataset != 'Deepfakes' and c_type == 'models':
                print('Models only available for Deepfakes. Aborting')
                return
            dataset_output_path = join(output_path, dataset_path, c_type)
            print('Output path: {}'.format(dataset_output_path))

            for folder in tqdm(filelist):
                folder_base_url = args.deepfakes_model_url + folder + '/'
                folder_dataset_output_path = join(dataset_output_path,
                                                  folder)
                download_files(DEEPFAKES_MODEL_NAMES, folder_base_url,
                               folder_dataset_output_path)


if __name__ == "__main__":
    args = parse_args()
    main(args)
