import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Geometry Dash Streamlit", layout="centered")

st.title("🏃 Geometry Dash - Stereo Madness")
st.caption("Nhấn **SPACE** hoặc **Click chuột** để nhảy qua các chướng ngại vật và về đích!")

# HTML5 Canvas Game Code - Designed Level Edition
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

// Game State
let gameState = "START"; // START, PLAYING, GAMEOVER, VICTORY
let speed = 6;
let distance = 0;

// Player
const player = {
    x: 120,
    y: 300,
    size: 35,
    vy: 0,
    gravity: 0.85,
    jumpPower: -13.8,
    isGrounded: false,
    rotation: 0
};

const floorY = 330;

// THIẾT KẾ MÀN CHƠI CỐ ĐỊNH (Level Design giống Stereo Madness)
// Vị trí (x) được tính từ lúc bắt đầu màn chơi
const LEVEL_LENGTH = 3500; // Độ dài màn chơi
const levelObstacles = [
    // Đoạn đầu tập nhảy
    { x: 600, type: "spike" },
    { x: 900, type: "spike" },
    { x: 1200, type: "block" },
    
    // Cặp gai đôi
    { x: 1500, type: "spike" },
    { x: 1535, type: "spike" },
    
    // Khối hộp kết hợp gai
    { x: 1850, type: "block" },
    { x: 2000, type: "spike" },
    { x: 2200, type: "block" },
    
    // Thử thách 3 gai liên tiếp
    { x: 2500, type: "spike" },
    { x: 2535, type: "spike" },
    { x: 2570, type: "spike" },
    
    // Đoạn nước rút về đích
    { x: 2900, type: "block" },
    { x: 3100, type: "spike" },
    { x: 3135, type: "spike" }
];

let activeObstacles = [];

function jump() {
    if (gameState === "START" || gameState === "GAMEOVER" || gameState === "VICTORY") {
        resetGame();
        gameState = "PLAYING";
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
    
    // Khởi tạo lại chướng ngại vật từ Level Map
    activeObstacles = levelObstacles.map(obs => ({
        x: obs.x,
        width: 35,
        height: 35,
        type: obs.type,
        passed: false
    }));
}

function update() {
    if (gameState !== "PLAYING") return;

    distance += speed;
    let progress = Math.min(100, Math.floor((distance / LEVEL_LENGTH) * 100));

    // Physics
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

    // Di chuyển chướng ngại vật & Check va chạm
    for (let obs of activeObstacles) {
        let currentX = obs.x - distance + player.x;

        // Va chạm chuẩn (Hitbox)
        let hitMargin = 5;
        if (
            player.x + player.size - hitMargin > currentX &&
            player.x + hitMargin < currentX + obs.width &&
            player.y + player.size - hitMargin > floorY - obs.height
        ) {
            gameState = "GAMEOVER";
            info.innerText = `💥 THẤT BẠI! Đã hoàn thành ${progress}% | Nhấn SPACE để thử lại`;
        }
    }

    // Kiểm tra VỀ ĐÍCH (Thắng)
    if (distance >= LEVEL_LENGTH) {
        gameState = "VICTORY";
        info.innerText = `🎉 CHÚC MỪNG! BẠN ĐÃ HOÀN THÀNH MÀN CHƠI 100%!`;
    } else {
        info.innerText = `Tiến độ: ${progress}%`;
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Vẽ Sàn
    ctx.fillStyle = "#00f0ff";
    ctx.fillRect(0, floorY, canvas.width, 4);
    ctx.fillStyle = "#0a1128";
    ctx.fillRect(0, floorY + 4, canvas.width, canvas.height - floorY);

    // Vẽ Thanh Tiến Độ (%) ở trên cùng
    let progressRatio = Math.min(1, distance / LEVEL_LENGTH);
    ctx.fillStyle = "rgba(255, 255, 255, 0.2)";
    ctx.fillRect(200, 15, 400, 12);
    ctx.fillStyle = "#00ffcc";
    ctx.fillRect(200, 15, 400 * progressRatio, 12);
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 1;
    ctx.strokeRect(200, 15, 400, 12);

    // Vẽ Cổng Về Đích (Finish Line)
    let finishX = LEVEL_LENGTH - distance + player.x;
    if (finishX < canvas.width + 100) {
        ctx.fillStyle = "#00ffcc";
        ctx.fillRect(finishX, floorY - 120, 15, 120);
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 16px Arial";
        ctx.fillText("FINISH", finishX - 15, floorY - 130);
    }

    // Vẽ Chướng ngại vật
    for (let obs of activeObstacles) {
        let currentX = obs.x - distance + player.x;
        
        if (currentX > -50 && currentX < canvas.width + 50) {
            if (obs.type === "spike") {
                ctx.fillStyle = "#ff0055";
                ctx.beginPath();
                ctx.moveTo(currentX, floorY);
                ctx.lineTo(currentX + obs.width / 2, floorY - obs.height);
                ctx.lineTo(currentX + obs.width, floorY);
                ctx.closePath();
                ctx.fill();
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 2;
                ctx.stroke();
            } else {
                ctx.fillStyle = "#ff9900";
                ctx.fillRect(currentX, floorY - obs.height, obs.width, obs.height);
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 2;
                ctx.strokeRect(currentX, floorY - obs.height, obs.width, obs.height);
            }
        }
    }

    // Vẽ Nhận vật Cube
    ctx.save();
    ctx.translate(player.x + player.size / 2, player.y + player.size / 2);
    ctx.rotate(player.rotation);
    ctx.fillStyle = "#00ffcc";
    ctx.fillRect(-player.size / 2, -player.size / 2, player.size, player.size);
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 3;
    ctx.strokeRect(-player.size / 2, -player.size / 2, player.size, player.size);
    
    // Mắt khối vuông
    ctx.fillStyle = "#000";
    ctx.fillRect(2, -8, 6, 6);
    ctx.fillRect(10, -8, 6, 6);
    ctx.restore();

    // Giao diện Màn hình Bắt đầu
    if (gameState === "START") {
        ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#00f0ff";
        ctx.font = "bold 28px Arial";
        ctx.textAlign = "center";
        ctx.fillText("STEREO MADNESS - LEVEL 1", canvas.width / 2, canvas.height / 2 - 20);
        ctx.font = "20px Arial";
        ctx.fillStyle = "#ffffff";
        ctx.fillText("Nhấn SPACE để Bắt Đầu", canvas.width / 2, canvas.height / 2 + 30);
    }

    // Giao diện MÀN HÌNH CHIẾN THẮNG (Victory Screen)
    if (gameState === "VICTORY") {
        ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = "#00ffcc";
        ctx.font = "bold 36px Arial";
        ctx.textAlign = "center";
        ctx.fillText("LEVEL COMPLETE! 100%", canvas.width / 2, canvas.height / 2 - 30);
        
        ctx.fillStyle = "#ffffff";
        ctx.font = "20px Arial";
        ctx.fillText("Chúc mừng! Bạn đã chinh phục thành công màn chơi!", canvas.width / 2, canvas.height / 2 + 15);
        ctx.fillText("Nhấn SPACE để chơi lại", canvas.width / 2, canvas.height / 2 + 55);
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
