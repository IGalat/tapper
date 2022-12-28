from setuptools import find_namespace_packages
from setuptools import setup


def main() -> None:
    setup(packages=find_namespace_packages(where="src"))


if __name__ == "__main__":
    main()
