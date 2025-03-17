// script.js

// Base API URL for your Flask backend
const BASE_API_URL = 'http://127.0.0.1:5000';

document.addEventListener('DOMContentLoaded', () => {
  // Interactive dialog: Open dialog overlay when main character is clicked
  const mainCharacter = document.getElementById('main-character');
  const dialogOverlay = document.getElementById('dialog-overlay');

  mainCharacter.addEventListener('click', () => {
    dialogOverlay.classList.remove('hidden');
  });

  // Attach event listeners for dialog option buttons
  const optionButtons = document.querySelectorAll('.dialog-option');
  optionButtons.forEach(button => {
    button.addEventListener('click', (e) => {
      const choice = e.target.getAttribute('data-choice');
      handleDialogChoice(choice);
    });
  });
});

// Handle dialog choices and call corresponding API functions
function handleDialogChoice(choice) {
  if (choice === 'books') {
    fetchBooks();
    closeDialog();
  } else if (choice === 'students') {
    fetchStudents();
    closeDialog();
  } else if (choice === 'overdue') {
    fetchOverdue();
    closeDialog();
  } else if (choice === 'exit') {
    closeDialog();
  }
}

// Hide the dialog overlay
function closeDialog() {
  document.getElementById('dialog-overlay').classList.add('hidden');
}

// Utility to display API results in the results container
function displayResults(htmlContent) {
  const container = document.getElementById('results-container');
  container.innerHTML = htmlContent;
}

// Fetch available books from the backend
function fetchBooks() {
  fetch(`${BASE_API_URL}/api/books`)
    .then(response => response.json())
    .then(data => {
      let html = '<h3>Available Books</h3>';
      if (data.length === 0) {
        html += '<p>No books available.</p>';
      } else {
        html += '<ul>';
        data.forEach(book => {
          html += `
            <li>
              <img src="assets/book-icon.png" alt="Book Icon">
              <div>
                <strong>${book.TenSach}</strong><br>
                <em>${book.TacGia || 'Unknown Author'}</em> - ${book.SoLuong} in stock
              </div>
            </li>
          `;
        });
        html += '</ul>';
      }
      displayResults(html);
    })
    .catch(error => {
      console.error('Error fetching books:', error);
      displayResults('<p>Error fetching books.</p>');
    });
}

// Fetch list of students from the backend
function fetchStudents() {
  fetch(`${BASE_API_URL}/api/students`)
    .then(response => response.json())
    .then(data => {
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

// Fetch overdue loans from the backend
function fetchOverdue() {
  fetch(`${BASE_API_URL}/api/overdue`)
    .then(response => response.json())
    .then(data => {
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

// Fetch the most borrowed book from the backend
function fetchMostBorrowed() {
  fetch(`${BASE_API_URL}/api/most_borrowed`)
    .then(response => response.json())
    .then(data => {
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
