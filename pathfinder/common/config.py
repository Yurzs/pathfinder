from pathfinder.common.middleware.middleware import MiddlewareList
from pathfinder.common.middleware.edns.middleware import EDNSMiddleware
from pathfinder.common.middleware.cache import CacheMiddleware

middlewares = MiddlewareList(EDNSMiddleware, CacheMiddleware)
