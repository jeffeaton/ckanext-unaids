# encoding: utf-8
from ckan.lib.helpers import url_for_static_or_external


def url_for_translated_static_or_external(*args, **kw):
    '''Returns the URL for static content that requires localization.
    '''

    args = (args[0].replace("/", "/{}_".format(kw.get('lang')), 1), ) + args[1:]
    return url_for_static_or_external(*args, **kw)
