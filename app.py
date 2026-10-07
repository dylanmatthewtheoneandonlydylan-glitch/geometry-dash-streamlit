import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Geometry Dash - Streamlit Edition", layout="centered")

st.title("🟨 Geometry Dash: Streamlit Edition")
st.caption("Nhấn **SPACEBAR** hoặc **CLICK CHUỘT** vào khung game để nhảy qua chướng ngại vật!")

# Mã Game Geometry Dash viết bằng HTML5 Canvas + JS
gd_game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { 
            margin: 0; 
            background-color: #0d0e15; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            font-family: Arial, sans-serif;
        }
        canvas { 
            border: 3px solid #00f0ff; 
            box-shadow: 0 0 20px #00f0ff; 
            background: linear-gradient(180deg, #0f0c29, #302b63, #24243e);
            cursor: pointer;
        }
    </style>
</head>
<body>
    <canvas id="gdCanvas" width="700" height="400"></canvas>

<script>
const canvas = document.getElementById("gdCanvas");
const ctx = canvas.getContext("2d");

// Cấu hình vật lý & Trạng thái game
const gravity = 0.65;
let gameSpeed = 6;
let score = 0;
let gameOver = false;
let gameWon = false;

// Nhân vật khối vuông (Cube)
const player = {
    x: 100,
    y: 280,
    size: 40,
    dy: 0,
    jumpForce: -12,
    isGrounded: false,
    rotation: 0,
    color: '#00ffcc'
};

// Sàn nhà
const floorY = 320;

// Danh sách chướng ngại vật (Gai nhọn - Triangles)
let obstacles = [];

function spawnObstacle() {
    // Tạo khoảng cách ngẫu nhiên giữa các gai
    if (obstacles.length === 0 || canvas.width - obstacles[obstacles.length - 1].x > 220 + Math.random() * 150) {
        obstacles.push({
            x: canvas.width,
            y: floorY,
            size: 40,
            type: 'spike'
        });
    }
}

// Lắng nghe thao tác Nhảy (Spacebar hoặc Click chuột)
function doJump() {
    if (player.isGrounded && !gameOver) {
        player.dy = player.jumpForce;
        player.isGrounded = false;
    }
    if (gameOver) {
        restartGame();
    }
}

window.addEventListener("keydown", e => {
    if (e.code === "Space" || e.code === "ArrowUp") {
        e.preventDefault();
        doJump();
    }
});
canvas.addEventListener("mousedown", doJump);

function restartGame() {
    player.y = floorY - player.size;
    player.dy = 0;
    player.rotation = 0;
    player.isGrounded = true;
    obstacles = [];
    score = 0;
    gameOver = false;
}

// Vòng lặp cập nhật Game (Update Loop)
function update() {
    if (gameOver) return;

    // Trọng lực & Nhảy
    player.dy += gravity;
    player.y += player.dy;

    // Xử lý va chạm sàn
    if (player.y + player.size >= floorY) {
        player.y = floorY - player.size;
        player.dy = 0;
        player.isGrounded = true;
        // Căn góc xoay về bội số 90 độ khi chạm đất
        player.rotation = Math.round(player.rotation / 90) * 90;
    } else {
        // Xoay khối vuông khi đang trên không
        player.rotation += 8;
    }

    // Di chuyển chướng ngại vật & tính điểm
    obstacles.forEach((obs, index) => {
        obs.x -= gameSpeed;

        // Xử lý va chạm Hitbox (Gai nhọn dạng tam giác)
        // Kiểm tra va chạm đơn giản giữa 2 hộp bounding box
        if (player.x < obs.x + obs.size - 10 &&
            player.x + player.size - 10 > obs.x &&
            player.y + player.size > obs.y - obs.size) {
            gameOver = true;
        }

        // Xóa gai đã đi qua màn hình
        if (obs.x + obs.size < 0) {
            obstacles.splice(index, 1);
            score += 1;
        }
    });

    spawnObstacle();
}

// Vẽ Đồ họa (Render)
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. Vẽ sàn nhà
    ctx.fillStyle = "#00f0ff";
    ctx.fillRect(0, floorY, canvas.width, 4);
    ctx.fillStyle = "#0a0a16";
    ctx.fillRect(0, floorY + 4, canvas.width, canvas.height - floorY);

    // 2. Vẽ Gai nhọn (Tam giác Geometry Dash)
    obstacles.forEach(obs => {
        ctx.fillStyle = "#ff0055";
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(obs.x, obs.y);
        ctx.lineTo(obs.x + obs.size / 2, obs.y - obs.size);
        ctx.lineTo(obs.x + obs.size, obs.y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    });

    // 3. Vẽ Khối vuông người chơi (Có hiệu ứng xoay)
    ctx.save();
    ctx.translate(player.x + player.size / 2, player.y + player.size / 2);
    ctx.rotate((player.rotation * Math.PI) / 180);

    // Thân nhân vật
    ctx.fillStyle = player.color;
    ctx.fillRect(-player.size / 2, -player.size / 2, player.size, player.size);
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 3;
    ctx.strokeRect(-player.size / 2, -player.size / 2, player.size, player.size);

    // Mắt nhân vật (Phong cách Geometry Dash)
    ctx.fillStyle = "#000";
    ctx.fillRect(-player.size / 4, -player.size / 4, 8, 8);
    ctx.fillRect(player.size / 8, -player.size / 4, 8, 8);

    ctx.restore();

    // 4. In Điểm số
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 22px Arial";
    ctx.fillText("Score: " + score, 20, 40);

    // 5. Màn hình Game Over
    if (gameOver) {
        ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "#ff0055";
        ctx.font = "bold 40px Arial";
        ctx.textAlign = "center";
        ctx.fillText("ATTEMPT FAILED!", canvas.width / 2, canvas.height / 2 - 20);

        ctx.fillStyle = "#ffffff";
        ctx.font = "18px Arial";
        ctx.fillText("Điểm của bạn: " + score, canvas.width / 2, canvas.height / 2 + 20);
        ctx.fillText("Click chuột hoặc nhấn SPACEBAR để chơi lại", canvas.width / 2, canvas.height / 2 + 60);
        ctx.textAlign = "left";
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

components.html(gd_game_code, height=430)
