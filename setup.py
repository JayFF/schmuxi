from setuptools import setup, find_packages

setup(name='schmuxi',
        version='0.1',
        description='Helps you evaluate spectroscopy-data and organize its documentation. Specially designed for Laserspectroscopy of 2D-materials.',
        url='https://github.com/JayFF/schmuxi',
        author='Jonathan Foerste',
        author_email='tv@in-hd.de',
        licence='MIT',
        packages=find_packages(),
        install_requires=['numpy','scipy','pandas','pyyaml'],
        include_package_data=True,
        zip_safe=False)
