"legal document system"

__version__ = "1.0.0"


try:
    import pluggy 

    # Marker to be imported and used in pluggins (and for own implementations)
    hookimpl = pluggy.HookimplMarker('LDS')
except ImportError:
    pass