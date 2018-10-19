from os.path import dirname
from os.path import join

from setuptools import find_packages
from setuptools import setup

with open(join(dirname(__file__), 'README.md')) as readme:
    long_description = readme.read()


def main():
    setup(
        name='flow',
        author='zkksch',
        author_email='stimur94@gmail.com',
        url='https://github.com/zkksch/flow',
        version='0.1.0',
        package_dir={'': 'src'},
        packages=find_packages('src'),
        description=(
            'Simple enum values flow implementation'
        ),
        long_description=long_description,
        long_description_content_type='text/markdown',
        license='MIT License',
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Operating System :: OS Independent'
        ]
    )


if __name__ == '__main__':
    main()
