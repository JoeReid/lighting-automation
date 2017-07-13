import sys
import logging
import re
import os.path
import importlib
from pathlib import PurePath
from functools import reduce
from functools import partial

import progressbar
import yaml

from ext.misc import fast_scan, fast_scan_regex_filter
from ext.attribute_packer import PersistentFramePacker
from ext.music import get_time, parse_timesigniture

from stageOrchestration.lighting.model.device_collection_loader import device_collection_loader
from .render_binary_sequence import render_binary_sequence

REGEX_PY_EXTENSION = re.compile(r'\.py$')
FAST_SCAN_REGEX_FILTER_FOR_PY_FILES = fast_scan_regex_filter(file_regex=REGEX_PY_EXTENSION, ignore_regex=r'^_')

log = logging.getLogger(__name__)


class SequenceManager(object):

    def __init__(self, path_sequences=None, path_stage_description=None, tempdir=None, framerate=None, **kwargs):
        assert os.path.isdir(path_sequences)
        assert os.path.isfile(path_stage_description)
        assert os.path.exists(tempdir)
        assert framerate

        self.path_sequences = PurePath(path_sequences)
        sys.path.append(str(self.path_sequences.parent))  # Can't load modules from path. Must add a system path. Thanks Python.
        self.tempdir = tempdir
        self.framerate = framerate
        self.device_collection = device_collection_loader(path_stage_description)
        assert self.device_collection.devices

        self.sequence_modules = {}

        self.reload_sequences()

    def get_filename(self, sequence):
        """
        Can be passed a module, sequence_name or filename
        """
        if hasattr(sequence, '_sequence_name'):
            sequence = sequence._sequence_name
        if not os.path.exists(sequence):
            sequence = os.path.join(self.tempdir, sequence)
        return sequence

    def get_packer(self, sequence, assert_exists=True):
        # TODO: make this a context manager?
        sequence = self.get_filename(sequence)
        if assert_exists:
            assert os.path.exists(sequence)
        return PersistentFramePacker(self.device_collection, sequence)

    def reload_sequences(self, sequence_files=None):
        """
        Traps for the Unwary in Python’s Import System
          http://python-notes.curiousefficiency.org/en/latest/python_concepts/import_traps.html
        """

        def _all_sequence_files():
            return tuple(
                (f.relative, f.abspath)
                for f in fast_scan(str(self.path_sequences), search_filter=FAST_SCAN_REGEX_FILTER_FOR_PY_FILES)
            )

        bar_sequence_name_label = progressbar.FormatCustomText('%(sequence_name)-20s', {'sequence_name': ''})
        bar = progressbar.ProgressBar(
            widgets=(
                'Rendering: ', bar_sequence_name_label, ' ', progressbar.Bar(marker='=', left='[', right=']'),
            ),
        )

        for f_relative, f_absolute in bar(sequence_files or _all_sequence_files()):
            bar_sequence_name_label.update_mapping(sequence_name=f_relative)
            self._render_sequence_module(
                self._load_sequence_module(f_relative),
            )

    def _load_sequence_module(self, f_relative):
        package_name = REGEX_PY_EXTENSION.sub('', f_relative).replace('/', '.')
        if package_name in self.sequence_modules:
            importlib.reload(self.sequence_modules[package_name])
        else:
            self.sequence_modules[package_name] = importlib.import_module(f'{self.path_sequences.stem}.{package_name}')
        sequence_module = self.sequence_modules[package_name]
        setattr(sequence_module, '_sequence_name', sequence_module.__name__.replace(f'{sequence_module.__package__}.', ''))
        return sequence_module

    def _render_sequence_module(self, sequence_module):
        log.debug('Rendering sequence_module {}'.format(sequence_module._sequence_name))
        packer = self.get_packer(sequence_module, assert_exists=False)

        def meta_yaml_reducer(accu, filename):
            filename = os.path.join(self.path_sequences, filename)
            if os.path.exists(filename):
                with open(filename, 'rt') as filehandle:
                    accu.update(yaml.load(filehandle))
            return accu
        meta = reduce(meta_yaml_reducer, ('_default.yaml', f'{sequence_module._sequence_name}.yaml'), {})

        get_time_func = partial(get_time, timesigniture=parse_timesigniture(meta['timesignature']), bpm=meta['bpm'])

        render_binary_sequence(
            packer=packer,
            sequence_module=sequence_module,
            device_collection=self.device_collection,
            get_time_func=get_time_func,
            frame_rate=self.framerate,  # TODO: correct inconsistent naming
        )
        packer.close()
        assert os.path.exists(packer.filename), f'Should have generated sequence file {packer.filename}'
