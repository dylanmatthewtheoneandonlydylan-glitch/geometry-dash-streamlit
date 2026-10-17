import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(
    page_title="Geometry Dash Custom Skin",
    layout="centered"
)

st.title("🏃 Geometry Dash - Custom Face Edition")
st.caption("Nhấn SPACE hoặc Click chuột để nhảy qua các chướng ngại vật!")


# ============================================================
# ĐỌC FILE ÂM THANH + TROLL FACE
# ============================================================

with open("pop_star.mp3", "rb") as f:
    music_url = "data:audio/mpeg;base64," + base64.b64encode(f.read()).decode()

with open("vine-boom.mp3", "rb") as f:
    death_url = "data:audio/mpeg;base64," + base64.b64encode(f.read()).decode()

with open("trollface.png", "rb") as f:
    troll_url = "data:image/png;base64," + base64.b64encode(f.read()).decode()

with open("player.png", "rb") as f:
    player_url = "data:image/png;base64," + base64.b64encode(f.read()).decode()


# ============================================================
# GAME
# ============================================================

game_html = """
<!DOCTYPE html>
<html>
<head>

<style>

body {
    margin: 0;
    background: #0d0f18;
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
    box-shadow: 0 0 25px rgba(0,240,255,0.5);
    border-radius: 8px;
    background: #000;
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

<div id="info">
    Nhấn SPACE để bắt đầu!
</div>


<audio
    id="bgMusic"
    src="MUSIC_URL_HERE"
    loop
    preload="auto">
</audio>

<audio
    id="deathSound"
    src="DEATH_SOUND_HERE"
    preload="auto">
</audio>


<script>

// ============================================================
// CANVAS
// ============================================================

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const info = document.getElementById("info");


// ============================================================
// AUDIO
// ============================================================

const bgMusic = document.getElementById("bgMusic");
const deathSound = document.getElementById("deathSound");

bgMusic.volume = 0.5;
deathSound.volume = 0.8;


// ============================================================
// PLAYER SKIN
// ============================================================

const playerImg = new Image();

playerImg.src = "PLAYER_IMAGE_HERE";


// ============================================================
// TROLL FACE
// ============================================================

const trollImg = new Image();

trollImg.src = "TROLL_FACE_HERE";


// ============================================================
// GAME STATE
// ============================================================

let gameState = "START";

let speed = 6;

let distance = 0;
let deathStarted = 0;
let particles = [];
let screenShake = 0;

function startDeathEffect(cx, cy) {
    gameState = "DYING";
    deathStarted = performance.now();
    screenShake = 12;
    particles = [];

    // Các mảnh neon bắn tung ra khi chạm gai
    const colors = ["#ff1744", "#ff3d81", "#ffffff", "#00e5ff", "#ff9100"];
    for (let i = 0; i < 34; i++) {
        const angle = Math.random() * Math.PI * 2;
        const power = 2 + Math.random() * 6;
        particles.push({
            x: cx, y: cy,
            vx: Math.cos(angle) * power,
            vy: Math.sin(angle) * power - 1.5,
            size: 3 + Math.random() * 7,
            life: 1,
            color: colors[Math.floor(Math.random() * colors.length)],
            spin: (Math.random() - 0.5) * 0.25,
            rotation: Math.random() * Math.PI
        });
    }
}


// ============================================================
// PLAYER
// ============================================================

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


// ============================================================
// OBSTACLES
// ============================================================

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


// ============================================================
// MUSIC
// ============================================================

function playMusic() {

    bgMusic.currentTime = 0;

    bgMusic.play().catch(function(error) {

        console.log("Music blocked:", error);

    });

}


function stopMusic() {

    bgMusic.pause();

    bgMusic.currentTime = 0;

}


// ============================================================
// DEATH SOUND
// ============================================================

function playDeathSound() {

    deathSound.currentTime = 0;

    deathSound.play().catch(function(error) {

        console.log("Death sound blocked:", error);

    });

}


// ============================================================
// START / JUMP
// ============================================================

function jump() {

    if (
        gameState === "START" ||
        gameState === "GAMEOVER" ||
        gameState === "VICTORY"
    ) {

        resetGame();

        gameState = "PLAYING";

        playMusic();

        return;
    }


    if (
        gameState === "PLAYING" &&
        player.isGrounded
    ) {

        player.vy = player.jumpPower;

        player.isGrounded = false;

    }

}


// ============================================================
// KEYBOARD
// ============================================================

window.addEventListener("keydown", function(e) {

    if (
        e.code === "Space" ||
        e.code === "ArrowUp"
    ) {

        e.preventDefault();

        jump();

    }

});


// ============================================================
// MOUSE
// ============================================================

canvas.addEventListener("mousedown", function() {

    jump();

});


// ============================================================
// RESET
// ============================================================

function resetGame() {

    player.y = floorY - player.size;

    player.vy = 0;

    player.rotation = 0;

    player.isGrounded = true;

    distance = 0;
    particles = [];
    screenShake = 0;

    activeObstacles =
        levelObstacles.map(function(obs) {

            return {

                x: obs.x,

                width: 35,

                height: 35,

                type: obs.type

            };

        });

}


// ============================================================
// UPDATE
// ============================================================

function update() {

    if (gameState === "DYING") {
        const elapsed = performance.now() - deathStarted;
        for (const p of particles) {
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.16;
            p.vx *= 0.985;
            p.life -= 0.022;
            p.rotation += p.spin;
        }
        particles = particles.filter(p => p.life > 0);
        screenShake *= 0.82;
        if (elapsed > 700) gameState = "GAMEOVER";
        return;
    }

    if (gameState !== "PLAYING") return;

    distance += speed;


    let progress =
        Math.min(
            100,
            Math.floor(
                distance / LEVEL_LENGTH * 100
            )
        );


    // Gravity

    player.vy += player.gravity;

    player.y += player.vy;


    // Ground

    if (player.y + player.size >= floorY) {

        player.y =
            floorY - player.size;

        player.vy = 0;

        player.isGrounded = true;

        player.rotation =
            Math.round(
                player.rotation /
                (Math.PI / 2)
            ) *
            (Math.PI / 2);

    }
    else {

        player.rotation += 0.15;

    }


    // ========================================================
    // COLLISION
    // ========================================================

    for (let obs of activeObstacles) {

        let currentX =
            obs.x -
            distance +
            player.x;

        let hitMargin = 6;


        if (

            player.x +
            player.size -
            hitMargin >
            currentX

            &&

            player.x +
            hitMargin <
            currentX +
            obs.width

            &&

            player.y +
            player.size -
            hitMargin >
            floorY -
            obs.height

        ) {

            startDeathEffect(
                player.x + player.size / 2,
                player.y + player.size / 2
            );

            stopMusic();
            playDeathSound();
            info.innerText = "💥 BÙM! Bạn đã chạm chướng ngại vật...";
            break;

        }

    }


    // ========================================================
    // VICTORY
    // ========================================================

    if (distance >= LEVEL_LENGTH) {

        gameState = "VICTORY";

        stopMusic();

        info.innerText =
            "🎉 XUẤT SẮC! BẠN ĐÃ HOÀN THÀNH 100%!";

    }
    else if (gameState === "PLAYING") {

        info.innerText =
            "Tiến độ: " +
            progress +
            "%";

    }

}


// ============================================================
// BACKGROUND
// ============================================================

function drawBackground() {
    // Bầu trời đêm chuyển sắc xanh tím
    const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
    grad.addColorStop(0, "#05091f");
    grad.addColorStop(0.52, "#111c59");
    grad.addColorStop(1, "#32145b");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Sao nhấp nháy và vệt sáng
    for (let i = 0; i < 70; i++) {
        const x = (i * 137 - distance * (0.08 + (i % 3) * 0.025) + 2000) % canvas.width;
        const y = (i * 47 + 19) % 245;
        const r = (i % 4 === 0) ? 2 : 1;
        ctx.globalAlpha = 0.35 + 0.45 * Math.abs(Math.sin(performance.now() / 700 + i));
        ctx.fillStyle = i % 5 === 0 ? "#00e5ff" : "#ffffff";
        ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
    }
    ctx.globalAlpha = 1;

    // Mặt trăng neon
    const moonGlow = ctx.createRadialGradient(650, 95, 8, 650, 95, 70);
    moonGlow.addColorStop(0, "rgba(175,205,255,0.95)");
    moonGlow.addColorStop(0.58, "rgba(103,124,255,0.75)");
    moonGlow.addColorStop(1, "rgba(80,70,255,0)");
    ctx.fillStyle = moonGlow;
    ctx.beginPath(); ctx.arc(650, 95, 70, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#c9d8ff";
    ctx.beginPath(); ctx.arc(650, 95, 36, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "rgba(112,135,220,0.35)";
    ctx.beginPath(); ctx.arc(638, 84, 8, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(663, 105, 11, 0, Math.PI * 2); ctx.fill();

    // Núi xa nhiều lớp tạo chiều sâu
    function mountainLayer(baseY, amp, step, color, parallax) {
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.moveTo(0, canvas.height);
        for (let x = -step; x <= canvas.width + step; x += step) {
            const xx = x - (distance * parallax) % step;
            const peakY = baseY - amp * (0.35 + 0.65 * Math.abs(Math.sin((x + 70) * 0.027)));
            ctx.lineTo(xx, peakY);
        }
        ctx.lineTo(canvas.width, canvas.height);
        ctx.closePath(); ctx.fill();
    }
    mountainLayer(300, 105, 58, "#171c58", 0.12);
    mountainLayer(330, 78, 42, "#10143e", 0.22);

    // Thành phố tương lai ở đường chân trời
    for (let i = 0; i < 24; i++) {
        const w = 16 + (i % 4) * 7;
        const h = 28 + ((i * 29) % 68);
        const x = (i * 43 - distance * 0.32) % (canvas.width + 50);
        const bx = x < -w ? x + canvas.width + 50 : x;
        ctx.fillStyle = i % 3 === 0 ? "#11183e" : "#0b1230";
        ctx.fillRect(bx, floorY - h + 8, w, h);
        ctx.fillStyle = i % 2 === 0 ? "#00e5ff" : "#ff3dba";
        ctx.globalAlpha = 0.75;
        for (let wy = floorY - h + 15; wy < floorY - 5; wy += 13) {
            ctx.fillRect(bx + 4, wy, 3, 4);
            if (w > 22) ctx.fillRect(bx + 12, wy, 3, 4);
        }
        ctx.globalAlpha = 1;
    }

    // Lưới neon ở mặt đất
    ctx.strokeStyle = "rgba(0,229,255,0.16)";
    ctx.lineWidth = 1;
    for (let x = -80; x < canvas.width + 80; x += 40) {
        const xx = x - (distance * 0.7) % 40;
        ctx.beginPath(); ctx.moveTo(xx, floorY); ctx.lineTo(canvas.width / 2 + (xx - canvas.width / 2) * 1.8, canvas.height); ctx.stroke();
    }
    for (let y = floorY + 18; y < canvas.height; y += 18) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
    }
}


// ============================================================
// DRAW
// ============================================================

function draw() {

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    drawBackground();


    // ========================================================
    // FLOOR
    // ========================================================

    ctx.fillStyle = "#e5fbff";

    ctx.shadowColor = "#00e5ff";

    ctx.shadowBlur = 18;

    ctx.fillRect(
        0,
        floorY,
        canvas.width,
        4
    );

    ctx.shadowBlur = 0;

    const floorGrad = ctx.createLinearGradient(0, floorY, 0, canvas.height);
    floorGrad.addColorStop(0, "#10163d");
    floorGrad.addColorStop(1, "#050817");
    ctx.fillStyle = floorGrad;

    ctx.fillRect(
        0,
        floorY + 4,
        canvas.width,
        canvas.height - floorY
    );


    // ========================================================
    // PROGRESS BAR
    // ========================================================

    let progressRatio =
        Math.min(
            1,
            distance / LEVEL_LENGTH
        );


    ctx.fillStyle =
        "rgba(255,255,255,0.2)";

    ctx.fillRect(
        200,
        15,
        400,
        10
    );


    ctx.fillStyle = "#00ffcc";

    ctx.fillRect(
        200,
        15,
        400 * progressRatio,
        10
    );


    // ========================================================
    // FINISH
    // ========================================================

    let finishX =
        LEVEL_LENGTH -
        distance +
        player.x;


    if (
        finishX <
        canvas.width + 100
    ) {

        ctx.fillStyle = "#00ffcc";

        ctx.shadowColor = "#00ffcc";

        ctx.shadowBlur = 15;

        ctx.fillRect(
            finishX,
            floorY - 130,
            15,
            130
        );

        ctx.shadowBlur = 0;

        ctx.fillStyle = "#ffffff";

        ctx.font = "bold 16px Arial";

        ctx.textAlign = "left";

        ctx.fillText(
            "FINISH",
            finishX - 15,
            floorY - 140
        );

    }


    // ========================================================
    // OBSTACLES
    // ========================================================

    for (let obs of activeObstacles) {

        let currentX =
            obs.x -
            distance +
            player.x;


        if (
            currentX > -50 &&
            currentX < canvas.width + 50
        ) {


            // SPIKE

            if (obs.type === "spike") {

                ctx.fillStyle = "#ff245f";

                ctx.shadowColor = "#ff1744";

                ctx.shadowBlur = 16;

                ctx.beginPath();

                ctx.moveTo(
                    currentX,
                    floorY
                );

                ctx.lineTo(
                    currentX +
                    obs.width / 2,
                    floorY -
                    obs.height
                );

                ctx.lineTo(
                    currentX +
                    obs.width,
                    floorY
                );

                ctx.closePath();

                ctx.fill();

                ctx.strokeStyle = "#ffffff";

                ctx.lineWidth = 2;

                ctx.stroke();

                ctx.shadowBlur = 0;

            }


            // BLOCK

            else {

                ctx.fillStyle = "#ff9900";

                ctx.shadowColor = "#ff9900";

                ctx.shadowBlur = 10;

                ctx.fillRect(
                    currentX,
                    floorY - obs.height,
                    obs.width,
                    obs.height
                );

                ctx.strokeStyle = "#ffffff";

                ctx.lineWidth = 2;

                ctx.strokeRect(
                    currentX,
                    floorY - obs.height,
                    obs.width,
                    obs.height
                );

                ctx.shadowBlur = 0;

            }

        }

    }


    // ========================================================
    // HIT EFFECT: MẢNH VỠ NEON BAY RA KHI CHẠM GAI
    // ========================================================
    if (gameState === "DYING") {
        ctx.save();
        for (const p of particles) {
            ctx.globalAlpha = Math.max(0, p.life);
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rotation);
            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 14;
            ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.65);
            ctx.setTransform(1, 0, 0, 1, 0, 0);
        }
        ctx.restore();
        ctx.globalAlpha = 1;
        ctx.shadowBlur = 0;
    }

    // ========================================================
    // PLAYER
    // ========================================================

    if (gameState !== "DYING" && gameState !== "GAMEOVER") {
    ctx.save();

    ctx.translate(
        player.x + player.size / 2,
        player.y + player.size / 2
    );

    ctx.rotate(player.rotation);


    ctx.strokeStyle = "#00f0ff";

    ctx.lineWidth = 3;

    ctx.shadowColor = "#00f0ff";

    ctx.shadowBlur = 10;

    ctx.strokeRect(
        -player.size / 2,
        -player.size / 2,
        player.size,
        player.size
    );

    ctx.shadowBlur = 0;


    if (playerImg.complete) {

        ctx.drawImage(
            playerImg,
            -player.size / 2,
            -player.size / 2,
            player.size,
            player.size
        );

    }
    else {

        ctx.fillStyle = "#00ffcc";

        ctx.fillRect(
            -player.size / 2,
            -player.size / 2,
            player.size,
            player.size
        );

    }


    ctx.restore();
    }

    // ========================================================
    // START SCREEN
    // ========================================================

    if (gameState === "START") {

        ctx.fillStyle =
            "rgba(0,0,0,0.7)";

        ctx.fillRect(
            0,
            0,
            canvas.width,
            canvas.height
        );


        ctx.fillStyle = "#00f0ff";

        ctx.font =
            "bold 28px Arial";

        ctx.textAlign = "center";

        ctx.fillText(
            "FACE DASH - POP STAR EDITION",
            canvas.width / 2,
            canvas.height / 2 - 20
        );


        ctx.font = "18px Arial";

        ctx.fillStyle = "#ffffff";

        ctx.fillText(
            "Nhấn SPACE hoặc Click chuột để bắt đầu!",
            canvas.width / 2,
            canvas.height / 2 + 30
        );

    }


    // ========================================================
    // 💀 GAME OVER + TROLL FACE
    // ========================================================

    if (gameState === "GAMEOVER") {

        // Lớp phủ

        ctx.fillStyle =
            "rgba(0,0,0,0.75)";

        ctx.fillRect(
            0,
            0,
            canvas.width,
            canvas.height
        );


        // GAME OVER

        ctx.fillStyle = "#ff0055";

        ctx.font =
            "bold 42px Arial";

        ctx.textAlign = "center";

        ctx.shadowColor = "#ff0055";

        ctx.shadowBlur = 15;

        ctx.fillText(
            "GAME OVER",
            canvas.width / 2,
            65
        );

        ctx.shadowBlur = 0;


        // ====================================================
        // 😈 TROLL FACE
        // ====================================================

        if (trollImg.complete) {

            let trollSize = 190;

            ctx.drawImage(
                trollImg,

                canvas.width / 2 -
                trollSize / 2,

                90,

                trollSize,

                trollSize
            );

        }


        // Chữ

        ctx.fillStyle = "#ffffff";

        ctx.font =
            "bold 18px Arial";

        ctx.fillText(
            "💀 Bạn đã chết!",
            canvas.width / 2,
            315
        );


        ctx.font = "16px Arial";

        ctx.fillText(
            "Nhấn SPACE hoặc Click để chơi lại",
            canvas.width / 2,
            350
        );

    }


    // ========================================================
    // 🏆 VICTORY
    // ========================================================

    if (gameState === "VICTORY") {

        ctx.fillStyle =
            "rgba(0,0,0,0.8)";

        ctx.fillRect(
            0,
            0,
            canvas.width,
            canvas.height
        );


        ctx.fillStyle = "#00ffcc";

        ctx.font =
            "bold 36px Arial";

        ctx.textAlign = "center";

        ctx.fillText(
            "VICTORY! 100%",
            canvas.width / 2,
            canvas.height / 2 - 20
        );


        ctx.font = "20px Arial";

        ctx.fillStyle = "#ffffff";

        ctx.fillText(
            "Chúc mừng bạn đã hoàn thành màn chơi!",
            canvas.width / 2,
            canvas.height / 2 + 25
        );

    }

}


// ============================================================
// GAME LOOP
// ============================================================

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


# ============================================================
# GẮN FILE VÀO HTML
# ============================================================

game_html = game_html.replace(
    "MUSIC_URL_HERE",
    music_url
)

game_html = game_html.replace(
    "DEATH_SOUND_HERE",
    death_url
)

game_html = game_html.replace(
    "TROLL_FACE_HERE",
    troll_url
)

game_html = game_html.replace(
    "PLAYER_IMAGE_HERE",
    player_url
)


# ============================================================
# CHẠY GAME
# ============================================================

components.html(
    game_html,
    height=480
)
