import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Geometry Dash Streamlit", layout="centered")

st.title("🏃 Geometry Dash 2D")
st.caption("Nhấn **SPACE** (phím Cách) hoặc **Click chuột** để nhảy qua chướng ngại vật!")

# HTML5 Canvas Game Code
game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            background-color: #0d0f18;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            font-family: Arial, sans-serif;
            color: white;
        }
        canvas {
            border: 4px solid #00f0ff;
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
            border-radius: 8px;
            background: linear-gradient(180deg, #1a0b2e 0%, #000000 100%);
        }
        #info {
            margin-top: 10px;
            font-size: 18px;
            font-weight: bold;
        }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="800" height="400"></canvas>
<div id="info">Nhấn SPACE để bắt đầu!</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const info = document.getElementById("info");

// Game Settings & State
let gameState = "START"; // START, PLAYING, GAMEOVER
let score = 0;
let highScore = 0;
let speed = 6;
let frameCount = 0;

// Player (Square Cube)
const player = {
    x: 100,
    y: 300,
    size: 35,
    vy: 0,
    gravity: 0.8,
    jumpPower: -13.5,
    isGrounded: false,
    rotation: 0
};

// Floor Level
const floorY = 330;

// Obstacles Array
let obstacles = [];

// Handle Keyboard & Click Inputs
function jump() {
    if (gameState === "START" || gameState === "GAMEOVER") {
        resetGame();
        gameState = "PLAYING";
        info.innerText = "Score: 0";
    } else if (gameState === "PLAYING" && player.isGrounded) {
        player.vy = player.jumpPower;
        player.isGrounded = false;
    }
}

window.addEventListener("keydown", (e) => {
    if (e.code === "Space" || e.code === "ArrowUp") {
        e.preventDefault();
        jump();
    }
});

canvas.addEventListener("mousedown", jump);

function resetGame() {
    player.y = floorY - player.size;
    player.vy = 0;
    player.rotation = 0;
    player.isGrounded = true;
    obstacles = [];
    score = 0;
    speed = 6;
    frameCount = 0;
}

// Spawn Balanced Obstacles
function spawnObstacle() {
    // Tới khoảng trắng ban đầu (khoảng 120 frames ~ 2 giây đầu không có chướng ngại vật)
    if (frameCount < 120) return;

    // Khoảng cách nhịp xuất hiện cân bằng (từ 70 - 110 frames)
    let minGap = 70;
    let maxGap = 110;
    
    if (obstacles.length === 0 || (frameCount - obstacles[obstacles.length - 1].spawnFrame) > Math.random() * (maxGap - minGap) + minGap) {
        let type = Math.random() < 0.7 ? "spike" : "block";
        obstacles.push({
            x: canvas.width + 50,
            width: 35,
            height: 35,
            type: type,
            spawnFrame: frameCount
        });
    }
}

function update() {
    if (gameState !== "PLAYING") return;

    frameCount++;
    score = Math.floor(frameCount / 10);

    // Tăng tốc độ rất nhẹ theo thời gian
    speed = 6 + Math.min(score / 500, 3);

    // Physics Update
    player.vy += player.gravity;
    player.y += player.vy;

    // Floor collision
    if (player.y + player.size >= floorY) {
        player.y = floorY - player.size;
        player.vy = 0;
        player.isGrounded = true;
        // Snap rotation to 90-degree grid when landing
        player.rotation = Math.round(player.rotation / (Math.PI / 2)) * (Math.PI / 2);
    } else {
        // Rotate cube in air
        player.rotation += 0.12;
    }

    // Spawn & Move Obstacles
    spawnObstacle();

    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        obs.x -= speed;

        // Collision Check (AABB / Triangle check simplified)
        let hitMargin = 6; // Hitbox chuẩn không bị nổ oan
        if (
            player.x + player.size - hitMargin > obs.x &&
            player.x + hitMargin < obs.x + obs.width &&
            player.y + player.size - hitMargin > floorY - obs.height
        ) {
            gameState = "GAMEOVER";
            if (score > highScore) highScore = score;
            info.innerText = `💥 GAME OVER! Score: ${score} | High Score: ${highScore} (Nhấn SPACE để chơi lại)`;
        }

        // Remove out-of-screen obstacles
        if (obs.x + obs.width < 0) {
            obstacles.splice(i, 1);
        }
    }

    if (gameState === "PLAYING") {
        info.innerText = `Score: ${score} | High Score: ${highScore}`;
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Floor
    ctx.fillStyle = "#00f0ff";
    ctx.fillRect(0, floorY, canvas.width, 4);
    ctx.fillStyle = "#0a1128";
    ctx.fillRect(0, floorY + 4, canvas.width, canvas.height - floorY);

    // Draw Obstacles
    for (let obs of obstacles) {
        if (obs.type === "spike") {
            ctx.fillStyle = "#ff0055";
            ctx.beginPath();
            ctx.moveTo(obs.x, floorY);
            ctx.lineTo(obs.x + obs.width / 2, floorY - obs.height);
            ctx.lineTo(obs.x + obs.width, floorY);
            ctx.closePath();
            ctx.fill();
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.stroke();
        } else {
            ctx.fillStyle = "#ff9900";
            ctx.fillRect(obs.x, floorY - obs.height, obs.width, obs.height);
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.strokeRect(obs.x, floorY - obs.height, obs.width, obs.height);
        }
    }

    // Draw Player (Rotated Cube)
    ctx.save();
    ctx.translate(player.x + player.size / 2, player.y + player.size / 2);
    ctx.rotate(player.rotation);
    ctx.fillStyle = "#00ffcc";
    ctx.fillRect(-player.size / 2, -player.size / 2, player.size, player.size);
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 3;
    ctx.strokeRect(-player.size / 2, -player.size / 2, player.size, player.size);
    
    // Player Eyes
    ctx.fillStyle = "#000";
    ctx.fillRect(2, -8, 6, 6);
    ctx.fillRect(10, -8, 6, 6);
    ctx.restore();

    // Start Screen
    if (gameState === "START") {
        ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#00f0ff";
        ctx.font = " bold 28px Arial";
        ctx.textAlign = "center";
        ctx.fillText("NHẤN SPACE ĐỂ BẮT ĐẦU", canvas.width / 2, canvas.height / 2);
    }
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

gameLoop();
</script>
</body>
</html>
"""

components.html(game_html, height=480)
