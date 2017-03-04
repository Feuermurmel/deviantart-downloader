import setuptools


setuptools.setup(
    name='ponydl',
    version='0.1',
    packages=setuptools.find_packages(),
    install_requires=['beautifulsoup4', 'requests', 'unidecode'],
    entry_points=dict(
        console_scripts=[
            'ponydl = ponydl:script_main']))
