# sales-reporting-tool

A Python-based tool designed to generate customizable sales reports by querying SQL databases and processing transaction data. This tool facilitates the creation of detailed sales reports with flexible grouping and filtering options.

## Features

- Generates sales reports from SQL Server data.
- Customizable grouping and filtering of sales transactions.
- Modular design with classes to handle initial parameters, transaction dataframes, and custom dataframes.
- Logging support for tracking operations.

## Tech Stack

- Python 3
- pandas for data manipulation
- pyodbc for SQL Server connectivity
- logging for application logging

## Getting Started

### Prerequisites

- Python 3.x installed
- Access to a SQL Server database with required sales data
- Required Python packages:

```bash
pip install pandas pyodbc openpyxl
```

### Installation

Clone the repository:

```bash
git clone https://github.com/justin-napolitano/sales-reporting-tool.git
cd sales-reporting-tool
```

### Running

Run the main sales report script (example):

```bash
python JNAP_testing_report_builder_tool/test_report_tool-2.6.py
```

Adjust SQL connection parameters and input files as needed.

## Project Structure

- `JNAP_stable_report_builder_tool/`: Contains stable versions of report builder scripts.
- `JNAP_testing_report_builder_tool/`: Contains testing and development versions of report builder scripts.
- `labels.txt`: List of labels, likely used for filtering or categorization.
- `README.md`: This documentation file.

## Future Work / Roadmap

- Add comprehensive documentation and usage examples.
- Implement unit tests for core classes and functions.
- Enhance user interaction for dynamic report customization.
- Expand support for other report types beyond sales.
- Improve error handling and logging detail.
- Optimize SQL queries and data processing for performance.
