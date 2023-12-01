"legal document system"

__version__ = "1.0.0"

import sys
import os 
import os.path as osp

package_dir = osp.abspath(osp.dirname(__file__))



try:
    import pluggy 
    # Marker to be imported and used in pluggins (and for own implementations)
    hookimpl = pluggy.HookimplMarker('LDS')
except ImportError:
    pass