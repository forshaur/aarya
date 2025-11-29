# Project Title: Aarya - OSINT Email Scanner

## Description
Aarya is an OSINT (Open Source Intelligence) email scanner that checks the existence of an email address across various platforms. It utilizes multiple modules to interact with services like Amazon, Flipkart, Duolingo, Spotify, Instagram, Twitter, Wattpad, Gmail, and ProtonMail.

## Features
- Scans email addresses for existence across multiple platforms.
- Provides detailed output on the status of the email address.
- Supports asynchronous requests for faster performance.

## Installation
To install the required dependencies, run:

```
pip install -r requirements.txt
```

## Usage
To use the Aarya email scanner, run the following command in your terminal:

```
python -m aarya.cli <email_address>
```

You can also specify an output file to save the results:

```
python -m aarya.cli <email_address> -o output.json
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Thanks to the developers of the libraries used in this project.
- Special thanks to the open-source community for their contributions.