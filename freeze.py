from cx_Freeze import setup, Executable

icons = ['edit', 'lock', 'qrcode', 'search',
         'trash', 'user', 'copy', 'save', 'plus']

executables = [
    Executable("scripts/cli.py", targetName='pinscher'),
    Executable("scripts/alfred/filter.py"),
    Executable("scripts/alfred/action.py"),
]

buildOptions = dict(
    compressed=True,
    packages=['Crypto', 'sqlite3', 'alp', 'qrcode', 'tempfile', 'PIL'],
    include_files=['scripts/alfred/resources/%s.png' % i for i in icons]
)

setup(
    name="pinscher",
    version="0.3dev",
    description="Password management tool",
    options=dict(build_exe=buildOptions),
    executables=executables
)
