const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const parent_div = document.querySelector('.main-content');

const keys = { up: false, down: false, left: false, right: false };

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
  shelf_height: 100,
  book_width: 40,
  book_height: 80,
  speeds: []
};


function generate_shelf(y_pos) {
  const books = [];
  let x_pos = 0;
  while (x_pos < canvas.width + 50) {
    const width = Math.floor(Math.random() * 31) + 20;
    const color = `hsl(${Math.random() * 360}, 60%, 40%)`;
    books.push({ x: x_pos, y: y_pos, width, color });
    x_pos += width + (Math.floor(Math.random() * 11) + 5);
  }
  return books;
}

function initialize_bookshelves() {
  bookshelf.shelves = [];
  bookshelf.speeds = [];
  const shelf_count = Math.ceil(canvas.height / bookshelf.shelf_height);
  for (let i = 0; i < shelf_count; i++) {
    const y = i * bookshelf.shelf_height;
    bookshelf.shelves.push(generate_shelf(y));
    bookshelf.speeds.push(Math.random() * 2 + 1);
  }
}

function draw_bookshelves() {
  bookshelf.shelves.forEach((shelf, idx) => {
    const y = idx * bookshelf.shelf_height;
    ctx.fillStyle = 'saddlebrown';
    ctx.fillRect(0, y, canvas.width, 10);
    shelf.forEach(book => {
      ctx.fillStyle = book.color;
      ctx.fillRect(book.x, y + 15, book.width, bookshelf.book_height);
      ctx.fillStyle = 'black';
      ctx.fillRect(book.x, y + 15, 1, bookshelf.book_height);
      ctx.fillRect(book.x + book.width, y + 15, 1, bookshelf.book_height);
    });
  });
}

function scroll_bookshelves() {
  bookshelf.shelves.forEach((shelf, idx) => {
    shelf.forEach(book => {
      book.x -= bookshelf.speeds[idx];
      bookshelf.speeds[idx] += Math.random() * 0.03 - 0.015;
      if (bookshelf.speeds[idx] < 1) bookshelf.speeds[idx] = 1;
      if (bookshelf.speeds[idx] > 3) bookshelf.speeds[idx] = 3;
      if (book.x + book.width < 0) {
        book.x = canvas.width;
      }
    });
  });
}

function clear_canvas() {
  canvas.width = parent_div.clientWidth;
  canvas.height = parent_div.clientHeight;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function update_frame() {
  clear_canvas();
  draw_bookshelves();
  scroll_bookshelves();
  requestAnimationFrame(update_frame);
}

document.addEventListener('DOMContentLoaded', () => {
  clear_canvas();
  initialize_bookshelves();
  update_frame();
});
