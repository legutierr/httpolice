# -*- coding: utf-8; -*-

from collections import namedtuple


# Commonly useful structures for representing various elements of the protocol


class _Unparseable(object):

    __slots__ = ()

    def __repr__(self):
        return 'Unparseable'

    def __eq__(self, other):
        return False

Unparseable = _Unparseable()


def okay(x):
    return (x is not None) and (x is not Unparseable)


class Parametrized(namedtuple('Parametrized', ('item', 'param'))):

    __slots__ = ()

    def __eq__(self, other):
        return (self.item == other) or super(Parametrized, self).__eq__(other)

    def __ne__(self, other):
        return (self.item != other) and super(Parametrized, self).__ne__(other)


class Versioned(namedtuple('Versioned', ('item', 'version'))):

    __slots__ = ()

    def __unicode__(self):
        if self.version:
            return u'%s/%s' % self
        else:
            return unicode(self.item)


class ProtocolString(unicode):

    __slots__ = ()

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, unicode.__repr__(self))


class CaseInsensitive(ProtocolString):

    __slots__ = ()

    def __eq__(self, other):
        if isinstance(other, basestring):
            return self.lower() == other.lower()
        else:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.lower())

    def startswith(self, other):
        return self.lower().startswith(other.lower())

    def endswith(self, other):
        return self.lower().endswith(other.lower())


###############################################################################


# Representations of specific protocol elements


class Message(object):

    __slots__ = ('version', 'header_entries', 'body', 'trailer_entries', 'raw')

    def __init__(self, version, header_entries,
                 body=None, trailer_entries=None, raw=None):
        self.version = HTTPVersion(version)
        self.header_entries = [HeaderEntry(k, v)
                               for k, v in header_entries]
        self.body = body if body is None else str(body)
        self.trailer_entries = [HeaderEntry(k, v)
                                for k, v in trailer_entries or []]
        self.raw = raw if raw is None else str(raw)


class Request(Message):

    __slots__ = ('scheme', 'method', 'target')

    def __init__(self, scheme, method, target, version, header_entries,
                 body=None, trailer_entries=None, raw=None):
        super(Request, self).__init__(version, header_entries,
                                      body, trailer_entries, raw)
        self.scheme = scheme if scheme is None else str(scheme)
        self.method = Method(method)
        self.target = str(target)

    def __repr__(self):
        return '<Request %s>' % self.method


class Response(Message):

    __slots__ = ('request', 'status', 'reason')

    def __init__(self, request, version, status, reason, header_entries,
                 body=None, trailer_entries=None, raw=None):
        super(Response, self).__init__(version, header_entries,
                                       body, trailer_entries, raw)
        self.request = request
        self.status = StatusCode(status)
        self.reason = reason if reason is None else str(reason)

    def __repr__(self):
        return '<Response %d>' % self.status


class HTTPVersion(ProtocolString):

    __slots__ = ()


http10 = HTTPVersion(u'HTTP/1.0')
http11 = HTTPVersion(u'HTTP/1.1')


class Method(ProtocolString):

    __slots__ = ()


class StatusCode(int):

    __slots__ = ()

    def __repr__(self):
        return 'StatusCode(%d)' % self

    informational = property(lambda self: 100 <= self < 199)
    successful = property(lambda self: 200 <= self < 299)
    redirection = property(lambda self: 300 <= self < 399)
    client_error = property(lambda self: 400 <= self < 499)
    server_error = property(lambda self: 500 <= self < 599)


class HeaderEntry(namedtuple('HeaderEntry', ('name', 'value'))):

    __slots__ = ()

    def __new__(cls, name, value):
        return super(HeaderEntry, cls).__new__(cls,
                                               FieldName(name), str(value))

    def __repr__(self):
        return '<HeaderEntry %s>' % self.name


class FieldName(CaseInsensitive):

    __slots__ = ()


class TransferCoding(CaseInsensitive):

    __slots__ = ()


class ContentCoding(CaseInsensitive):

    __slots__ = ()


class ConnectionOption(CaseInsensitive):

    __slots__ = ()


class MediaType(CaseInsensitive):

    """
    Although in RFC 7231 a ``<media-type>`` includes parameters,
    what's mainly interesting for HTTPolice is the media type itself,
    i.e. the ``type/subtype`` pair
    (or ``type/*``, or ``*/*`` -- in the case of the ``Accept`` header,
    although formally a ``*`` matches the production for ``<token>``).

    We could represent this as a tuple, but that's a hopeless rabbit hole,
    because then we would branch out to structured suffixes (like ``+xml``),
    facet prefixes (like ``vnd.``), and so on.
    Instead we have a single string that can be picked apart
    by functions in :mod:`httpolice.known.media_type`.
    """

    __slots__ = ()


class UpgradeToken(CaseInsensitive):

    # RFC 7230 doesn't say that upgrade tokens are case-insensitive.
    # But RFC 6455 does say that for the ``WebSocket`` token,
    # and it would make a lot of sense in general.

    __slots__ = ()


class LanguageTag(CaseInsensitive):

    __slots__ = ()


class ProductName(ProtocolString):

    __slots__ = ()


class Charset(CaseInsensitive):

    __slots__ = ()


class EntityTag(namedtuple('EntityTag', ('weak', 'opaque_tag'))):

    __slots__ = ()

    def weak_equiv(self, other):
        return self.opaque_tag == other.opaque_tag

    def strong_equiv(self, other):
        return not self.weak and not other.weak and \
            self.opaque_tag == other.opaque_tag


class RangeUnit(CaseInsensitive):

    __slots__ = ()


class RangeSpecifier(namedtuple('RangeSpecifier', ('unit', 'ranges'))):

    __slots__ = ()


class ContentRange(namedtuple('ContentRange', ('unit', 'range'))):

    __slots__ = ()


class CacheDirective(CaseInsensitive):

    __slots__ = ()


class WarningValue(namedtuple('WarningValue',
                              ('code', 'agent', 'text', 'date'))):

    __slots__ = ()

    # Allow comparing directly to warning codes
    # so that we can do stuff like ``299 in msg.headers.warning``
    # (like with :class:`Parametrized`).

    def __eq__(self, other):
        return self.code == other or super(WarningValue, self).__eq__(other)

    def __ne__(self, other):
        return self.code != other and super(WarningValue, self).__ne__(other)


class WarnCode(int):

    __slots__ = ()

    def __repr__(self):
        return 'WarnCode(%d)' % self