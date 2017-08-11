from datetime import datetime
from itertools import izip
from typing import Any, Callable, IO, MutableMapping, Optional, Text, Tuple, Union

PY2 = ...  # type: bool
text_type = unicode
int_to_byte = chr
number_types = (int, long, float)

bytes_like = Union[bytearray, str]

class _CompactJSON:
    def loads(self, payload: Text) -> Any: ...
    def dumps(self, obj: Any) -> Text: ...

compact_json = _CompactJSON
EPOCH = ...  # type: int

def want_bytes(s: str, encoding='', errors='') -> str: ...
def is_text_serializer(serializer: Any) -> bool: ...
def constant_time_compare(val1: bytes_like, val2: bytes_like) -> bool: ...

class BadData(Exception):
    message = ...  # type: str
    def __init__(self, message: str) -> None: ...

class BadPayload(BadData):
    original_error = ...  # type: Optional[Exception]
    def __init__(self, message: str, original_error: Optional[Exception]=None) -> None: ...

class BadSignature(BadData):
    payload = ...  # type: Optional[Any]
    def __init__(self, message: str, payload: Optional[Any]=None) -> None: ...

class BadTimeSignature(BadSignature):
    date_signed = ...  # type: Optional[int]
    def __init__(self, message, payload: Optional[Any]=None, date_signed: Optional[int]=None) -> None: ...

class BadHeader(BadSignature):
    header = ...  # type: Any
    original_error = ...  # type: Any
    def __init__(self, message, payload=None, header=None, original_error=None) -> None: ...

class SignatureExpired(BadTimeSignature): ...

def base64_encode(string: bytes_like) -> str: ...
def base64_decode(string: bytes_like) -> str: ...
def int_to_bytes(num: int) -> str: ...
def bytes_to_int(bytestr: bytes_like) -> int: ...

class SigningAlgorithm:
    def get_signature(self, key: bytes_like, value: bytes_like) -> str: ...
    def verify_signature(self, key: bytes_like, value: bytes_like, sig: bytes_like) -> bool: ...

class NoneAlgorithm(SigningAlgorithm):
    def get_signature(self, key: bytes_like, value: bytes_like) -> str: ...

class HMACAlgorithm(SigningAlgorithm):
    default_digest_method = ...  # type: Callable
    digest_method = ...  # type: Callable
    def __init__(self, digest_method: Optional[Callable]=None) -> None: ...
    def get_signature(self, key: bytes_like, value: bytes_like) -> str: ...

class Signer:
    default_digest_method = ...  # type: Callable
    default_key_derivation = ...  # type: str
    secret_key = ...  # type: bytes_like
    sep = ...  # type: str
    salt = ...  # type: bytes_like
    key_derivation = ...  # type: str
    digest_method = ...  # type: Callable
    algorithm = ...  # type: SigningAlgorithm
    def __init__(self, secret_key: bytes_like, salt: Optional[bytes_like]=None, sep: Optional[str]='',
                 key_derivation: Optional[str]=None,
                 digest_method: Optional[Callable]=None,
                 algorithm: Optional[SigningAlgorithm]=None) -> None: ...
    def derive_key(self) -> str: ...
    def get_signature(self, value: bytes_like) -> str: ...
    def sign(self, value: bytes_like) -> str: ...
    def verify_signature(self, value: bytes_like, sig: bytes_like) -> bool: ...
    def unsign(self, signed_value: str) -> str: ...
    def validate(self, signed_value: str) -> bool: ...

class TimestampSigner(Signer):
    def get_timestamp(self) -> int: ...
    def timestamp_to_datetime(self, ts: int) -> datetime: ...
    def sign(self, value: bytes_like) -> str: ...
    def unsign(self, value: str, max_age: Optional[int]=None, return_timestamp=False) -> Any: ...
    def validate(self, signed_value: str, max_age: Optional[int]=None) -> bool: ...

class Serializer:
    default_serializer = ...  # type: Any
    default_signer = ...  # type: Callable[..., Signer]
    secret_key = ...  # type: Any
    salt = ...  # type: bytes_like
    serializer = ...  # type: Any
    is_text_serializer = ...  # type: bool
    signer = ...  # type: Signer
    signer_kwargs = ...  # type: MutableMapping
    def __init__(self, secret_key: bytes_like, salt: Optional[bytes_like]=b'', serializer=None, signer: Optional[Callable[..., Signer]]=None, signer_kwargs: Optional[MutableMapping]=None) -> None: ...
    def load_payload(self, payload: Any, serializer=None) -> Any: ...
    def dump_payload(self, *args, **kwargs) -> str: ...
    def make_signer(self, salt: Optional[bytes_like]=None) -> Signer: ...
    def dumps(self, obj: Any, salt: Optional[bytes_like]=None) -> str: ...
    def dump(self, obj: Any, f: IO[str], salt: Optional[bytes_like]=None) -> None: ...
    def loads(self, s: str, salt: Optional[bytes_like]=None) -> Any: ...
    def load(self, f: IO[str], salt: Optional[bytes_like]=None): ...
    def loads_unsafe(self, s, salt: Optional[bytes_like]=None) -> Tuple[bool, Any]: ...
    def load_unsafe(self, f: IO[str], *args, **kwargs) -> Tuple[bool, Any]: ...

class TimedSerializer(Serializer):
    default_signer = ...  # type: Callable[..., TimestampSigner]
    def loads(self, s: str, salt: Optional[bytes_like]=None, max_age: Optional[int]=None, return_timestamp=False) -> Any: ...
    def loads_unsafe(self, s: str, salt: Optional[bytes_like]=None, max_age: Optional[int]=None) -> Tuple[bool, Any]: ...

class JSONWebSignatureSerializer(Serializer):
    jws_algorithms = ...  # type: MutableMapping[str, SigningAlgorithm]
    default_algorithm = ...  # type: str
    default_serializer = ...  # type: Any
    algorithm_name = ...  # type: str
    algorithm = ...  # type: Any
    def __init__(self, secret_key: bytes_like, salt: Optional[bytes_like]=None, serializer=None, signer: Optional[Callable[..., Signer]]=None, signer_kwargs: Optional[MutableMapping]=None, algorithm_name: Optional[str]=None) -> None: ...
    def load_payload(self, payload: Any, return_header=False) -> Any: ...
    def dump_payload(self, *args, **kwargs) -> str: ...
    def make_algorithm(self, algorithm_name: str) -> SigningAlgorithm: ...
    def make_signer(self, salt: Optional[bytes_like]=None, algorithm_name: Optional[str]=None) -> Signer: ...
    def make_header(self, header_fields=Optional[MutableMapping]) -> MutableMapping: ...
    def dumps(self, obj: Any, salt: Optional[bytes_like]=None, header_fields=Optional[MutableMapping]) -> str: ...
    def loads(self, s: str, salt: Optional[bytes_like]=None, return_header=False) -> Any: ...
    def loads_unsafe(self, s, salt: Optional[bytes_like]=None, return_header=False) -> Tuple[bool, Any]: ...

class TimedJSONWebSignatureSerializer(JSONWebSignatureSerializer):
    DEFAULT_EXPIRES_IN = ...  # type: int
    expires_in = ...  # type: int
    def __init__(self, secret_key: bytes_like, expires_in: Optional[int]=None, **kwargs) -> None: ...
    def make_header(self, header_fields=Optional[MutableMapping]) -> MutableMapping: ...
    def loads(self, s: str, salt: Optional[bytes_like]=None, return_header=False) -> Any: ...
    def get_issue_date(self, header: MutableMapping) -> Optional[datetime]: ...
    def now(self) -> int: ...

class URLSafeSerializerMixin:
    def load_payload(self, payload: Any, serializer=None, return_header=False, **kwargs) -> Any: ...  # FIXME: This is invalid but works around https://github.com/pallets/itsdangerous/issues/74
    def dump_payload(self, *args, **kwargs) -> str: ...

class URLSafeSerializer(URLSafeSerializerMixin, Serializer):
    default_serializer = ...  # type: Any

class URLSafeTimedSerializer(URLSafeSerializerMixin, TimedSerializer):
    default_serializer = ...  # type: Any
