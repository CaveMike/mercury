import md5

class Digest(object):
    @staticmethod
    def ha1( username, realm, password ):
    	return md5.md5( username + ':' + realm + ':' + password ).hexdigest()

    @staticmethod
    def ha2( method, uri ):
	return md5.md5( method + ':' + uri ).hexdigest()

    @staticmethod
    def response( ha1, ha2, nonce, nc = None, cnonce = None, qop = None ):
        if nc is None or cnonce is None or qop is None:
            r = ha1 + ':' + nonce + ':' + ha2
        else:
            r = ha1 + ':' + nonce + ':' + str(nc) + ':' + str(cnonce) + ':' + str(qop) + ':' + ha2
	return md5.md5( r ).hexdigest()

