import os
from distutils.command.build import build

from django.core import management
from setuptools import find_packages, setup

try:
    with open(
            os.path.join(os.path.dirname(__file__), "README.rst"), encoding="utf-8"
    ) as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""


class CustomBuild(build):
    def run(self):
        management.call_command("compilemessages", verbosity=1)
        build.run(self)


cmdclass = {"build": CustomBuild}

setup(
    name="pretalx-halfnarp",
    version="1.0.0",
    description="Pretalx-Halfnarp is a Plugin that helps you to estimate the interest in your submissions and plan "
                "room-sizes accordingly by scheduling the most requested submissions into the larger rooms. It can "
                "also help you avoid overlaps by correlating submissions that are preferred by the same people so "
                "that you can plan them at different times."
                ""
                "Halfnarp is an anagram of Fahrplan, a not-yet sorted Fahrplan",
    long_description=long_description,
    url="https://github.com/seibert-media/pretalx-halfnarp",
    author="Peter Körner",
    author_email="pkoerner@seibert-media.net",
    license="Apache Software License",
    install_requires=[
        "jsonschema"
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretalx.plugin]
pretalx_halfnarp=pretalx_halfnarp:PretalxPluginMeta
""",
)
