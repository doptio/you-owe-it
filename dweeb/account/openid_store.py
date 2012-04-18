'''OpenID authentication Store using memcached.'''

import logging
import memcache
from openid.store.interface import OpenIDStore

log = logging.getLogger(__name__)
memcache = memcache.Client(['127.0.0.1:11211'], debug=0)

NONCE_TTL = 600

def assoc_key(server_url, handle):
    # FIXME - Should probably quote the server_url and handle to be good
    # little programmers.
    if handle:
        key = 'openid.association.%s.%s' % (server_url, handle)
    else:
        key = 'openid.association.%s' % (server_url)
    return key.encode('utf-8')

def nonce_key(server_url, timestamp, salt):
    # FIXME - Should probably quote the server_url and handle to be good
    # little programmers.
    key = 'openid.nonce.%s.%d.%s' % (server_url, timestamp, salt)
    return key.encode('utf-8')

class MemcacheStore(OpenIDStore):
    '''Memcached-backed OpenID authentication store.'''

    def storeAssociation(self, server_url, assoc):
        for handle in [assoc.handle, None]:
            memcache.set(assoc_key(server_url, handle),
                         assoc,
                         assoc.getExpiresIn())

    def getAssociation(self, server_url, handle=None):
        return memcache.get(assoc_key(server_url, handle))

    def removeAssociation(self, server_url, handle):
        return bool(memcache.delete(assoc_key(server_url, handle)))

    def useNonce(self, server_url, timestamp, salt):
        key = nonce_key(server_url, timestamp, salt)
        return bool(memcache.add(key, '-', NONCE_TTL))

    def cleanupAssociations(self):
        pass

    def cleanupNonces(self):
        pass
