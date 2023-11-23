"legal document system"

__version__ = "1.0.0"

import sys
import os 
import os.path as osp
current_path = os.getcwd()
# package_dir = osp.dirname(current_path)
# sys.path.append(package_dir)
# print("1:", package_dir)
# print("2:",os.path.abspath(os.path.dirname(__name__)))

try:
    import pluggy 

    # Marker to be imported and used in pluggins (and for own implementations)
    hookimpl = pluggy.HookimplMarker('LDS')
except ImportError:
    pass