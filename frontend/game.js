const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const parentDiv = document.querySelector('.main-content');
canvas.width = parentDiv.clientWidth;
canvas.height = parentDiv.clientHeight;
console.log('canvas', canvas);

const character = {
    width: 50,
    height: 50,
    x: canvas.width / 2 - 25,
    y: canvas.height / 2 - 25,
    speed: 10,
    acceleration: 2,
    deceleration: 0.4,
    dx: 0,
    dy: 0
};

function drawCharacter() {
    ctx.fillStyle = 'blue';
    ctx.fillRect(character.x, character.y, character.width, character.height);
}

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function newPos() {
    character.x += character.dx;
    character.y += character.dy;

    // Slow down character
    if (character.dx > 0) {
        character.dx -= character.deceleration;
        if (character.dx < 0) character.dx = 0;
    }
    if (character.dx < 0) {
        character.dx += character.deceleration;
        if (character.dx > 0) character.dx = 0;
    }
    if (character.dy > 0) {
        character.dy -= character.deceleration;
        if (character.dy < 0) character.dy = 0;
    }
    if (character.dy < 0) {
        character.dy += character.deceleration;
        if (character.dy > 0) character.dy = 0;
    }


    // Prevent character from moving out of canvas bounds
    if (character.x < 0) character.x = 0;
    if (character.y < 0) character.y = 0;
    if (character.x + character.width > canvas.width) character.x = canvas.width - character.width;
    if (character.y + character.height > canvas.height) character.y = canvas.height - character.height;
}

function update() {
    console.log('update');
    clearCanvas();
    drawCharacter();
    newPos();

    requestAnimationFrame(update);
}

function keyDown(e) {
    if (e.key === 'ArrowRight' || e.key === 'Right') {
        character.dx += character.acceleration;
        if (character.dx > character.speed) character.dx = character.speed;
    }
    if (e.key === 'ArrowLeft' || e.key === 'Left') {
        character.dx -= character.acceleration;
        if (character.dx < -character.speed) character.dx = -character.speed;
    }
    if (e.key === 'ArrowUp' || e.key === 'Up') {
        character.dy -= character.acceleration;
        if (character.dy < -character.speed) character.dy = -character.speed;
    }
    if (e.key === 'ArrowDown' || e.key === 'Down') {
        character.dy += character.acceleration;
        if (character.dy > character.speed) character.dy = character.speed;
    }
}


document.addEventListener('keydown', keyDown);

update();
