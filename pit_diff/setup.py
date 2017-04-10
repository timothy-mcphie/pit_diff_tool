from setuptools import setup, find_packages

from pit_diff import VERSION

setup(
        name='pit_diff',
        version=VERSION,
        description="Get the diff of two pitest xml reports",
        author='Timothy McPhie',
        author_email='mcphietimothy65@gmail.com',
        url='http://github.com/timothy-mcphie/pit_diff_tool',
        license='MIT',
        packages=find_packages()
    )
