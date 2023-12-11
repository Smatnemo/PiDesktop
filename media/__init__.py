import os.path as osp


def get_filename(name):
    return osp.join(osp.dirname(osp.abspath(__file__)), 'assets', name)