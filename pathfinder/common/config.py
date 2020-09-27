from pathfinder.common.middleware.cache import CacheMiddleware
from pathfinder.common.middleware.edns.middleware import EDNSMiddleware
from pathfinder.common.middleware.middleware import MiddlewareList

middlewares = MiddlewareList(EDNSMiddleware, CacheMiddleware)
