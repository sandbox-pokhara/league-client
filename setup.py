import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="league-client",
    version="1.0.49",
    author="Pradish Bijukchhe",
    author_email="pradishbijukchhe@gmail.com",
    description="Python package to communicate with riot client and league client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sandbox-pokhara/league-client",
    project_urls={
        "Bug Tracker": "https://github.com/sandbox-pokhara/league-client/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    package_dir={"": "."},
    package_data={"league_client": ["*.json"]},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "league-connection",
        "psutil",
        "aiohttp",
        "ucaptcha>=1.0.2",
    ],
)
