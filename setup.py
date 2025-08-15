import setuptools
from pathlib import Path


PACKAGE_NAME = "synsatipy"


def get_packages(package_name):
    package = Path(package_name)
    packages = [
        str(path.parent).replace("/", ".") for path in package.rglob("__init__.py")
    ]
    return packages


def get_requirements(requirements_filename):
    requirements_file = Path(__file__).parent / requirements_filename
    assert requirements_file.exists()
    with open(requirements_file) as f:
        requirements = [
            line.strip() for line in f.readlines() if not line.startswith("#")
        ]
    # Iris has a different name on PyPI...
    if "iris" in requirements:
        requirements.remove("iris")
        requirements.append("scitools-iris")
    return requirements



with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name=PACKAGE_NAME,
    version="v1.0.1",
    author="Fabian Senf",
    author_email="senf@tropos.de",
    packages=get_packages(PACKAGE_NAME),
    description="SynsatiPy supports calculation of synthetic satellite images.",
    long_description=description,
#    long_description_content_type=description,
#    url="https://github.com/gituser/test-tackage",
    license="GPL-v3",
    python_requires=">=3.8",
    install_requires=get_requirements("requirements.txt"),
    test_requires=["pytest"],
)
