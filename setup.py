import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = ['pyramid', 'WebError', 'sqlalchemy', 'pymongo', 'zope.sqlalchemy',
    'zope.interface', 'colander', 'py-bcrypt']
test_requires = requires + ["mock", "webtest"]

setup(name='pyramid_registration',
      version='0.0',
      description='pyramid_registration',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      test_suite="pyramid_registration",
      entry_points = """\
      [paste.app_factory]
      main = pyramid_registration:main
      """,
      paster_plugins=['pyramid'],
      )

