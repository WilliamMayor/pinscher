from cx_Freeze import setup, Executable

executables = [
    Executable("pinscher/scripts/cli.py")
]

buildOptions = dict(
    compressed=True,
    packages=['Crypto', 'sqlite3']
)

setup(
    name="pinscher",
    version="0.2dev",
    description="Password management tool",
    options=dict(build_exe=buildOptions),
    executables=executables
)
