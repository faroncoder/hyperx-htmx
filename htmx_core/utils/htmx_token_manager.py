from django.conf import settings

# Use environment-aware prefix injected by HTMXCoreConfig.ready()
PREFIX = getattr(settings, "HTMX_CACHE_PREFIX", "hyperx:htmx:")


def get_cache_key(token):
	return f"{PREFIX}token:{token}"

def get_registry_key(user_id, session_key):
	return f"{PREFIX}registry:{user_id}:{session_key}"

def get_push_key(connection_id):
	return f"{PREFIX}wss_push:{connection_id}"




