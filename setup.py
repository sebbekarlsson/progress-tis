from distutils.core import setup
import setuptools


setup(
    name='progress-tis',
    version='1.0',
    install_requires=[
        'pyfiglet'
    ],
    packages=[
        'tis'
    ],
    entry_points={
        "console_scripts": [
            "tis-auth = tis.entry_points:login",
            "tis-courses = tis.entry_points:get_courses",
            "tis-assignments = tis.entry_points:get_assignments",
            "tis-msg = tis.entry_points:send_msg"
        ]
    },
   )
