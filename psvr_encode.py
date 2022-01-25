import os
import sys
import time
import json
import argparse
import subprocess

from tqdm import tqdm
from datetime import datetime

prob_results = []


def probe_file(input_path):
    p = subprocess.run(['ffprobe', input_path], capture_output=True)
    p = p.stderr.decode().split('\r\n')
    p = [x.strip() for x in p if ('Stream' in x) or ('Duration' in x)]
    if len(p) > 0:
        p.append(input_path)
        global prob_results
        prob_results.append(p)


def probe_dir(dir_path):
    dir_list = [os.path.join(dir_path, p) for p in os.listdir(dir_path)]
    for file in dir_list:
        probe_file(file)


def print_probe_result():
    print(f'\n################# Probe result #################')
    global prob_results
    if len(prob_results) == 0:
        print('No available files!')
        sys.exit()
    else:
        print(f'File number: {len(prob_results)}')
    for result in prob_results:
        print(f'\n{result[-1]}')
        for info in result[:len(result) - 1]:
            print(f'\t{info}')
    print(f'\n################################################\n')


def encode_file(ffmpeg_cmd, verbose):
    global args, data
    for arg in data.keys():
        ffmpeg_cmd.append(arg)
        ffmpeg_cmd.append(data[arg])

    output_postfix = '_' + args.platform + '_' + args.degrees + '_' + args.type + '.mp4'

    output_path = ffmpeg_cmd[2].split('.')[0] + output_postfix
    if os.path.exists(output_path):
        os.remove(output_path)

    ffmpeg_cmd.append(output_path)

    tic = time.perf_counter()

    ffmpeg_process = subprocess.Popen(ffmpeg_cmd,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      universal_newlines=True)
    set_progress_bar = False
    total_seconds = 0
    last_progress = 0
    pbar = None
    for stderr_line in iter(ffmpeg_process.stderr.readline, ""):
        line = str(stderr_line)[:-1]
        if verbose:
            print(line)
        else:
            if any(x in line for x in ['Stream', 'Output', 'Input']):
                print(line)
            if 'Duration:' in line:
                duration = line.split(',')[0][-11:].split('.')[0]
                duration = datetime.strptime(duration, '%H:%M:%S')
                total_seconds = int((duration - datetime(1900, 1, 1)).total_seconds())
            if 'time=' in line:
                if not set_progress_bar:
                    input_file_name = os.path.basename(ffmpeg_cmd[2])
                    pbar = tqdm(total=total_seconds, desc=f"Encoding {input_file_name}")
                    set_progress_bar = True
                line = line.split(' ')
                progress = [w for w in line if 'time' in w][0].split('=')[-1].split('.')[0]
                progress = datetime.strptime(progress, '%H:%M:%S')
                current_progress = int((progress - datetime(1900, 1, 1)).total_seconds())
                update_progress = current_progress - last_progress
                pbar.update(update_progress)
                last_progress = current_progress
    if pbar:
        pbar.close()
    ffmpeg_process.stderr.close()
    return_code = ffmpeg_process.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, ffmpeg_cmd)

    toc = time.perf_counter()

    print(f'{ffmpeg_process}')
    print(f'encoding time: {toc - tic:.2f} seconds')


if __name__ == '__main__':
    base_path = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        dest='input',
                        help='Input video or folder path',
                        required=True,
                        type=str)
    parser.add_argument('-p', '--platform',
                        choices='psvr',
                        dest='platform',
                        default='psvr',
                        help='Specify the platform target')
    parser.add_argument('-d', '--degrees',
                        choices=('0', '180', '360'),
                        dest='degrees',
                        default='180',
                        help='Specify video degrees, or 0 for flat/fixed-frame')
    parser.add_argument('-e', '--encoder',
                        choices=('h264_nvenc', 'libx264'),
                        dest='encoder',
                        default='libx264',
                        help='h264_venc for GPU acceleration')
    parser.add_argument('-t', '--type',
                        choices=('sbs', 'ou', 'mono', '2d'),
                        dest='type',
                        default='sbs',
                        help='Input video type')
    parser.add_argument('--verbose',
                        dest='verbose',
                        action='store_true',
                        help='Print original encoding output')
    args = parser.parse_args()

    if not os.path.isabs(args.input):
        args.input = os.path.join(base_path, args.input)
        print(args.input)

    if os.path.isfile(args.input):
        probe_file(args.input)
    elif os.path.isdir(args.input):
        probe_dir(args.input)
    else:
        print(f'Invalid input path')
        sys.exit()
    print_probe_result()

    f = open(os.path.join(base_path, 'ffmpeg_args.json'))
    data = json.load(f)
    f.close()
    data = data[args.platform]

    input_files = [i[-1] for i in prob_results]

    print(f'\n################### Encoding ###################')
    for input_file in input_files:
        print()
        ffmpeg_args = ['ffmpeg', '-i', input_file, '-c:v', args.encoder]
        encode_file(ffmpeg_args, args.verbose)
