import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Geometry Dash Custom Skin", layout="centered")

st.title("🏃 Geometry Dash - Custom Face Edition")
st.caption("Nhấn **SPACE** hoặc **Click chuột** để nhảy qua các chướng ngại vật!")

# HTML5 Canvas Game Code với âm thanh và nhạc nền
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
            user-select: none;
        }
        canvas {
            border: 4px solid #00f0ff;
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.5);
            border-radius: 8px;
            background: #000000;
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

<!-- Các file âm thanh -->
<audio id="bgMusic" src="https://ia800109.us.archive.org/3/items/vgmtapes-1144/Kirby%2064%20-%20The%20Crystal%20Shards%20%28N64%29/03%20Pop%20Star.mp3" loop preload="auto"></audio>
<audio id="deathSound" src="https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3" preload="auto"></audio>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const info = document.getElementById("info");

// Audio Elements
const bgMusic = document.getElementById("bgMusic");
const deathSound = document.getElementById("deathSound");

bgMusic.volume = 0.5;
deathSound.volume = 0.7;

// Load Custom Skin Image
const playerImg = new Image();
playerImg.src = "https://i.imgur.com/8Q8S4wD.png";

// Game State
let gameState = "START"; 
let speed = 6;
let distance = 0;

// Player Settings
const player = {
    x: 120,
    y: 300,
    size: 42,
    vy: 0,
    gravity: 0.85,
    jumpPower: -13.8,
    isGrounded: false,
    rotation: 0
};

const floorY = 330;
const LEVEL_LENGTH = 3500;

// Chướng ngại vật
const levelObstacles = [
    { x: 600, type: "spike" },
    { x: 900, type: "spike" },
    { x: 1200, type: "block" },
    { x: 1500, type: "spike" },
    { x: 1535, type: "spike" },
    { x: 1850, type: "block" },
    { x: 2000, type: "spike" },
    { x: 2200, type: "block" },
    { x: 2500, type: "spike" },
    { x: 2535, type: "spike" },
    { x: 2570, type: "spike" },
    { x: 2900, type: "block" },
    { x: 3100, type: "spike" },
    { x: 3135, type: "spike" }
];

let activeObstacles = [];

function playMusic() {
    bgMusic.currentTime = 0;
    bgMusic.play().catch(e => console.log("Cần tương tác người dùng để phát nhạc:", e));
}

function stopMusic() {
    bgMusic.pause();
    bgMusic.currentTime = 0;
}

function jump() {
    if (gameState === "START" || gameState === "GAMEOVER" || gameState === "VICTORY") {
        resetGame();
        gameState = "PLAYING";
        playMusic();
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
    distance = 0;
    
    activeObstacles = levelObstacles.map(obs => ({
        x: obs.x,
        width: 35,
        height: 35,
        type: obs.type
    }));
}

function update() {
    if (gameState !== "PLAYING") return;

    distance += speed;
    let progress = Math.min(100, Math.floor((distance / LEVEL_LENGTH) * 100));

    // Mức trọng lực và di chuyển
    player.vy += player.gravity;
    player.y += player.vy;

    if (player.y + player.size >= floorY) {
        player.y = floorY - player.size;
        player.vy = 0;
        player.isGrounded = true;
        player.rotation = Math.round(player.rotation / (Math.PI / 2)) * (Math.PI / 2);
    } else {
        player.rotation += 0.15;
    }

    // Kiểm tra va chạm với chướng ngại vật
    for (let obs of activeObstacles) {
        let currentX = obs.x - distance + player.x;
        let hitMargin = 6;

        if (
            player.x + player.size - hitMargin > currentX &&
            player.x + hitMargin < currentX + obs.width &&
            player.y + player.size - hitMargin > floorY - obs.height
        ) {
            gameState = "GAMEOVER";
            stopMusic();
            deathSound.currentTime = 0;
            deathSound.play().catch(e => console.log(e));
            info.innerText = `💥 THẤT BẠI! Tiến độ: ${progress}% | Nhấn SPACE để chơi lại`;
        }
    }

    // Về đích
    if (distance >= LEVEL_LENGTH) {
        gameState = "VICTORY";
        stopMusic();
        info.innerText = `🎉 XUẤT SẮC! BẠN ĐÃ HOÀN THÀNH 100%!`;
    } else {
        info.innerText = `Tiến độ: ${progress}%`;
    }
}

function drawBackground() {
    let grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
    grad.addColorStop(0, "#1a0033");
    grad.addColorStop(1, "#000000");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const colors = ["#ff0055", "#00f0ff", "#ffcc00", "#00ff66", "#cc00ff"];
    for (let i = 0; i < 16; i++) {
        let x = i * 55 - (distance * 0.2) % 55;
        ctx.fillStyle = colors[i % colors.length];
        ctx.shadowColor = colors[i % colors.length];
        ctx.shadowBlur = 10;
        ctx.fillRect(x, 0, 8, 40 + (i % 3) * 25);
    }
    ctx.shadowBlur = 0;
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. Vẽ nền
    drawBackground();

    // 2. Vẽ Sàn
    ctx.fillStyle = "#00f0ff";
    ctx.shadowColor = "#00f0ff";
    ctx.shadowBlur = 12;
    ctx.fillRect(0, floorY, canvas.width, 4);
    ctx.shadowBlur = 0;
    ctx.fillStyle = "#0d001a";
    ctx.fillRect(0, floorY + 4, canvas.width, canvas.height - floorY);

    // 3. Thanh tiến độ (%)
    let progressRatio = Math.min(1, distance / LEVEL_LENGTH);
    ctx.fillStyle = "rgba(255, 255, 255, 0.2)";
    ctx.fillRect(200, 15, 400, 10);
    ctx.fillStyle = "#00ffcc";
    ctx.fillRect(200, 15, 400 * progressRatio, 10);

    // 4. Cổng Về Đích
    let finishX = LEVEL_LENGTH - distance + player.x;
    if (finishX < canvas.width + 100) {
        ctx.fillStyle = "#00ffcc";
        ctx.shadowColor = "#00ffcc";
        ctx.shadowBlur = 15;
        ctx.fillRect(finishX, floorY - 130, 15, 130);
        ctx.shadowBlur = 0;
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 16px Arial";
        ctx.fillText("FINISH", finishX - 15, floorY - 140);
    }

    // 5. Vẽ Chướng ngại vật
    for (let obs of activeObstacles) {
        let currentX = obs.x - distance + player.x;
        
        if (currentX > -50 && currentX < canvas.width + 50) {
            if (obs.type === "spike") {
                ctx.fillStyle = "#ff0055";
                ctx.shadowColor = "#ff0055";
                ctx.shadowBlur = 10;
                ctx.beginPath();
                ctx.moveTo(currentX, floorY);
                ctx.lineTo(currentX + obs.width / 2, floorY - obs.height);
                ctx.lineTo(currentX + obs.width, floorY);
                ctx.closePath();
                ctx.fill();
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 2;
                ctx.stroke();
                ctx.shadowBlur = 0;
            } else {
                ctx.fillStyle = "#ff9900";
                ctx.shadowColor = "#ff9900";
                ctx.shadowBlur = 10;
                ctx.fillRect(currentX, floorY - obs.height, obs.width, obs.height);
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 2;
                ctx.strokeRect(currentX, floorY - obs.height, obs.width, obs.height);
                ctx.shadowBlur = 0;
            }
        }
    }

    // 6. Vẽ Nhân vật Skin Mặt Người
    ctx.save();
    ctx.translate(player.x + player.size / 2, player.y + player.size / 2);
    ctx.rotate(player.rotation);

    ctx.strokeStyle = "#00f0ff";
    ctx.lineWidth = 3;
    ctx.shadowColor = "#00f0ff";
    ctx.shadowBlur = 10;
    ctx.strokeRect(-player.size / 2, -player.size / 2, player.size, player.size);
    ctx.shadowBlur = 0;

    if (playerImg.complete) {
        ctx.drawImage(playerImg, -player.size / 2, -player.size / 2, player.size, player.size);
    } else {
        ctx.fillStyle = "#00ffcc";
        ctx.fillRect(-player.size / 2, -player.size / 2, player.size, player.size);
    }
    ctx.restore();

    // Giao diện Màn hình Bắt đầu / Thắng
    if (gameState === "START") {
        ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#00f0ff";
        ctx.font = "bold 28px Arial";
        ctx.textAlign = "center";
        ctx.fillText("FACE DASH - POP STAR EDITION", canvas.width / 2, canvas.height / 2 - 20);
        ctx.font = "18px Arial";
        ctx.fillStyle = "#ffffff";
        ctx.fillText("Nhấn SPACE hoặc Click chuột để bắt đầu!", canvas.width / 2, canvas.height / 2 + 30);
    }

    if (gameState === "VICTORY") {
        ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#00ffcc";
        ctx.font = "bold 36px Arial";
        ctx.textAlign = "center";
        ctx.fillText("VICTORY! 100%", canvas.width / 2, canvas.height / 2 - 20);
        ctx.font = "20px Arial";
        ctx.fillStyle = "#ffffff";
        ctx.fillText("Chúc mừng bạn đã hoàn thành màn chơi!", canvas.width / 2, canvas.height / 2 + 25);
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
