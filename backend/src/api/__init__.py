"""
Taxini API package.

This package is a placeholder to organize versioned API modules (e.g., `v1`, `v2`).
Implementations (routers, endpoints) should live in subpackages such as `taxini.api.v1`.

Intentionally left minimal; no application logic should be added here.
"""

# Explicitly export nothing at the package root. Subpackages (e.g., `v1`) will be discovered and used by the app.
__all__: list[str] = []
