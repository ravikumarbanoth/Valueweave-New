"""ValueWeave REST API — read-only HTTP access to the knowledge graph."""

#: Defined before the submodule imports below: `api.app` reads it back out of this
#: partially-initialised module, so reordering these lines reintroduces a circular
#: import.
API_VERSION = "2.2.0"

from api.errors import ApiError                   # noqa: E402
from api.app import Application, create_server    # noqa: E402

__all__ = ["Application", "create_server", "ApiError", "API_VERSION"]
