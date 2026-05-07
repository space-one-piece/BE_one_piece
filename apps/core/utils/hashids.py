from hashids import Hashids  # type: ignore

from config.settings.base import HASHIDS_SALT

hashids = Hashids(salt=HASHIDS_SALT, min_length=12)


def encode_id(id: int) -> str:
    return str(hashids.encode(id))


def decode_id(id: str) -> int | None:
    decoded = hashids.decode(id)
    return decoded[0] if decoded else None
