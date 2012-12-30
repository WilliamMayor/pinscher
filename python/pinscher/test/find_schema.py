import os


def _walk_up(bottom):
    bottom = os.path.realpath(bottom)

    try:
        names = os.listdir(bottom)
    except Exception:
        return

    dirs, nondirs = [], []
    for name in names:
        if os.path.isdir(os.path.join(bottom, name)):
            dirs.append(name)
        else:
            nondirs.append(name)

    yield bottom, dirs, nondirs

    new_path = os.path.realpath(os.path.join(bottom, '..'))
    if new_path == bottom:
        return

    for x in _walk_up(new_path):
        yield x


def find_schema():
    for current, dirs, files in _walk_up(os.path.dirname(os.path.abspath(__file__))):
        if 'pinscher.schema' in files:
            path = os.path.join(current, 'pinscher.schema')
            if not os.path.islink(path):
                return path
