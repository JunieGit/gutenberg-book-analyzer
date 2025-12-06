# Project Gutenberg Book Analyzer

**Author**: Min Htet Khant
**Course**: CIS-117-HYA-CRN98242  
**Semester**: Fall 2025  
**Date**: December 5, 2025

## Description

A Python desktop application that allows users to search and analyze books from Project Gutenberg's free library. The application downloads book text, analyzes word frequencies, filters out common stopwords, and stores results in a local SQLite database for quick retrieval.

## Features

- **Local Database Search**: Search previously analyzed books by title
- **Web Scraping**: Download books directly from Project Gutenberg URLs
- **Word Frequency Analysis**: Identifies and displays the top 10 most frequent meaningful words
- **Stopword Filtering**: Removes common words (articles, prepositions, pronouns) for meaningful results
- **Data Persistence**: Stores book titles and word frequencies in SQLite database
- **User-Friendly GUI**: Clean Tkinter interface with status updates and error handling
- **Error Handling**: Comprehensive try/except blocks prevent crashes

## Technologies Used

- **Python 3.x**
- **SQLite3** - Database management
- **Tkinter** - Graphical user interface
- **urllib** - Web scraping from Project Gutenberg
- **Regular Expressions (re)** - Text processing
- **Collections.Counter** - Efficient word frequency counting

## Installation & Setup

1. **Clone this repository:**
```bash
   git clone https://github.com/JunieGit/gutenberg-book-analyzer.git
   cd gutenberg-book-analyzer
```

2. **Ensure Python 3.x is installed**

3. **Run the application:**
```bash
   python final.py
```

## How to Use

### Fetching a New Book:
1. Paste a Project Gutenberg plain text URL in the "Gutenberg URL" field
2. Click "Fetch & Analyze."
3. Wait for the download and analysis to complete
4. View the top 10 most frequent words

### Searching Local Database:
1. Enter a book title in the "Book Title" field
2. Click "Search Database."
3. Results appear instantly from local storage

## Example Project Gutenberg URLs

- **Little Women**: https://www.gutenberg.org/cache/epub/37106/pg37106.txt
- **Pride and Prejudice**: https://www.gutenberg.org/files/1342/1342-0.txt
- **Alice in Wonderland**: https://www.gutenberg.org/files/11/11-0.txt
- **Frankenstein**: https://www.gutenberg.org/files/84/84-0.txt
- **Moby Dick**: https://www.gutenberg.org/files/2701/2701-0.txt

## Project Structure
```
gutenberg-book-analyzer/
├── final.py          # Main application file
├── books.db          # SQLite database (auto-generated)
└── README.md         # Project documentation
```

## Code Highlights

### Database Structure
- **books table**: Stores book titles and URLs
- **word_frequency table**: Stores words and their frequencies, linked to books via foreign key

### Stopword Filtering
Filters out 60+ common English words including articles (the, a, an), prepositions (in, on, at), and pronouns (I, you, he, she) to provide meaningful analysis results.

### Error Handling
Comprehensive try/except blocks handle:
- Network errors during download
- Database connection issues
- Missing books in the database
- Invalid URLs

## Requirements Met

This project fulfills all requirements for the CIS-117 Final Project:

✅ Uses WWW API (urllib) for web scraping  
✅ Tkinter-based GUI  
✅ SQLite3 database integration  
✅ Searches local database for book titles  
✅ Displays the top 10 most frequent words with frequencies  
✅ Fetches books from Project Gutenberg by URL  
✅ Filters stopwords (articles, prepositions, etc.)  
✅ Exception handling with try/except  
✅ All methods documented with docstrings  
✅ Header comments with description, name, and date  

## License

This project was created as a class assignment for educational purposes.

## Acknowledgments

- Project Gutenberg for providing free access to thousands of books
- CIS-117 course materials and instruction
```
