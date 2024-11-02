import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MovieRecommender", 
    version="2.0.1",
    author="Aditya, Bahare, Monish",
    author_email="asingh78@ncsu.edu",
    description="A collaborative filtering-based movie recommendation engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/git-ankit/MovieRecommender",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Video",
    ],
    install_requires=[
        "flask", 
        "flask-mail",
        "flask-cors",
        "pytest",
        "os",
        # Add other dependencies here as needed
    ],
    python_requires=">=3.6",
)
