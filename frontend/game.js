const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const parentDiv = document.querySelector('.main-content');
console.log('canvas', canvas);

keys = {'up': false, 'down': false, 'left': false, 'right': false};

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
    canvas.width = parentDiv.clientWidth;
    canvas.height = parentDiv.clientHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function newPos() {
    character.x += character.dx;
    character.y += character.dy;

    // Slow down character
    if (!keys['up'] && !keys['down']) {
        if (character.dy > 0) {
            character.dy -= character.deceleration;
        } else if (character.dy < 0) {
            character.dy += character.deceleration;
        }
    }
    if (!keys['left'] && !keys['right']) {
        if (character.dx > 0) {
            character.dx -= character.deceleration;
        } else if (character.dx < 0) {
            character.dx += character.deceleration;
        }
    }


    // Prevent character from moving out of canvas bounds
    if (character.x < 0) character.x = 0;
    if (character.y < 0) character.y = 0;
    if (character.x + character.width > canvas.width) character.x = canvas.width - character.width;
    if (character.y + character.height > canvas.height) character.y = canvas.height - character.height;
}

function handleAcceleration() {
    if (keys['up']) {
        character.dy = -character.speed;
    }
    if (keys['down']) {
        character.dy = character.speed;
    }
    if (keys['left']) {
        character.dx = -character.speed;
    }
    if (keys['right']) {
        character.dx = character.speed;
    }
    if (character.dx > character.speed) character.dx = character.speed;
    if (character.dy > character.speed) character.dy = character.speed;
    if (character.dx < -character.speed) character.dx = -character.speed;
    if (character.dy < -character.speed) character.dy = -character.speed;
}

function keyDown(e) {
    if (e.key === 'ArrowUp') {
        keys['up'] = true;
    }
    if (e.key === 'ArrowDown') {
        keys['down'] = true;
    }
    if (e.key === 'ArrowLeft') {
        keys['left'] = true;
    }
    if (e.key === 'ArrowRight') {
        keys['right'] = true;
    }
}

function keyUp(e) {
    if (e.key === 'ArrowUp') {
        keys['up'] = false;
    }
    if (e.key === 'ArrowDown') {
        keys['down'] = false;
    }
    if (e.key === 'ArrowLeft') {
        keys['left'] = false;
    }
    if (e.key === 'ArrowRight') {
        keys['right'] = false;
    }
}

document.addEventListener('keydown', keyDown);
document.addEventListener('keyup', keyUp);

//if mobile, add joystick
joystick = {
    center: {x: 100, y: 100},
    baseRadius: 50,
    stickRadius: 25,
    stick: {x: 100, y: 100}
};

function drawJoystick() {
    ctx.beginPath();
    ctx.arc(joystick.center.x, canvas.height - 100, joystick.baseRadius, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(joystick.stick.x, canvas.height - 200 + joystick.stick.y, joystick.stickRadius, 0, Math.PI * 2);
    ctx.fill();
}

function handleJoystick(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top - (canvas.height - 200);

    const dx = x - joystick.center.x;
    const dy = y - joystick.center.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance < joystick.baseRadius) {
        joystick.stick.x = x;
        joystick.stick.y = y;
    } else {
        const ratio = joystick.baseRadius / distance;
        joystick.stick.x = joystick.center.x + dx * ratio;
        joystick.stick.y = joystick.center.y + dy * ratio;
    }
    character.dx = (joystick.stick.x - joystick.center.x) / 5;
    character.dy = (joystick.stick.y - joystick.center.y) / 5;

}

canvas.addEventListener('mousedown', (e) => {
    handleJoystick(e);
    canvas.addEventListener('mousemove', handleJoystick);
});

canvas.addEventListener('mouseup', () => {
    canvas.removeEventListener('mousemove', handleJoystick);
    joystick.stick.x = joystick.center.x;
    joystick.stick.y = joystick.center.y;
});

function update() {
    clearCanvas();
    drawJoystick();
    drawCharacter();
    newPos();

    requestAnimationFrame(update);
}
update();
