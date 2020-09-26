from pathfinder.common.middleware.middleware import MiddlewareList
from pathfinder.common.middleware.edns.middleware import EDNSMiddleware

middlewares = MiddlewareList(EDNSMiddleware)
