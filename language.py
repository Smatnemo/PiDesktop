"""Pibooth language handling.
"""

import io
import os
import os.path as osp
import LDS
from configparser import ConfigParser
from LDS.utils import LOGGER, open_text_editor


PARSER = ConfigParser()

CURRENT = 'en'  # Dynamically set at startup

DEFAULT = {
    'en': {
        'intro': "Legal",
        'login': "Unlock Screen",
        'choose_document': "Choose Document",
        'choose_inmate': "Choose Inmate",
        'No_documents': "No Documents",
        'decrypt': "Enter Decryption Key",
        'wrong_decrypt': "Wrong Decryption Key",
        'locked': "3 attempts: Locked for 30 seconds",
        '1': "1 photo",
        '2': "2 photos",
        '3': "3 photos",
        '4': "4 photos",
        'capture': "",
        'capture_photo':"Please take a photo",
        'smile': "Smile !",
        'processing': "Processing...",
        'print': "Printing Document",
        'print_successful': "Document Printed",
        'print_failed': "Document Print Unsuccessful",
        'print_forget': "Please\nTake a\nphoto",
        'no_spooler':"Printer Spooler Not Running",
        'queue_stopped':"Print Queue Stopped",
        'no_printer':"Printer not detected",
        'decryption_failed':"Document failed to decrypt",
        'incomplete':"Document incomplete",
        'no_document':"Document not found",
        'no_orders':"No orders have been found",
        'download_orders':"Please download documents",
        'downloading':"Downloading Documents",
        'no_camera':"Camera not detected",
        'capture_again': "Take another photo?",
        'done':"Return to Documents",
        'num_of_pages': "Number of pages",
        'finished': "Thanks",
        'oops': "Oops! something went wrong",
        'wrong_password':"Oops! Wrong Password",
        'Q1':"Did it print successfully?",
        'Q2':"Was your image captured?",
        'Q3':"Was your signature captured?",
        'Q4':"Did the correctional officer see the document?",
        'code_required':"CO Unlock Code Required",
        'version':"Legal Version {}".format(LDS.__version__),
        'intro_print': "Or you can\nstill print\nthis photo",
        '':"",
    },
    'sp': {
        'Q1':"Did it print successfully?",
        'Q2':"Was your image captured?",
        'Q3':"Was your signature captured?"
    },
}

def init(filename, clear=False):
    """Initialize the translation system.

    :param filename: path to the translations file
    :type filename: str
    :param clear: restore default translations
    :type clear: bool
    """
    PARSER.filename = osp.abspath(osp.expanduser(filename))

    if not osp.isfile(PARSER.filename) or clear:
        LOGGER.info("Generate the translation file in '%s'", PARSER.filename)
        dirname = osp.dirname(PARSER.filename)
        if not osp.isdir(dirname):
            os.makedirs(dirname)

        with io.open(PARSER.filename, 'w', encoding="utf-8") as fp:
            for section, options in DEFAULT.items():
                fp.write("[{}]\n".format(section))
                for name, value in options.items():
                    value = value.splitlines()
                    fp.write("{} = {}\n".format(name, value[0]))
                    if len(value) > 1:
                        for part in value[1:]:
                            fp.write("    {}\n".format(part))
                fp.write("\n\n")

    PARSER.read(PARSER.filename, encoding='utf-8')

    # Update the current file with missing language(s) and key(s)
    changed = False
    for section, options in DEFAULT.items():
        if not PARSER.has_section(section):
            changed = True
            LOGGER.debug("Add [%s] to available language list", section)
            PARSER.add_section(section)

        for option, value in options.items():
            if not PARSER.has_option(section, option):
                changed = True
                LOGGER.debug("Add [%s][%s] to available translations", section, option)
                PARSER.set(section, option, value)

    if changed:
        with io.open(PARSER.filename, 'w', encoding="utf-8") as fp:
            PARSER.write(fp)


def edit():
    """Open a text editor to edit the translations.
    """
    if not getattr(PARSER, 'filename', None):
        raise EnvironmentError("Translation system is not initialized")

    open_text_editor(PARSER.filename)


def get_supported_languages():
    """Return the list of supported language.
    """
    if getattr(PARSER, 'filename', None):
        return list(sorted(lang for lang in PARSER.sections()))
    return list(sorted(DEFAULT.keys()))


def get_translated_text(key):
    """Return the text corresponding to the key in the language defined in the config.

    :param key: key in the translation file
    :type key: str
    """
    if not getattr(PARSER, 'filename', None):
        raise EnvironmentError("Translation system is not initialized")

    if PARSER.has_section(CURRENT) and PARSER.has_option(CURRENT, key):
        return PARSER.get(CURRENT, key).strip('"')
    elif PARSER.has_option('en', key):
        LOGGER.warning("Unsupported language '%s', fallback to English", CURRENT)
        return PARSER.get('en', key).strip('"')

    LOGGER.debug("No translation defined for '%s/%s' key", CURRENT, key)
    return None