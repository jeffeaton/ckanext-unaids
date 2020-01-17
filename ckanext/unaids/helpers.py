# encoding: utf-8
from ckan.lib.helpers import url_for_static_or_external
from ckan.common import g
import logging
import os

log = logging.getLogger()


def get_logo_path(logo_filename, language):
    '''Returns the URL for static content that requires localization.
    '''
    log.debug("Called get_logo_path")
    log.debug("Logo filename: {}".format(logo_filename))
    log.debug("Language: {}".format(language))

    current_directory = os.path.dirname(
        os.path.abspath(__file__)
    )
    public_directory = current_directory + "/theme/public"
    localised_logo_filename = "/{}_{}".format(language, logo_filename[1:])
    localised_logo_path = public_directory + localised_logo_filename

    log.debug("Localised logo path: {}".format(localised_logo_path))

    if os.path.exists(localised_logo_path):
        return url_for_static_or_external(localised_logo_filename)
    else:
        return url_for_static_or_external(logo_filename)
