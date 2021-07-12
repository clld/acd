from pathlib import Path

from clld.web.assets import environment

import acd


environment.append_path(
    Path(acd.__file__).parent.joinpath('static').as_posix(),
    url='/acd:static/')
environment.load_path = list(reversed(environment.load_path))
