from hyperx.core.cx_router import CXRouter

def handle_log(parts, payload):
    print("[HANDLE_LOG]", parts, payload)

CXRouter.register("hyperx.logger:log:record:write", handle_log)

CXRouter.dispatch(
    "hyperx.logger:log:0.3:record:write",
    {"msg": "this is a CX log test"}
)
print("Active routes:", CXRouter.list_routes())
