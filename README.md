# gtk-audio-transcribe
Simple user interface for transcribing audio into text (STT).

## Installation

Install redis on your machine (if not already present):

```bash
sudo apt install redis-server
sudo systemctl restart redis
```

Set up the virtual environment and install the application:

```bash
virtualenv -p /usr/bin/python3 venv
./venv/bin/pip install "git+ssh://git@github.com/waikato-ufdl/gtk-audio-transcribe.git"
```

## Example

### Docker

Download the [English tflite model](https://github.com/waikato-ufdl/gtk-audio-transcribe/releases/download/v1.3.0/full.tflite) 
into the current directory and start the Coqui container from the same directory: 

```bash
docker run   \
    --net=host \
    -v `pwd`:/workspace \
    -it waikatodatamining/tf_coqui_stt:1.15.2_0.10.0a10_cpu \
    stt_transcribe_redis \
    --redis_in audio \
    --redis_out transcript \
    --model /workspace/full.tflite \
    --verbose
```

### Config

Create a YAML config file called `config.yaml` in the current directory with the following content:

```yaml
# the 
redis:
  host: "localhost"
  port: 6379
  db: 0
  channel_out: "audio"
  channel_in: "transcript"

recording:
  # the device to use for recording
  device: "pulse"
  # maximum length in seconds
  max_duration: 3.0
  # the number of channels
  num_channels: 1
  # the sample rate in Hz
  sample_rate: 16000
```

### Application

Start the application as follows:

```bash
./venv/bin/python3 -c config.yaml
```
