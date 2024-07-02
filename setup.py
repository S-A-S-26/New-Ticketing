from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in ticketing/__init__.py
from ticketing import __version__ as version

setup(
	name="ticketing",
	version=version,
	description="Process tracking",
	author="Dexciss",
	author_email="ssutar@dexciss.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
