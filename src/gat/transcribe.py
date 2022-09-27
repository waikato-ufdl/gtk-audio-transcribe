import argparse
import gi
import numpy as np
import os
import redis
import threading
import traceback
import sounddevice as sd

gi.require_version('Gtk', '3.0')
from io import BytesIO
from gi.repository import Gtk, Gdk, GLib
from scipy.io.wavfile import write
from yaml import load
from yaml import Loader


def load_config(path):
    """
    Loads the configuration from the specified file.

    :param path: the path pointing to the config file (YAML)
    :type path: str
    :return: the configuration
    :rtype: dict
    """
    with open(path, "r") as cf:
        return load(cf, Loader=Loader)


def app_dir():
    """
    Returns the application dir.

    :return: the directory:
    :rtype: str
    """
    return os.path.dirname(__file__)


def float2pcm(sig, dtype='int16'):
    # https://stackoverflow.com/a/62215702/4698227
    sig = np.asarray(sig)
    dtype = np.dtype(dtype)
    i = np.iinfo(dtype)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    return (sig * abs_max + offset).clip(i.min, i.max).astype(dtype)


class MainWindow(object):
    """
    Handles the main window and its events.
    """

    def __init__(self, config, builder):
        """
        Initializes the manager.

        :param config: the configuration
        :type config: dict
        :param builder: the GTK builder instance to use
        :type builder: Gtk.Builder
        """
        self.redis = config["redis"]
        self.r = redis.Redis(host=self.redis["host"], port=self.redis["port"], db=self.redis["db"])
        self.pubsub = None

        self.recording = config["recording"]
        sd.default.device = self.recording["device"]

        builder.connect_signals(self)

        self.window = builder.get_object("window_main")
        self.gtkbox_buttons = builder.get_object("gtkbox_buttons")
        self.gtkbox_focus = builder.get_object("gtkbox_focus")
        self.button_rec = builder.get_object("button_rec")
        self.button_stop = builder.get_object("button_stop")
        self.button_exit = builder.get_object("button_exit")
        self.text_viewport = builder.get_object("text_viewport")

        self.text_transcript_buffer = Gtk.TextBuffer()
        self.text_transcript = builder.get_object("text_transcript")
        self.text_transcript.set_buffer(self.text_transcript_buffer)

        self.buffer = None
        self.is_recording = False

        self.update_buttons()

    def button_rec_clicked_cb(self, button):
        def _record_audio(main):
            main.buffer = sd.rec(
                int(self.recording["max_duration"] * self.recording["sample_rate"]),
                samplerate=self.recording["sample_rate"],
                channels=self.recording["num_channels"])
            sd.wait()
            audio = BytesIO()
            write(audio, self.recording["sample_rate"], float2pcm(main.buffer))
            main.r.publish(main.redis["channel_out"], audio.read())
            main.is_recording = False
            GLib.idle_add(main.update_buttons)

        self.is_recording = True
        self.update_buttons()
        t = threading.Thread(target=_record_audio, args=(self,))
        t.start()

    def button_clear_clicked_cb(self, button):
        self.text_transcript_buffer.set_text("")

    def button_exit_clicked_cb(self, button):
        if self.is_recording:
            sd.stop()
        Gtk.main_quit()

    def window_main_delete_event_cb(self, *args):
        if self.is_recording:
            sd.stop()
        Gtk.main_quit(*args)

    def update_buttons(self):
        self.button_rec.set_sensitive(not self.is_recording)


def transcribe(config):
    """
    Opens up interface for transcribing audio.

    :param config: the configuration parameters
    :type config: dict
    """
    # load UI
    builder = Gtk.Builder()
    builder.add_from_file(app_dir() + "/transcribe.glade")

    # attach signals
    main_window = MainWindow(config, builder)

    # add css
    screen = Gdk.Screen.get_default()
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path(app_dir() + "/transcribe.css")
    context = Gtk.StyleContext()
    context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    # display window
    window = builder.get_object("window_main")
    window.set_title("Transcribe audio")
    window.set_position(Gtk.WindowPosition.CENTER)
    window.show_all()

    def _output_transcript(main):
        def anon_handler(message):
            text = message['data'].decode()
            if len(text.strip()) == 0:
                text = "..."
            end_iter = main.text_transcript_buffer.get_end_iter()
            main.text_transcript_buffer.insert(end_iter, text + "\n")

        # subscribe and start listening
        p = main.r.pubsub()
        main.pubsub = p
        p.psubscribe(**{main.redis["channel_in"]: anon_handler})
        p.run_in_thread(sleep_time=0.001)

    t = threading.Thread(target=_output_transcript, args=(main_window,))
    t.start()

    Gtk.main()

    # let thread finish, error message can be ignored
    if main_window.pubsub is not None:
        main_window.pubsub.close()


def main(args=None):
    """
    Performs the collection.
    Use -h to see all options.

    :param args: the command-line arguments to use, uses sys.argv if None
    :type args: list
    """

    parser = argparse.ArgumentParser(
        description='Simple user interface for transcribing audio.',
        prog="gat-transcribe",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--config", dest="config", metavar="FILE", required=True, help="the YAML file with the configuration")
    parsed = parser.parse_args(args=args)

    config = load_config(parsed.config)
    transcribe(config)


def sys_main():
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    :rtype: int
    """

    try:
        main()
        return 0
    except Exception:
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc())
