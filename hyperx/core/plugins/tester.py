from hyperx.core.cx_router import CXRouter

# simulate loading routes
import hyperx.core.plugins.logger_cx_routes

print("Routes:", CXRouter.list_routes())

CXRouter.dispatch(
    "hyperx.logger:log:0.3:record:write",
    {"msg": "vector test OK"}
)
CXRouter.dispatch(
    "hyperx.worker:alert:0.9:monitor:restart",
    {"reason": "manual trigger"}
)
