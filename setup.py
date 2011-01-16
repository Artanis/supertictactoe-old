try:
    from setuptools import setup
except:
    from distutils.core import setup

config =  {
    'name': "supertictactoe"
    'description': "",
    'version': "0.0.0",
    'author': "Erik Youngren",
    'author_email': "youngren.erik@gmail.com",
    'url': None,
    'download_url': None,
    'install_requires': [],
    'packages': ["supertictactoe"],
    'scripts': [],
}

setup(**config)

