from setuptools import setup, find_packages

try:
    import py2exe # to enable py2exe if it's available
    PY2EXE_ENABLED = True
except ImportError:
    PY2EXE_ENABLED = False

setup(
    name='DamBuilder',
    version='1.0',
    author='Faraway (Martijn Faassen, Felicia Wong)',
    author_email='faassen@startifact.com',
    description="Dam Builder",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='GPL',
    install_requires=[
    'setuptools',
    'pyode >= 1.2.0',
#    'pygame >= 1.7.1',
    ],
    # required for py2exe
    windows=[
    {
    'dest_base': 'dambuilder',
    'script': 'dambuilder_game.py',
    'icon_resources': [(1, 'data/dambuilder.ico',)]
    }
    ],
    entry_points= {
    'console_scripts': [
    'dambuilder = dambuilder.main:main',
    ]
    },
)

if PY2EXE_ENABLED:
    import shutil
    # pygame needs this
    shutil.copyfile('freesansbold.ttf', 'dist/freesansbold')
    # dambuilder needs its data
    shutil.copytree('data', 'dist/data')
