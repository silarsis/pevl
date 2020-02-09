from setuptools import setup, find_packages  # type: ignore


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="pevl",
    version="0.0.2",
    packages=find_packages(),
    author="Kevin Littlejohn",
    author_email="kevin@littlejohn.id.au",
    description="Library to handle versions for events",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="event sourcing versioning",
    url="https://github.com/silarsis/pevl",
    python_requires=">=3.8"
)
