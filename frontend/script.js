// script.js

function showDialogueOptions() {
    document.getElementById('dialogue-options').style.display = 'block';
  }
  

// Base API URL for your Flask backend (use HTTPS if needed)
const BASE_API_URL = 'https://khgb.pythonanywhere.com';

// Global variables for sequential create form
let createState = 0;  // 0: Book Title, 1: Author, 2: Genre, 3: Quantity
let createData = {};


dialog = document.getElementById("dialogue-line");

function showText(text) {
    dialog.innerHTML = text;
}

function getRandomBorrowMsg(name, book) {
    const messages = [
      `Thank you, ${name}! You have borrowed book #${book}.`,
      `Great choice, ${name}! Enjoy reading book #${book}.`,
      `You're all set, ${name}! Borrowed book #${book} successfully.`,
      `Got it, ${name}! Borrowed book #${book} for you.`,
      `Done, ${name}! Borrowed book #${book} successfully.`,
    ];
    showText(messages[Math.floor(Math.random() * messages.length)]);
  }

function getRandomReturnMsg(name, book) {
    const messages = [
      `Thank you, ${name}! You have returned book #${book}.`,
      `Great job, ${name}! You returned book #${book} successfully.`,
      `You're all set, ${name}! Returned book #${book} successfully.`,
      `Got it, ${name}! Returned book #${book} for you.`,
      `Done, ${name}! Returned book #${book} successfully.`,
    ];
    showText(messages[Math.floor(Math.random() * messages.length)]);
  }

document.addEventListener('DOMContentLoaded', () => {
    fetch(`${BASE_API_URL}/log_visit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: window.location.href })
    })
    .then(response => response.json())
    .then(data => console.log("Visit logged:", data))
    .catch(error => console.error("Error logging visit:", error));
  
  
  // Attach event listeners for dialogue option buttons
  const optionButtons = document.querySelectorAll('.dialogue-option');
  optionButtons.forEach(button => {
    button.addEventListener('click', (e) => {
      const choice = e.target.getAttribute('data-choice');
      console.log("Dialogue option selected:", choice);
      handleDialogChoice(choice);
    });
  });
  
  // Attach event listener for borrow form "Next" button and input field for Enter key
  const borrowInput = document.getElementById('borrow-input');
  document.getElementById('borrow-next').addEventListener('click', handleBorrowNext);
  borrowInput.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleBorrowNext();
    }
  });
  
  // Attach event listener for create form "Next" button and input field for Enter key
  const createInput = document.getElementById('create-input');
  document.getElementById('create-next').addEventListener('click', handleCreateNext);
  createInput.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleCreateNext();
    }
  });
  
  // Attach event listener for return form "Next" button and input field for Enter key
  const returnInput = document.getElementById('return-input');
  document.getElementById('return-next').addEventListener('click', handleReturnNext);
  returnInput.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleReturnNext();
    }
  });
  
  // Attach event listeners for cancel buttons
  const cancelButtons = document.querySelectorAll('.cancel-form');
  cancelButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      toggleForm(false);
      showDialogueOptions();
      resetBorrowForm();
      resetCreateForm();
      resetReturnForm();
    });
  });
  
  // Initially load available books into the sidebar and refresh every 30 seconds
  fetchBooks();
  setInterval(fetchBooks, 30000);
});

// Function to toggle between dialogue options and form container
function toggleForm(show) {
  const formContainer = document.getElementById('dialogue-form-container');
  const optionsContainer = document.getElementById('dialogue-options');
  if (show) {
    optionsContainer.style.display = 'none';
    formContainer.style.display = 'block';
  } else {
    formContainer.style.display = 'none';
    optionsContainer.style.display = 'block';
  }
}

// Handle dialogue choices and call corresponding API functions or show form
function handleDialogChoice(choice) {
  console.log("Handling dialogue choice:", choice);
  if (choice === 'books') {
    fetchBooks();
  } else if (choice === 'students') {
    fetchStudents();
  } else if (choice === 'overdue') {
    fetchOverdue();
  } else if (choice === 'most') {
    fetchMostBorrowed();
  } else if (choice === 'borrow') {
    // Show sequential borrow book form
    toggleForm(true);
    document.getElementById('borrow-form').style.display = 'block';
    document.getElementById('create-form').style.display = 'none';
    document.getElementById('return-form').style.display = 'none';
    initBorrowForm();
  } else if (choice === 'create') {
    // Show sequential create book form
    toggleForm(true);
    document.getElementById('create-form').style.display = 'block';
    document.getElementById('borrow-form').style.display = 'none';
    document.getElementById('return-form').style.display = 'none';
    initCreateForm();
  } else if (choice === 'return') {
    // Show sequential return book form
    toggleForm(true);
    document.getElementById('return-form').style.display = 'block';
    document.getElementById('borrow-form').style.display = 'none';
    document.getElementById('create-form').style.display = 'none';
    initReturnForm();
  } else {
    console.log("Unknown dialogue choice:", choice);
  }
}

// Utility: Display HTML content in the results container
function displayResults(htmlContent) {
  console.log("Displaying results...");
  const container = document.getElementById('books-container');
  container.innerHTML = htmlContent;
}

// Function to parse the search input and fetch filtered books
function fetchFilteredBooks(){
  const searchBar = document.getElementById('searchFilter');
  const searchTerm = searchBar.value;
  const pairRegex = /(\w+):'([^']+)'/g;
  let match;
  let filters = { genres: [], authors: [], titles: [] };
  let consumed = [];  // will track all matched substrings

  // 1) Extract key:'value' pairs
  while ((match = pairRegex.exec(searchTerm)) !== null) {
    const key = match[1].toLowerCase();
    const value = match[2];
    consumed.push(match[0]);  // e.g. "genre:'action'"
    if (key === 'genre') {
      filters.genres.push(value);
    } else if (key === 'author') {
      filters.authors.push(value);
    }
  }

  // 2) Remove those matched substrings from the original, then split remainder
  let remainder = searchTerm;
  consumed.forEach(str => {
    remainder = remainder.replace(str, '');
  });
  // split on whitespace, filter out empty tokens
  const titleTokens = remainder
    .split(/\s+/)
    .map(s => s.trim())
    .filter(Boolean);
  filters.titles = titleTokens;

  console.log("Filters parsed:", filters);
  
  // Call the filter API endpoint with the filters as JSON payload
  fetch(`${BASE_API_URL}/api/filter_books`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(filters)
  })
  .then(response => response.json())
  .then(data => {
    console.log("Filtered books data:", data);
    let html = '<h3>Filtered Books</h3><ul>';
    if (data.length === 0) {
      html += '<li>No books found.</li>';
    } else {
      data.forEach(book => {
        html += `<li>
                   <strong>ID: ${book.MaSach}</strong><br>
                   ${book.TenSach}<br>
                   <em>${book.TacGia || 'Unknown Author'}</em> (${book.TheLoai || 'Unknown Genre'})<br>
                   Quantity: ${book.SoLuong}
                 </li>`;
      });
    }
    html += '</ul>';
    document.getElementById('books-container').innerHTML = html;
  })
  .catch(error => console.error("Error fetching filtered books:", error));
}

// Attach to your search button
document.getElementById('searchButton').addEventListener('click', fetchFilteredBooks);



// API function: Fetch available books and render in the sidebar
function fetchBooks() {
  console.log("Fetching available books from API for sidebar...");
  fetch(`${BASE_API_URL}/api/books`)
    .then(response => {
      console.log("Response received for books:", response);
      return response.json();
    })
    .then(data => {
      console.log("Data received for books:", data);
      let html = `<div class="filter-container" style="display: flex; flex-direction: column; position: fixed; top: 0; left: 0; padding: 10px; background-color: #222; width: 25%; height: 15%; z-index: 1000;">
      <label for="genreFilter">Search:</label> <br>
      <input type="text" id="searchFilter" placeholder="genre:'action' author:'John Doe'" style="width: 100%;"> <br>
      <button id="searchButton" onclick="fetchFilteredBooks();"> Search </button>
    </div> 
    <div id="margin" style="margin-top: 30%;"></div>
    <h3>Books in library</h3>`;
      if (data.length === 0) {
        html += '<li>None</li>';
      } else {
        data.forEach(book => {
          html += `
            <li>
              <strong>ID: ${book.MaSach}</strong> <br> <br> ${book.TenSach}
              <br> <br>
              <em>${book.TacGia || 'Unknown Author'}</em> (${book.TheLoai || 'Unknown Genre'}) <br>
              <br>
              Quantity: ${book.SoLuong}
              <hr>
            </li>
          `;
        });
      }
      html += '</ul>';
      const container = document.getElementById('books-container');
      container.innerHTML = html;
    })
    .catch(error => {
      console.error('Error fetching books:', error);
      const container = document.getElementById('books-container');
      container.innerHTML = '<p>Error fetching books.</p>';
    });
}

// API function: Fetch students
function fetchStudents() {
  console.log("Fetching students from API...");
  fetch(`${BASE_API_URL}/api/students`)
    .then(response => {
      console.log("Response received for students:", response);
      return response.json();
    })
    .then(data => {
      console.log("Data received for students:", data);
      let html = '<h3>Students</h3>';
      if (data.length === 0) {
        html += '<p>No students found.</p>';
      } else {
        html += '<ul>';
        data.forEach(student => {
          html += `
            <li>
              <div>
                <strong>${student.TenHS}</strong><br>
                Class: ${student.Lop || 'N/A'} - Phone: ${student.SoDienThoai || 'N/A'}
              </div>
            </li>
          `;
        });
        html += '</ul>';
      }
      displayResults(html);
    })
    .catch(error => {
      console.error('Error fetching students:', error);
      displayResults('<p>Error fetching students.</p>');
    });
}

// API function: Fetch overdue loans
function fetchOverdue() {
  console.log("Fetching overdue loans from API...");
  fetch(`${BASE_API_URL}/api/overdue`)
    .then(response => {
      console.log("Response received for overdue loans:", response);
      return response.json();
    })
    .then(data => {
      console.log("Data received for overdue loans:", data);
      let html = '<h3>Overdue Loans</h3>';
      if (data.length === 0) {
        html += '<p>No overdue loans.</p>';
      } else {
        html += '<ul>';
        data.forEach(record => {
          html += `
            <li>
              <div>
                <strong>${record.TenHS}</strong> - ${record.TenSach}<br>
                Due: ${record.NgayTra}
              </div>
            </li>
          `;
        });
        html += '</ul>';
      }
      displayResults(html);
    })
    .catch(error => {
      console.error('Error fetching overdue loans:', error);
      displayResults('<p>Error fetching overdue loans.</p>');
    });
}

// API function: Fetch the most borrowed book
function fetchMostBorrowed() {
  console.log("Fetching the most borrowed book from API...");
  fetch(`${BASE_API_URL}/api/most_borrowed`)
    .then(response => {
      console.log("Response received for most borrowed book:", response);
      return response.json();
    })
    .then(data => {
      console.log("Data received for most borrowed book:", data);
      let html = '<h3>Most Borrowed Book</h3>';
      if (!data.TenSach) {
        html += '<p>No data available.</p>';
      } else {
        html += `<p><strong>${data.TenSach}</strong> has been borrowed ${data.SoLanMuon} times.</p>`;
      }
      displayResults(html);
    })
    .catch(error => {
      console.error('Error fetching most borrowed book:', error);
      displayResults('<p>Error fetching most borrowed book.</p>');
    });
}

function initBorrowForm() {
  const userID = localStorage.getItem('MaHS');
  if (userID) {
    const inputField = document.getElementById('borrow-input');
    document.getElementById('borrow-question').innerText = "Enter the Book ID (MaSach):";
    inputField.value = "";
    inputField.placeholder = "Book ID";
  } else {
    showText("Please log in to borrow books.");
    toggleForm(false);
    showDialogueOptions();
  }
}

function handleBorrowNext() {
  const inputField = document.getElementById('borrow-input');
  const inputVal = inputField.value.trim();
  if (true){
    if (!inputVal) {
      showText("Please enter the Book ID.");
      return;
    }
    storedMaHS = localStorage.getItem('MaHS');
    const maSach = inputVal;
    console.log(`Borrowing book via sequential form: Student ID ${storedMaHS}, Book ID ${maSach}`);
    fetch(`${BASE_API_URL}/api/borrow`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ MaHS: storedMaHS, MaSach: maSach })
    })
      .then(response => {
        console.log("Response received for borrow:", response);
        return response.json();
      })
      .then(data => {
        console.log("Data received for borrow:", data);
        if (data.error) {
          showText("Error: " + data.error);
        } else {
            getRandomBorrowMsg(storedMaHS, maSach);
        }
        resetBorrowForm();
        toggleForm(false);
        showDialogueOptions();
        fetchBooks();
      })
      .catch(error => {
        console.error('Error borrowing book:', error);
        showText("Error borrowing book.");
      });
  }
}

function resetBorrowForm() {
  borrowState = 0;
  storedMaHS = "";
  const inputField = document.getElementById('borrow-input');
  inputField.value = "";
  inputField.placeholder = "Student ID";
  document.getElementById('borrow-question').innerText = "";
}

function initReturnForm() {
  const inputField = document.getElementById('return-input');
  const userID = localStorage.getItem('MaHS');
  if (userID) {
  document.getElementById('return-question').innerText = "Enter the Book ID (MaSach):";
  inputField.value = "";
  inputField.placeholder = "Book ID";
  } else {
    showText("Please log in to return books.");
    toggleForm(false);
    showDialogueOptions();
  }
}

function handleReturnNext() {
  const inputField = document.getElementById('return-input');
  const inputVal = inputField.value.trim();
  storedReturnMaHS = localStorage.getItem('MaHS');
  if (true) {
    if (!inputVal) {
      showText("Please enter the Book ID.");
      return;
    }
    const maSach = inputVal;
    console.log(`Returning book via sequential form: Student ID ${storedReturnMaHS}, Book ID ${maSach}`);
    fetch(`${BASE_API_URL}/api/return`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ MaHS: storedReturnMaHS, MaSach: maSach })
    })
      .then(response => {
        console.log("Response received for return:", response);
        return response.json();
      })
      .then(data => {
        console.log("Data received for return:", data);
        if (data.error) {
          showText("Error: " + data.error);
        } else {
            getRandomReturnMsg(storedReturnMaHS, maSach);
        }
        resetReturnForm();
        toggleForm(false);
        showDialogueOptions();
        fetchBooks();
      })
      .catch(error => {
        console.error('Error returning book:', error);
        showText("Error returning book.");
      });
  }
}

function resetReturnForm() {
  returnState = 0;
  storedReturnMaHS = "";
  const inputField = document.getElementById('return-input');
  inputField.value = "";
  inputField.placeholder = "Student ID";
  document.getElementById('return-question').innerText = "";
}



// Preload the audio file
const clickSound = new Audio('./assets/click_sound_1.mp3');

// Attach event listener to all buttons
document.querySelectorAll('button').forEach(button => {
  button.addEventListener('click', () => {
    clickSound.currentTime = 0; // Reset sound to start
    clickSound.play().catch(error => console.error("Sound play failed:", error));
  });
});
