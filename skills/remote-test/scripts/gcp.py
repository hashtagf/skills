"""Stdlib-only Google Cloud REST helpers shared by client, API and node agent.

No third-party packages: team Macs, Cloud Run functions and test VMs use the
same code. Tokens come from gcloud (users) or the metadata server (services).
"""
import base64, json, os, ssl, subprocess, threading, time, urllib.error, urllib.parse, urllib.request

METADATA = 'http://metadata.google.internal/computeMetadata/v1/'


def _tls_context():
    """python.org macOS builds ship without CA certs unless 'Install Certificates'
    was run; fall back to the system bundle so no extra package is needed."""
    ctx = ssl.create_default_context()
    if not ctx.cert_store_stats().get('x509_ca'):
        for bundle in (os.environ.get('SSL_CERT_FILE'), '/etc/ssl/cert.pem', '/etc/ssl/certs/ca-certificates.crt'):
            if bundle and os.path.isfile(bundle):
                ctx.load_verify_locations(bundle); break
    return ctx


TLS = _tls_context()


class ApiError(RuntimeError):
    def __init__(self, code, status, message):
        super().__init__(f'{code} {status}: {message}')
        self.code, self.status, self.message = code, status, message


class Precondition(ApiError):
    """Optimistic-concurrency or create-if-absent conflict."""


class NotFound(ApiError):
    pass


class GcloudTokens:
    """User credentials from the local gcloud CLI (team Macs)."""
    def __init__(self, gcloud='gcloud'):
        self.gcloud, self._lock, self._cache = gcloud, threading.Lock(), {}

    def _get(self, kind, args):
        with self._lock:
            value, expiry = self._cache.get(kind, (None, 0))
            if value and time.time() < expiry:
                return value
            try:
                out = subprocess.run([self.gcloud, 'auth', *args], check=True, capture_output=True, text=True, timeout=60)
            except subprocess.CalledProcessError as error:
                raise RuntimeError('gcloud authentication failed; run `gcloud auth login` (' + error.stderr.strip()[-300:] + ')') from None
            value = out.stdout.strip()
            self._cache[kind] = (value, time.time() + 1500)
            return value

    def access(self):
        return self._get('access', ['print-access-token'])

    def identity(self, audience=None):
        # User accounts cannot choose an audience; Cloud Run IAM accepts gcloud user ID tokens.
        return self._get('identity', ['print-identity-token'])


class MetadataTokens:
    """Attached service account credentials (Cloud Run, Compute Engine)."""
    def __init__(self):
        self._lock, self._cache = threading.Lock(), (None, 0)

    def access(self):
        with self._lock:
            value, expiry = self._cache
            if value and time.time() < expiry:
                return value
            req = urllib.request.Request(METADATA + 'instance/service-accounts/default/token', headers={'Metadata-Flavor': 'Google'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.load(resp)
            self._cache = (data['access_token'], time.time() + max(60, data.get('expires_in', 300) - 120))
            return data['access_token']

    @staticmethod
    def attribute(path):
        req = urllib.request.Request(METADATA + path, headers={'Metadata-Flavor': 'Google'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode()


def request(method, url, tokens=None, body=None, data=None, headers=None, timeout=60, token=None, retries=3):
    """JSON request with bounded retry for transient (429/5xx/network) failures."""
    hdrs = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode()
        hdrs['Content-Type'] = 'application/json'
    for attempt in range(retries + 1):
        auth = token or (tokens.access() if tokens else None)
        if auth:
            hdrs['Authorization'] = 'Bearer ' + auth
        payload = data
        if hasattr(data, 'seek'):
            data.seek(0)
        req = urllib.request.Request(url, data=payload, method=method, headers=hdrs)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=TLS if url.startswith('https') else None) as resp:
                raw = resp.read()
                kind = resp.headers.get('Content-Type', '')
                return json.loads(raw) if raw and 'json' in kind else raw
        except urllib.error.HTTPError as error:
            raw = error.read()
            try:
                info = json.loads(raw).get('error', {})
                info = info if isinstance(info, dict) else {'message': str(info)}
            except ValueError:
                info = {'message': raw.decode(errors='replace')[:500]}
            status, message = info.get('status', ''), info.get('message', '')
            if error.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(2 * (attempt + 1)); continue
            if error.code == 404:
                raise NotFound(error.code, status, message) from None
            if error.code == 409 or status in ('FAILED_PRECONDITION', 'ABORTED', 'ALREADY_EXISTS') or error.code == 412:
                raise Precondition(error.code, status, message) from None
            raise ApiError(error.code, status, message) from None
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            if attempt < retries:
                time.sleep(2 * (attempt + 1)); continue
            raise ApiError(0, 'UNAVAILABLE', str(error)) from None


# ---------------------------------------------------------------- Firestore

def encode(value):
    if value is None: return {'nullValue': None}
    if isinstance(value, bool): return {'booleanValue': value}
    if isinstance(value, int): return {'integerValue': str(value)}
    if isinstance(value, float): return {'doubleValue': value}
    if isinstance(value, str): return {'stringValue': value}
    if isinstance(value, (list, tuple)): return {'arrayValue': {'values': [encode(v) for v in value]}}
    if isinstance(value, dict): return {'mapValue': {'fields': {k: encode(v) for k, v in value.items()}}}
    raise TypeError('Unsupported Firestore value: ' + type(value).__name__)


def decode(value):
    (kind, inner), = value.items()
    if kind == 'nullValue': return None
    if kind == 'integerValue': return int(inner)
    if kind == 'doubleValue': return float(inner)
    if kind == 'arrayValue': return [decode(v) for v in inner.get('values', [])]
    if kind == 'mapValue': return {k: decode(v) for k, v in inner.get('fields', {}).items()}
    return inner


class Firestore:
    """Document store. Documents are dicts; '_update_time' carries the version."""
    def __init__(self, project, database, tokens):
        self.tokens = tokens
        self.root = f'projects/{project}/databases/{database}/documents'
        self.base = 'https://firestore.googleapis.com/v1/' + self.root

    @staticmethod
    def _doc(raw):
        doc = {k: decode(v) for k, v in raw.get('fields', {}).items()}
        doc['_id'] = raw['name'].rsplit('/', 1)[1]
        doc['_update_time'] = raw.get('updateTime')
        return doc

    def get(self, collection, doc_id):
        try:
            return self._doc(request('GET', f'{self.base}/{collection}/{doc_id}', self.tokens))
        except NotFound:
            return None

    def create(self, collection, doc_id, fields):
        url = f'{self.base}/{collection}?documentId={urllib.parse.quote(doc_id)}'
        return self._doc(request('POST', url, self.tokens, body={'fields': {k: encode(v) for k, v in fields.items()}}))

    def update(self, collection, doc_id, fields, update_time=None):
        """Partial update; with update_time it succeeds only if unchanged since read."""
        query = [('updateMask.fieldPaths', k) for k in fields]
        query.append(('currentDocument.updateTime', update_time) if update_time else ('currentDocument.exists', 'true'))
        url = f'{self.base}/{collection}/{doc_id}?' + urllib.parse.urlencode(query)
        return self._doc(request('PATCH', url, self.tokens, body={'fields': {k: encode(v) for k, v in fields.items()}}))

    def query(self, collection, filters=(), order=None, descending=False, limit=None):
        """filters: (field, op, value) with Firestore ops: EQUAL, IN, LESS_THAN, ..."""
        q = {'from': [{'collectionId': collection}]}
        clauses = [{'fieldFilter': {'field': {'fieldPath': f}, 'op': op, 'value': encode(v)}} for f, op, v in filters]
        if len(clauses) == 1: q['where'] = clauses[0]
        elif clauses: q['where'] = {'compositeFilter': {'op': 'AND', 'filters': clauses}}
        if order: q['orderBy'] = [{'field': {'fieldPath': order}, 'direction': 'DESCENDING' if descending else 'ASCENDING'}]
        if limit: q['limit'] = limit
        rows = request('POST', self.base + ':runQuery', self.tokens, body={'structuredQuery': q})
        return [self._doc(r['document']) for r in rows if 'document' in r]


# ------------------------------------------------------------------ Pub/Sub

class PubSub:
    def __init__(self, project, tokens):
        self.project, self.tokens = project, tokens
        self.base = 'https://pubsub.googleapis.com/v1/projects/' + project

    def publish(self, topic, payload, **attributes):
        msg = {'data': base64.b64encode(json.dumps(payload).encode()).decode(), 'attributes': {k: str(v) for k, v in attributes.items()}}
        return request('POST', f'{self.base}/topics/{topic}:publish', self.tokens, body={'messages': [msg]})['messageIds'][0]

    def pull(self, subscription, max_messages):
        res = request('POST', f'{self.base}/subscriptions/{subscription}:pull', self.tokens,
                      body={'maxMessages': max_messages}, timeout=90)
        out = []
        for item in res.get('receivedMessages', []):
            data = item['message'].get('data', '')
            out.append((item['ackId'], json.loads(base64.b64decode(data) or b'{}')))
        return out

    def ack(self, subscription, ack_ids):
        if ack_ids:
            request('POST', f'{self.base}/subscriptions/{subscription}:acknowledge', self.tokens, body={'ackIds': list(ack_ids)})

    def nack(self, subscription, ack_ids):
        if ack_ids:
            request('POST', f'{self.base}/subscriptions/{subscription}:modifyAckDeadline', self.tokens,
                    body={'ackIds': list(ack_ids), 'ackDeadlineSeconds': 0})


# ---------------------------------------------------------- Cloud Storage

class Storage:
    def __init__(self, bucket, tokens):
        self.bucket, self.tokens = bucket, tokens

    def _object(self, name):
        return f'https://storage.googleapis.com/storage/v1/b/{self.bucket}/o/' + urllib.parse.quote(name, safe='')

    def upload(self, name, path, content_type='application/octet-stream', if_absent=True):
        q = {'uploadType': 'media', 'name': name}
        if if_absent: q['ifGenerationMatch'] = '0'
        url = f'https://storage.googleapis.com/upload/storage/v1/b/{self.bucket}/o?' + urllib.parse.urlencode(q)
        with open(path, 'rb') as stream:
            size = stream.seek(0, 2); stream.seek(0)
            return request('POST', url, self.tokens, data=stream, timeout=900,
                           headers={'Content-Type': content_type, 'Content-Length': str(size)})

    def download(self, name, path):
        raw = request('GET', self._object(name) + '?alt=media', self.tokens, timeout=900)
        data = raw if isinstance(raw, bytes) else json.dumps(raw).encode()
        with open(path, 'wb') as out:
            out.write(data)

    def metadata(self, name):
        try:
            return request('GET', self._object(name), self.tokens)
        except NotFound:
            return None

    def list(self, prefix):
        items, token = [], None
        while True:
            q = {'prefix': prefix}
            if token: q['pageToken'] = token
            res = request('GET', f'https://storage.googleapis.com/storage/v1/b/{self.bucket}/o?' + urllib.parse.urlencode(q), self.tokens)
            items += [i['name'] for i in res.get('items', [])]
            token = res.get('nextPageToken')
            if not token: return items


# ------------------------------------------------------------------ Compute

class Compute:
    def __init__(self, tokens):
        self.tokens = tokens

    @staticmethod
    def _url(node):
        return f"https://compute.googleapis.com/compute/v1/projects/{node['project']}/zones/{node['zone']}/instances/{node['instance']}"

    def status(self, node):
        return request('GET', self._url(node), self.tokens)['status']

    def start(self, node):
        return request('POST', self._url(node) + '/start', self.tokens, body={})


def jwt_claims(authorization):
    """Claims of a bearer token already verified by Cloud Run IAM. Never use
    this behind an endpoint that allows unauthenticated invocation."""
    token = authorization.split(' ', 1)[1] if authorization.lower().startswith('bearer ') else ''
    parts = token.split('.')
    if len(parts) != 3:
        return {}
    pad = '=' * (-len(parts[1]) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(parts[1] + pad))
    except ValueError:
        return {}
