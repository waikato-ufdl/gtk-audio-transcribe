# gtk-audio-transcribe
Simple user interface for transcribing audio into text (STT). 

The user interface records audio, broadcasts it on a [Redis](https://redis.io/) 
channel and then displays the transcript that was received on another Redis 
channel. The interface is therefore not tied to a particular STT engine, as long
as it can communicate via Redis channels.

Uses [python-sounddevice](https://python-sounddevice.readthedocs.io/en/latest/) under
the hood for recording the audio (stumbled across the library in 
[this post](https://realpython.com/playing-and-recording-sound-python/)).


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

## Coqui STT Example

The following example uses [Coqui STT](https://github.com/coqui-ai/STT) via 
[Redis and docker](https://github.com/waikato-datamining/tensorflow/tree/master/coqui/stt).

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
