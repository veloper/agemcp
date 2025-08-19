from collections import OrderedDict
from typing import Callable, Generic, Tuple, TypeVar


K = TypeVar('K')
V = TypeVar('V')

class LRUCache(Generic[K, V]):
    """
    An in-memory Least Recently Used (LRU) cache for key-value pairs, supporting arbitrary types via generics.

    This class is generic over key and value types, using Python's TypeVar and Generic constructs.
    You can instantiate LRUCache for any combination of key and value types, ensuring type safety
    and flexibility (e.g., LRUCache[str, int], LRUCache[int, MyCustomType], etc).

    The cache maintains a fixed-size mapping, evicting the least recently accessed item when full.
    Accessing or inserting a key marks it as most recently used. This is useful for optimizing
    memory usage and keeping only the most relevant items available.

    Typical use cases include memoization, caching expensive computations, or limiting resource usage
    in applications that process large datasets.

    Type Parameters:
        K: Type of cache keys.
        V: Type of cache values.

    Attributes:
        max_size (int): Maximum number of items to store in the cache.
    """

    def __init__(self, max_size: int = 100):
        self._cache : OrderedDict[K, V] = OrderedDict()
        self.max_size = max_size

    def get(self, key: K) -> V | None:
        if key not in self._cache:
            return None
        self._cache.move_to_end(key) # magic (use the move_to_end unique to OrderedDict as a way to indicate recent access)
        return self._cache[key]

    def put(self, key: K, value: V) -> None:
        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)
        self._cache[key] = value

    def clear(self, filter: Callable[[Tuple[K, V]], bool] | None = None) -> None:
        """Clear the cache, optionally filtering which items to evict.
        
        None == clear all items.
        """
        if filter is None:
            self._cache.clear()
        else:
            keys_to_remove = [key for key, value in self._cache.items() if filter((key, value))]
            for key in keys_to_remove:
                del self._cache[key]

