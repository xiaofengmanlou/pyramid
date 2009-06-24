""" Utility functions for dealing with URLs in repoze.bfg """

import urllib

from zope.component import queryMultiAdapter
from zope.component import getUtility
from repoze.bfg.interfaces import IContextURL
from repoze.bfg.interfaces import IRoutesMapper

from repoze.bfg.traversal import TraversalContextURL
from repoze.bfg.traversal import quote_path_segment

from routes import URLGenerator
from routes.util import GenerationException

def route_url(request, route_name, **kw):
    """Generates a fully qualified URL for a named BFG route.
    
    Use the request object as the first positional argument.  Use the
    route's ``name`` as the second positional argument.  Use keyword
    arguments to supply values which match any dynamic path elements
    in the route definition.  Raises a ValueError exception if the URL
    cannot be generated when the

    For example, if you've defined a route named "foobar" with the path
    ``:foo/:bar/*traverse``::

        route_url(request, 'foobar', foo='1')          => <ValueError exception>
        route_url(request, 'foobar', foo='1', bar='2') => <ValueError exception>
        route_url('foobar', foo='1', bar='2',
                   'traverse='a/b)                     =>  http://e.com/1/2/a/b

    All keys given to ``route_url`` are sent to the BFG Routes "mapper"
    instance for generation except for::
        
        anchor          specifies the anchor name to be appened to the path
        host            overrides the default host if provided
        protocol        overrides the default (current) protocol if provided
        qualified       return a fully qualified URL (default True)

    """
    if not 'qualified' in kw:
        kw['qualified'] = True
    try:
        mapper = getUtility(IRoutesMapper)
        generator = URLGenerator(mapper, request.environ)
        return generator(route_name, **kw)
    except GenerationException, why:
        raise ValueError(str(why))

def model_url(model, request, *elements, **kw):
    """
    Generate a string representing the absolute URL of the model (or
    context) object based on the ``wsgi.url_scheme``, ``HTTP_HOST`` or
    ``SERVER_NAME`` in the request, plus any ``SCRIPT_NAME``.  If a
    'virtual root path' is present in the request environment (the
    value of the WSGI environ key ``HTTP_X_VHM_ROOT``), and the
    ``model`` was obtained via traversal, the URL path will not
    include the virtual root prefix (it will be stripped out of the
    generated URL).  If a ``query`` keyword argument is provided, a
    query string based on its value will be composed and appended to
    the generated URL string (see details below).  The overall result
    of this function is always a UTF-8 encoded string (never unicode).

    .. note:: If the ``model`` used is the result of a traversal, it
       must be :term:`location`-aware.  The 'model' can also be the
       context of a URL dispatch; contexts found this way do not need
       to be location-aware.

    Any positional arguments passed in as ``elements`` must be strings
    or unicode objects.  These will be joined by slashes and appended
    to the generated model URL.  Each of the elements passed in is
    URL-quoted before being appended; if any element is unicode, it
    will converted to a UTF-8 bytestring before being URL-quoted.

    .. warning:: if no ``elements`` arguments are specified, the model
                 URL will end with a trailing slash.  If any
                 ``elements`` are used, the generated URL will *not*
                 end in trailing a slash.

    If a keyword argument ``query`` is present, it will used to
    compose a query string that will be tacked on to the end of the
    URL.  The value of ``query`` must be a sequence of two-tuples *or*
    a data structure with an ``.items()`` method that returns a
    sequence of two-tuples (presumably a dictionary).  This data
    structure will be turned into a query string per the documentation
    of ``repoze.url.urlencode`` function.  After the query data is
    turned into a query string, a leading ``?`` is prepended, and the
    the resulting string is appended to the generated URL.

    .. note:: Python data structures that are passed as ``query``
              which are sequences or dictionaries are turned into a
              string under the same rules as when run through
              urllib.urlencode with the ``doseq`` argument equal to
              ``True``.  This means that sequences can be passed as
              values, and a k=v pair will be placed into the query
              string for each value.

    If a keyword argument ``anchor`` is present, its string
    representation will be used as a named anchor in the generated URL
    (e.g. if ``anchor`` is passed as ``foo`` and the model URL is
    ``http://example.com/model/url``, the resulting generated URL will
    be ``http://example.com/model/url#foo``).

    .. note:: If ``anchor`` is passed as a string, it should be UTF-8
              encoded. If ``anchor`` is passed as a Unicode object, it
              will be converted to UTF-8 before being appended to the
              URL.  The anchor value is not quoted in any way before
              being appended to the generated URL.

    If both ``anchor`` and ``query`` are specified, the anchor element
    will always follow the query element,
    e.g. ``http://example.com?foo=1#bar``.
    """
    
    context_url = queryMultiAdapter((model, request), IContextURL)
    if context_url is None:
        # b/w compat for unit tests
        context_url = TraversalContextURL(model, request)
    model_url = context_url()

    qs = ''
    anchor = ''

    if 'query' in kw:
        qs = '?' + urlencode(kw['query'], doseq=True)

    if 'anchor' in kw:
        anchor = kw['anchor']
        if isinstance(anchor, unicode):
            anchor = anchor.encode('utf-8')
        anchor = '#' + anchor

    if elements:
        suffix = '/'.join([quote_path_segment(s) for s in elements])
    else:
        suffix = ''

    return model_url + suffix + qs + anchor

def urlencode(query, doseq=False):
    """
    A wrapper around Python's stdlib `urllib.urlencode function
    <http://docs.python.org/library/urllib.html>`_ which accepts
    unicode keys and values within the ``query`` dict/sequence; all
    Unicode keys and values are first converted to UTF-8 before being
    used to compose the query string.  The behavior of the function is
    otherwise the same as the stdlib version.

    The value of ``query`` must be a sequence of two-tuples
    representing key/value pairs *or* an object (often a dictionary)
    with an ``.items()`` method that returns a sequence of two-tuples
    representing key/value pairs.  ``doseq`` controls what happens
    when a sequence is presented as one of the values.  See the Python
    stdlib documentation for ``urllib.urlencode`` for more
    information.
    """
    if hasattr(query, 'items'):
        # presumed to be a dictionary
        query = query.items()

    newquery = []
    for k, v in query:

        if k.__class__ is unicode:
            k = k.encode('utf-8')

        try:
            v.__iter__
        except AttributeError:
            if v.__class__ is unicode:
                v = v.encode('utf-8')
        else:
            L = []
            for x in v:
                if x.__class__ is unicode:
                    x = x.encode('utf-8')
                L.append(x)
            v = L

        newquery.append((k, v))

    return urllib.urlencode(newquery, doseq=doseq)


