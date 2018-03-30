import re
import os

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name="musombi-notifications",
    version="1.0",
    description="Portable fcm notifcations musombi style",
    long_description="You shall do this",
    author="Christian Musombi",
    author_email="xtain@bruce.com",
    url="https://github.com/MusombiC/Notifications",
    download_url="https://github.com/MusombiC/Notifications.git",
    license="MIT License",
    packages=[
        "musombi_notifications",
    ],
    include_package_data=True,
    install_requires=[
        "Django>=1.7.0",
        "django-fcm>=0.1.1"
    ],
    tests_require=[
        "nose",
        "coverage",
    ],
    zip_safe=False,
    test_suite="tests.runtests.start",
    classifiers=[
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)