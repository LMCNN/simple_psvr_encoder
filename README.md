# Simple Psvr Encoder

A simple tool to encode psvr video.

## Usage

### Environment setup

1. Install [python](https://www.python.org/downloads/) (don't forget to add python to PATH)

2. Download [ffmpeg](https://www.ffmpeg.org/download.html), and add ffmpeg/bin to PATH
4. Download this tool

### Encode

```shell
usage: psvr_encode.py [-h] -i INPUT [-a {psvr,littlestar}] [-d {0,180,360}]
                      [-e {h264_nvenc,libx264}] [-t {sbs,ou,mono,2d}]
                      [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input video or folder path
  -a {psvr,littlestar}, --arguments {psvr,littlestar}
                        Specify the ffmpeg arguments
  -d {0,180,360}, --degrees {0,180,360}
                        Specify video degrees, or 0 for flat/fixed-frame
  -e {h264_nvenc,libx264}, --encoder {h264_nvenc,libx264}
                        h264_venc for GPU acceleration
  -t {sbs,ou,mono,2d}, --type {sbs,ou,mono,2d}
                        Input video type
  --verbose             Print original encoding output

```

#### Encode a single file

Suppose the input file's path is: D:\test.mp4 , run following command

```shell
python psvr_encode.py -i D:\test.mp4
```

then a encoded file(test_psvr_180_sbs.mp4) is generated in the same folder of the input file. The postfix of the the output file is determined by the input arguments.  Default arguments are: psvr, 180, sbs, and libx264.

#### Encode files in the same folder

Suppose the folder which contains the input file has following structure:

```shell
D:\test 
        test1.mkv
        test2.mkv
        test3.mp4
```

Run following command:

```shell
python psvr_encode.py -i D:\test
```

then the outputs will be like this:

```shell
D:\test 
        test1.mkv
        test1_psvr_180_sbs.mp4
        test2.mkv
        test2_psvr_180_sbs.mp4
        test3.mp4
        test3_psvr_180_sbs.mp4
```

