"""
Project Gutenberg Book Analyzer
Author: Min Htet Khant
Date: December 5, 2025

Description:
This application allows users to search for books in a local database and retrieve
the top 10 most frequent words. It also enables searching Project Gutenberg's library
by URL to download books, analyze word frequencies, and store results locally.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import urllib.request
import re
from collections import Counter


class BookAnalyzerDB:
    """Database handler for storing and retrieving book information."""
    
    def __init__(self, db_name="books.db"):
        """
        Initialize database connection and create tables if they don't exist.
        
        Args:
            db_name (str): Name of the SQLite database file
        """
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Create necessary tables for storing book data."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                url TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS word_frequency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                word TEXT NOT NULL,
                frequency INTEGER NOT NULL,
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
        ''')
        self.conn.commit()
    
    def add_book(self, title, url, word_frequencies):
        """
        Add a book and its word frequencies to the database.
        
        Args:
            title (str): Book title
            url (str): Project Gutenberg URL
            word_frequencies (list): List of tuples (word, frequency)
        """
        try:
            # Insert book
            self.cursor.execute('INSERT INTO books (title, url) VALUES (?, ?)', (title, url))
            book_id = self.cursor.lastrowid
            
            # Insert word frequencies
            for word, freq in word_frequencies:
                self.cursor.execute(
                    'INSERT INTO word_frequency (book_id, word, frequency) VALUES (?, ?, ?)',
                    (book_id, word, freq)
                )
            
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Book already exists, update it
            return self.update_book(title, url, word_frequencies)
        except Exception as e:
            print(f"Error adding book: {e}")
            return False
    
    def update_book(self, title, url, word_frequencies):
        """
        Update existing book's word frequencies.
        
        Args:
            title (str): Book title
            url (str): Project Gutenberg URL
            word_frequencies (list): List of tuples (word, frequency)
        """
        try:
            # Get book ID
            self.cursor.execute('SELECT id FROM books WHERE title = ?', (title,))
            result = self.cursor.fetchone()
            if result:
                book_id = result[0]
                
                # Delete old word frequencies
                self.cursor.execute('DELETE FROM word_frequency WHERE book_id = ?', (book_id,))
                
                # Insert new word frequencies
                for word, freq in word_frequencies:
                    self.cursor.execute(
                        'INSERT INTO word_frequency (book_id, word, frequency) VALUES (?, ?, ?)',
                        (book_id, word, freq)
                    )
                
                # Update URL if provided
                if url:
                    self.cursor.execute('UPDATE books SET url = ? WHERE id = ?', (url, book_id))
                
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating book: {e}")
            return False
    
    def search_book(self, title):
        """
        Search for a book by title and retrieve top 10 word frequencies.
        
        Args:
            title (str): Book title to search for
            
        Returns:
            list: List of tuples (word, frequency) or None if not found
        """
        try:
            self.cursor.execute('SELECT id FROM books WHERE title LIKE ?', (f'%{title}%',))
            result = self.cursor.fetchone()
            
            if result:
                book_id = result[0]
                self.cursor.execute('''
                    SELECT word, frequency 
                    FROM word_frequency 
                    WHERE book_id = ? 
                    ORDER BY frequency DESC 
                    LIMIT 10
                ''', (book_id,))
                return self.cursor.fetchall()
            return None
        except Exception as e:
            print(f"Error searching book: {e}")
            return None
    
    def close(self):
        """Close database connection."""
        self.conn.close()


class TextAnalyzer:
    """Handles text processing and word frequency analysis."""
    
    # Common English stopwords to filter out
    STOPWORDS = {
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them',
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
        'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is',
        'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'should', 'could',
        'may', 'might', 'must', 'can', 'that', 'this', 'these',
        'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
        'what', 'which', 'who', 'when', 'where', 'why', 'how',
        'all', 'each', 'every', 'both', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only',
        'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
        'just', 'now', 'also', 'then', 'there', 'here'
    }
    
    @staticmethod
    def download_text(url):
        """
        Download text from Project Gutenberg URL.
        
        Args:
            url (str): URL of the book
            
        Returns:
            str: Downloaded text content
        """
        try:
            with urllib.request.urlopen(url) as response:
                text = response.read().decode('utf-8')
            return text
        except Exception as e:
            raise Exception(f"Error downloading text: {e}")
    
    @staticmethod
    def extract_title_from_text(text):
        """
        Extract book title from Project Gutenberg text.
        
        Args:
            text (str): Full text content
            
        Returns:
            str: Extracted title or "Unknown Title"
        """
        lines = text.split('\n')
        for line in lines[:50]:  # Check first 50 lines
            if 'Title:' in line:
                return line.split('Title:')[1].strip()
        return "Unknown Title"
    
    @classmethod
    def analyze_text(cls, text):
        """
        Analyze text and return top 10 most frequent words.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            list: List of tuples (word, frequency) for top 10 words
        """
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-z]+\b', text.lower())
        
        # Filter out stopwords and short words
        filtered_words = [
            word for word in words 
            if word not in cls.STOPWORDS and len(word) > 2
        ]
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Return top 10
        return word_counts.most_common(10)


class BookAnalyzerGUI:
    """Main GUI application for the Book Analyzer."""
    
    def __init__(self, root):
        """
        Initialize the GUI application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Project Gutenberg Book Analyzer")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        self.db = BookAnalyzerDB()
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Project Gutenberg Book Analyzer",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Local Database Search Section
        ttk.Label(
            main_frame, 
            text="Search Local Database:",
            font=('Arial', 11, 'bold')
        ).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        ttk.Label(main_frame, text="Book Title:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(main_frame, width=50)
        self.title_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.search_db_btn = ttk.Button(
            main_frame,
            text="Search Database",
            command=self.search_local_database
        )
        self.search_db_btn.grid(row=2, column=2, padx=(10, 0), pady=5)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20
        )
        
        # Project Gutenberg Search Section
        ttk.Label(
            main_frame,
            text="Add Book from Project Gutenberg:",
            font=('Arial', 11, 'bold')
        ).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        ttk.Label(main_frame, text="Gutenberg URL:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.fetch_btn = ttk.Button(
            main_frame,
            text="Fetch & Analyze",
            command=self.fetch_and_analyze
        )
        self.fetch_btn.grid(row=5, column=2, padx=(10, 0), pady=5)
        
        # Example URL
        example_label = ttk.Label(
            main_frame,
            text="Example: https://www.gutenberg.org/cache/epub/37106/pg37106.txt",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        )
        example_label.grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Results Section
        ttk.Label(
            main_frame,
            text="Top 10 Most Frequent Words:",
            font=('Arial', 11, 'bold')
        ).grid(row=7, column=0, columnspan=3, sticky=tk.W, pady=(20, 10))
        
        # Results display with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            main_frame,
            height=15,
            width=70,
            font=('Courier', 10),
            wrap=tk.WORD
        )
        self.results_text.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure row weights for resizing
        main_frame.rowconfigure(8, weight=1)
    
    def search_local_database(self):
        """Search for a book in the local database and display results."""
        title = self.title_entry.get().strip()
        
        if not title:
            messagebox.showwarning("Input Required", "Please enter a book title to search.")
            return
        
        try:
            self.status_var.set(f"Searching for '{title}'...")
            self.root.update()
            
            results = self.db.search_book(title)
            
            if results:
                self.display_results(title, results)
                self.status_var.set(f"Found results for '{title}'")
            else:
                messagebox.showinfo(
                    "Book Not Found",
                    f"Book '{title}' was not found in the local database.\n\n"
                    "Try fetching it from Project Gutenberg using the URL field."
                )
                self.status_var.set("Book not found")
                self.results_text.delete(1.0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while searching: {str(e)}")
            self.status_var.set("Error occurred")
    
    def fetch_and_analyze(self):
        """Fetch book from Project Gutenberg, analyze it, and save to database."""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Input Required", "Please enter a Project Gutenberg URL.")
            return
        
        try:
            self.status_var.set("Downloading book from Project Gutenberg...")
            self.root.update()
            
            # Download text
            text = TextAnalyzer.download_text(url)
            
            self.status_var.set("Analyzing word frequencies...")
            self.root.update()
            
            # Extract title
            title = TextAnalyzer.extract_title_from_text(text)
            
            # Analyze text
            word_frequencies = TextAnalyzer.analyze_text(text)
            
            self.status_var.set("Saving to database...")
            self.root.update()
            
            # Save to database
            success = self.db.add_book(title, url, word_frequencies)
            
            if success:
                self.display_results(title, word_frequencies)
                self.status_var.set(f"Successfully added '{title}' to database")
                messagebox.showinfo(
                    "Success",
                    f"Book '{title}' has been successfully analyzed and saved to the database!"
                )
            else:
                messagebox.showerror("Error", "Failed to save book to database.")
                self.status_var.set("Error saving to database")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred")
    
    def display_results(self, title, word_frequencies):
        """
        Display word frequency results in the text widget.
        
        Args:
            title (str): Book title
            word_frequencies (list): List of tuples (word, frequency)
        """
        self.results_text.delete(1.0, tk.END)
        
        # Header
        self.results_text.insert(tk.END, f"Book: {title}\n")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # Results
        self.results_text.insert(tk.END, f"{'Rank':<6} {'Word':<20} {'Frequency':<10}\n")
        self.results_text.insert(tk.END, "-" * 60 + "\n")
        
        for i, (word, freq) in enumerate(word_frequencies, 1):
            self.results_text.insert(tk.END, f"{i:<6} {word:<20} {freq:<10}\n")
        
        self.results_text.insert(tk.END, "\n" + "=" * 60 + "\n")
    
    def on_closing(self):
        """Handle application closing."""
        self.db.close()
        self.root.destroy()


def main():
    """Main function to run the application."""
    root = tk.Tk()
    app = BookAnalyzerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()