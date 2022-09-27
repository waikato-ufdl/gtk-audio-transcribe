from setuptools import setup


def _read(f):
    """
    Reads in the content of the file.
    :param f: the file to read
    :type f: str
    :return: the content
    :rtype: str
    """
    return open(f, 'rb').read()


setup(
    name="gtk-audio-transcribe",
    description="Simple GTK user interface for transcribing audio.",
    url="https://github.com/waikato-ufdl/gtk-audio-transcribe",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 3',
    ],
    package_dir={
        '': 'src'
    },
    packages=[
        "gat",
    ],
    package_data={
        "gat": ["*.css", "*.glade", "*.png"],
    },
    install_requires=[
        "numpy==1.23.3",
        "scipy==1.9.1",
        "sounddevice==0.4.5",
        "pyyaml",
        "pygobject",
        "PyGObject-stubs",
        "redis",
    ],
    version="0.0.1",
    author='Peter Reutemann',
    author_email='fracpete@waikato.ac.nz',
    entry_points={
        "console_scripts": [
            "gat-transcribe=gat.transcribe:sys_main",
        ]
    }
)
