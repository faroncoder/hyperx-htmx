
import pytest
from django.core.cache import cache

@pytest.mark.django_db
def test_tab_mapping_cache_bootstrap(htmx_client):
    """Confirm tab mapping built and cached."""
    mapping = cache.get("dynamic_tab_mapping")
    assert mapping is not None, "Tab mapping not cached at startup"
    assert isinstance(mapping, dict)
    assert len(mapping) > 0
