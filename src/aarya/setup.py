from setuptools import setup, find_packages

setup(
    name='aarya',
    version='1.0.6',
    
    # This tells Python your code is inside the 'src' folder
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    author="Shaurya Mishra",
    author_email="shaur.codes@gmail.com",
    description="The Advanced OSINT Email Scanner",
    url='https://github.com/forshaur/aarya',
    
    # Dependencies that will be auto-installed
    install_requires=[
        "httpx",
        "requests",
        "beautifulsoup4",
        "browser_cookie3",
        "rich"
    ],
    
    include_package_data=True,
    
  
    entry_points={
        'console_scripts': [
            'aarya = aarya.cli:main'
        ]
    },
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)