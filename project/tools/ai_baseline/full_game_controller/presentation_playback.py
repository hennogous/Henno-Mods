"""Install bounded shipped-popup acknowledgements on this controller instance.

No game I/O or activation occurs on import/install. Calls preserve the existing
release path, then NaturalWonder, then a fresh ProjectBuilt proof. Installation
is idempotent, including callers that separately opted into NaturalWonder.
"""
from .natural_wonder_guard import install as install_natural_wonder
from .project_built_guard import install as install_project_built


def install(controller):
    install_natural_wonder(controller)
    install_project_built(controller)
    return controller
