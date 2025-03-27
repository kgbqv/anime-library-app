const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const parentDiv = document.querySelector('.main-content');

keys = { 'up': false, 'down': false, 'left': false, 'right': false };

const character = {
    width: 50,
    height: 50,
    x: canvas.width / 2 - 25,
    y: canvas.height / 2 - 25,
    speed: 10,
    dx: 0,
    dy: 0
};

const bookshelf = {
    shelves: [],
    shelfHeight: 100,
    bookWidth: 40,
    bookHeight: 80,
    speed: []
};



function generateShelf(y) {
    const books = [];
    let x = 0;
    // Continue until we fill the canvas plus a buffer
    while (x < canvas.width + 50) {
        // Generate a random width between 20 and 50
        let width = Math.floor(Math.random() * (50 - 20 + 1)) + 20;
        let color = `hsl(${Math.random() * 360}, 60%, 40%)`;
        books.push({ x, y, width, color });
        // Generate a random gap between 5 and 15
        let gap = Math.floor(Math.random() * 11) + 5;
        x += width + gap;
    }
    return books;
}

function initializeBookshelves() {
    bookshelf.shelves = [];
    const numShelves = Math.ceil(canvas.height / bookshelf.shelfHeight);
    console.log("Initializing", numShelves, "shelves.");
    for (let i = 0; i < numShelves; i++) {
        let shelfY = i * bookshelf.shelfHeight;
        bookshelf.shelves.push(generateShelf(shelfY));
        bookshelf.speed.push(Math.floor(Math.random() * 3) + 1);
    }
}

function drawBookshelves() {
    bookshelf.shelves.forEach((shelf, shelfIndex) => {
        let shelfY = shelfIndex * bookshelf.shelfHeight;
        // Draw the brown shelf board (10px thick)
        ctx.fillStyle = 'saddlebrown';
        ctx.fillRect(0, shelfY, canvas.width, 10);
        // Draw each book with its individual width
        shelf.forEach((book) => {
            ctx.fillStyle = book.color;
            ctx.fillRect(book.x, shelfY + 15, book.width, bookshelf.bookHeight);
            //fill in left border and right border
            ctx.fillStyle = 'black';
            ctx.fillRect(book.x, shelfY + 15, 1, bookshelf.bookHeight);
            ctx.fillRect(book.x + book.width, shelfY + 15, 1, bookshelf.bookHeight);
        });
    });
}

function scrollBookshelves() {
    bookshelf.shelves.forEach((shelf, shelfIndex) => {
        shelf.forEach((book, bookIndex) => {
            book.x -= bookshelf.speed[shelfIndex];
            //randomly change the speed of the book
            bookshelf.speed[shelfIndex] += Math.random() * 0.03 - 0.015;
            if (bookshelf.speed[shelfIndex] < 1) {
                bookshelf.speed[shelfIndex] = 1;
            } else if (bookshelf.speed[shelfIndex] > 3) {
                bookshelf.speed[shelfIndex] = 3;
            }
            // When a book fully scrolls off the left, reset its x to canvas.width
            if (book.x + book.width < 0) {
                book.x = canvas.width;
            }
        });
    });
}

function clearCanvas() {
    canvas.width = parentDiv.clientWidth;
    canvas.height = parentDiv.clientHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function update() {

    clearCanvas();
    drawBookshelves();
    //drawCharacter();
    scrollBookshelves();
    //newPos();
    // Log current character position for debugging
    console.log(`Character position: x=${character.x}, y=${character.y}`);
    requestAnimationFrame(update);
}

// Initialize everything on DOM content load
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded. Initializing bookshelves.');

    clearCanvas();
    initializeBookshelves();
    update();
});
