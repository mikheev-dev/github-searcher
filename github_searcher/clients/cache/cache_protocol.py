from typing import Protocol, Any


class CacheProtocol(Protocol):
    """
    Protocol for cache client.
    """
    async def get(self, *args, **kwargs):
        """
        Get data from cache. Arguments are not specified for support different clients
        """
        raise NotImplementedError

    async def set(self, *args, **kwargs) -> Any:
        """
        Put data for cache. Arguments are not specified for support different clients
        """
        raise NotImplementedError
