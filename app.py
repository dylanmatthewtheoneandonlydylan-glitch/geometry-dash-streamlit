import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(
    page_title="Geometry Dash Custom Skin",
    layout="wide"
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

html, body {
    margin: 0;
    width: 100%;
    background: #0d0f18;
    font-family: Arial, sans-serif;
    color: white;
    user-select: none;
    overflow-x: hidden;
}
body {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    flex-direction: column;
    padding: 8px 0 12px;
    box-sizing: border-box;
}
canvas {
    display: block;
    width: min(98vw, 1400px);
    height: auto;
    border: 3px solid #00f0ff;
    box-shadow: 0 0 32px rgba(0,240,255,0.45);
    border-radius: 10px;
    background: #000;
}
#info {
    margin-top: 10px;
    font-size: clamp(16px, 1.8vw, 22px);
    font-weight: bold;
    text-align: center;
}

</style>

</head>

<body>

<canvas id="gameCanvas" width="1200" height="600"></canvas>

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

let speed = 7;

let distance = 0;
let deathStarted = 0;
let particles = [];
let winParticles = [];
let victoryTrail = [];
let victoryBurst = [];
let victoryPlayerY = 0;
let victoryPlayerX = 0;
let winningStarted = 0;
let winStarted = 0;
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

function startVictoryEffect() {
    winStarted = performance.now();
    winParticles = [];
    victoryTrail = [];
    victoryBurst = [];
    victoryPlayerY = player.y;
    victoryPlayerX = player.x;

    // Hạt nền nhẹ, chỉ xuất hiện rõ sau khi chạm cổng.
    const colors = ["#fff176", "#ffe95b", "#ffffff", "#ffef9a"];
    for (let i = 0; i < 95; i++) {
        winParticles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 1.8,
            vy: 0.5 + Math.random() * 2.6,
            size: 2 + Math.random() * 6,
            rotation: Math.random() * Math.PI,
            spin: (Math.random() - 0.5) * 0.12,
            color: colors[Math.floor(Math.random() * colors.length)],
            alpha: 0.45 + Math.random() * 0.55
        });
    }
}

function createFinishBurst(cx, cy) {
    victoryBurst = [];
    const colors = ["#fff176", "#ffe95b", "#ffffff", "#ffef9a", "#43e8ff"];
    for (let i = 0; i < 125; i++) {
        const angle = Math.random() * Math.PI * 2;
        const power = 2 + Math.random() * 8;
        victoryBurst.push({
            x: cx,
            y: cy,
            vx: Math.cos(angle) * power,
            vy: Math.sin(angle) * power,
            size: 3 + Math.random() * 8,
            life: 1,
            rotation: Math.random() * Math.PI,
            spin: (Math.random() - 0.5) * 0.22,
            color: colors[Math.floor(Math.random() * colors.length)]
        });
    }
}



// ============================================================
// PLAYER
// ============================================================

const player = {

    x: 180,

    y: 440,

    size: 54,

    vy: 0,

    gravity: 0.85,

    jumpPower: -13.8,

    isGrounded: false,

    rotation: 0

};


const floorY = 500;

const LEVEL_LENGTH = 5000;


// ============================================================
// OBSTACLES
// ============================================================

const levelObstacles = [
    { x: 600, type: "spike" },
    { x: 900, type: "spike" },
    { x: 1200, type: "block" },

    // Cặp gai 5-6: đặt sát nhau, không còn khe hở.
    { x: 1500, type: "spike" },
    { x: 1535, type: "spike" },
    { x: 1900, type: "block" },
    { x: 2100, type: "spike" },
    { x: 2320, type: "block" },

    // Ba gai nối liền nhau, mỗi gai rộng 35 px.
    { x: 2620, type: "spike" },
    { x: 2655, type: "spike" },
    { x: 2690, type: "spike" },
    { x: 3050, type: "block" },
    { x: 3270, type: "spike" },
    { x: 3305, type: "spike" }
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

    player.x = 180;
    victoryPlayerX = player.x;
    player.x = 180;
    player.y = floorY - player.size;

    player.vy = 0;

    player.rotation = 0;

    player.isGrounded = true;

    distance = 0;
    particles = [];
    winParticles = [];
    victoryTrail = [];
    victoryBurst = [];
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

    // Giai đoạn 1: khối vuông xoay, bay theo đường cong và lao vào tường FINISH.
    if (gameState === "WINNING") {
        const elapsed = performance.now() - winningStarted;
        const duration = 2100;
        const progress = Math.min(1, elapsed / duration);
        const wallX = canvas.width * 0.62;
        const startX = 180;
        const endX = wallX - player.size * 0.9;
        const baseY = floorY - player.size;
        const eased = progress * progress * (3 - 2 * progress);

        player.x = startX + (endX - startX) * eased;
        player.y = baseY - Math.sin(progress * Math.PI) * 145 + Math.sin(progress * Math.PI * 2) * 18;
        player.rotation += 0.28 + progress * 0.34;

        // Vệt cầu vồng bám sát phía sau khối vuông.
        const rainbow = ["#ff3b9d", "#ff8a35", "#ffe84a", "#58ff85", "#43e8ff", "#6875ff", "#d66bff"];
        for (let i = 0; i < 3; i++) {
            victoryTrail.push({
                x: player.x + player.size * 0.18 + Math.random() * 8,
                y: player.y + player.size * (0.25 + Math.random() * 0.5),
                size: 5 + Math.random() * 10,
                life: 1,
                color: rainbow[Math.floor(Math.random() * rainbow.length)]
            });
        }
        victoryTrail.forEach(p => { p.x -= 1.8; p.life -= 0.022; p.size *= 0.99; });
        victoryTrail = victoryTrail.filter(p => p.life > 0);

        if (progress >= 1) {
            // Giai đoạn 2: khối vuông chạm cổng, bùng sáng và biến mất.
            const impactX = wallX;
            const impactY = player.y + player.size / 2;
            createFinishBurst(impactX, impactY);
            victoryPlayerX = player.x;
            victoryPlayerY = player.y;
            player.x = -1000;
            player.y = -1000;
            gameState = "VICTORY";
            winStarted = performance.now();
            stopMusic();
            info.innerText = "🎉 XUẤT SẮC! BẠN ĐÃ HOÀN THÀNH 100%!";
        }
        return;
    }

    if (gameState === "VICTORY") {
        const t = performance.now() - winStarted;

        // Khối vuông bay lên nhẹ và xoay liên tục
        player.y = victoryPlayerY - Math.min(105, t * 0.055) + Math.sin(t / 115) * 8;
        player.rotation += 0.105;

        // Tạo vệt cầu vồng phía sau khối vuông
        if (Math.random() < 0.92) {
            const rainbow = ["#ff3b9d", "#ff8a35", "#ffe84a", "#58ff85", "#43e8ff", "#6875ff", "#d66bff"];
            victoryTrail.push({
                x: player.x + player.size * 0.28 + Math.random() * 8,
                y: player.y + player.size * (0.35 + Math.random() * 0.3),
                size: 7 + Math.random() * 10,
                life: 1,
                color: rainbow[Math.floor(Math.random() * rainbow.length)]
            });
        }
        victoryTrail.forEach(p => { p.x -= 2.2; p.life -= 0.025; p.size *= 0.992; });
        victoryTrail = victoryTrail.filter(p => p.life > 0);

        for (const p of victoryBurst) {
            p.x += p.vx; p.y += p.vy;
            p.vy += 0.035; p.vx *= 0.992;
            p.life -= 0.009; p.rotation += p.spin;
        }
        victoryBurst = victoryBurst.filter(p => p.life > 0);

        for (const p of winParticles) {
            p.x += p.vx; p.y += p.vy; p.rotation += p.spin;
            if (p.y > canvas.height + 12) {
                p.y = -10; p.x = Math.random() * canvas.width;
            }
            if (p.x < -10) p.x = canvas.width + 10;
            if (p.x > canvas.width + 10) p.x = -10;
        }
        return;
    }

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
        gameState = "WINNING";
        winningStarted = performance.now();
        startVictoryEffect();
        victoryPlayerX = player.x;
        info.innerText = "✨ ĐANG LAO VÀO TƯỜNG FINISH!";
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
    // Nền xanh đen kiểu Geometry Dash — không còn phủ nền tím.
    const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
    grad.addColorStop(0, "#020719");
    grad.addColorStop(0.55, "#07143b");
    grad.addColorStop(1, "#020617");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Sao nhỏ nhấp nháy.
    for (let i = 0; i < 78; i++) {
        const x = ((i * 137 - distance * (0.08 + (i % 3) * 0.025) + 4000) % canvas.width + canvas.width) % canvas.width;
        const y = (i * 47 + 19) % 285;
        ctx.globalAlpha = 0.28 + 0.65 * Math.abs(Math.sin(performance.now() / 650 + i));
        ctx.fillStyle = i % 6 === 0 ? "#00eaff" : "#ffffff";
        ctx.fillRect(x, y, i % 4 === 0 ? 3 : 2, i % 4 === 0 ? 3 : 2);
    }
    ctx.globalAlpha = 1;

    // Hai lớp núi hình học xanh đậm.
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
        ctx.closePath();
        ctx.fill();
    }
    mountainLayer(365, 85, 65, "#0b1b50", 0.12);
    mountainLayer(400, 62, 45, "#07102f", 0.22);

    // Thành phố neon sát đường chân trời.
    for (let i = 0; i < 28; i++) {
        const w = 15 + (i % 4) * 6;
        const h = 25 + ((i * 29) % 65);
        let x = ((i * 43 - distance * 0.32 + 5000) % (canvas.width + 50));
        if (x > canvas.width) x -= canvas.width + 50;
        ctx.fillStyle = "#050b25";
        ctx.fillRect(x, floorY - h, w, h);
        ctx.fillStyle = i % 2 === 0 ? "#00eaff" : "#ff35ce";
        ctx.globalAlpha = 0.8;
        for (let wy = floorY - h + 8; wy < floorY - 5; wy += 13) {
            ctx.fillRect(x + 4, wy, 3, 4);
            if (w > 22) ctx.fillRect(x + 12, wy, 3, 4);
        }
        ctx.globalAlpha = 1;
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

    const barWidth = Math.min(560, canvas.width * 0.48);
    const barX = (canvas.width - barWidth) / 2;
    ctx.fillRect(
        barX,
        20,
        barWidth,
        14
    );


    ctx.fillStyle = "#00ffcc";

    ctx.fillRect(
        barX,
        20,
        barWidth * progressRatio,
        14
    );


    // ========================================================
    // FINISH PORTAL — cổng cyan giống ảnh tham khảo
    // ========================================================
    const finishX = (gameState === "WINNING" || gameState === "VICTORY")
        ? canvas.width * 0.62
        : LEVEL_LENGTH - distance + player.x + 105;
    if (finishX > -150 && finishX < canvas.width + 150) {
        const gateW = 100;
        const gateH = 205;
        const gateTop = floorY - gateH;
        const pulse = 0.82 + 0.18 * Math.sin(performance.now() / 105);
        ctx.save();
        ctx.globalAlpha = pulse;

        // Vầng sáng lớn phía sau cổng.
        const halo = ctx.createRadialGradient(finishX, gateTop + gateH * 0.52, 8, finishX, gateTop + gateH * 0.52, 180);
        halo.addColorStop(0, "rgba(0,255,255,0.45)");
        halo.addColorStop(0.45, "rgba(0,170,255,0.20)");
        halo.addColorStop(1, "rgba(0,120,255,0)");
        ctx.fillStyle = halo;
        ctx.fillRect(finishX - 185, gateTop - 45, 370, gateH + 90);

        // Lõi cổng xanh lam trong suốt.
        const portalGrad = ctx.createLinearGradient(finishX - gateW / 2, 0, finishX + gateW / 2, 0);
        portalGrad.addColorStop(0, "rgba(0,245,255,0.16)");
        portalGrad.addColorStop(0.5, "rgba(45,130,255,0.55)");
        portalGrad.addColorStop(1, "rgba(0,245,255,0.16)");
        ctx.fillStyle = portalGrad;
        ctx.beginPath();
        ctx.moveTo(finishX - gateW / 2, floorY);
        ctx.lineTo(finishX - gateW / 2, gateTop + 42);
        ctx.quadraticCurveTo(finishX - gateW / 2, gateTop, finishX, gateTop);
        ctx.quadraticCurveTo(finishX + gateW / 2, gateTop, finishX + gateW / 2, gateTop + 42);
        ctx.lineTo(finishX + gateW / 2, floorY);
        ctx.closePath();
        ctx.fill();

        // Viền cyan phát sáng.
        ctx.strokeStyle = "#00f5ff";
        ctx.lineWidth = 10;
        ctx.shadowColor = "#00eaff";
        ctx.shadowBlur = 30;
        ctx.beginPath();
        ctx.moveTo(finishX - gateW / 2, floorY);
        ctx.lineTo(finishX - gateW / 2, gateTop + 42);
        ctx.quadraticCurveTo(finishX - gateW / 2, gateTop, finishX, gateTop);
        ctx.quadraticCurveTo(finishX + gateW / 2, gateTop, finishX + gateW / 2, gateTop + 42);
        ctx.lineTo(finishX + gateW / 2, floorY);
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Oval năng lượng ở giữa cổng.
        ctx.strokeStyle = "#d8ffff";
        ctx.lineWidth = 3;
        ctx.shadowColor = "#ffffff";
        ctx.shadowBlur = 15;
        ctx.beginPath();
        ctx.ellipse(finishX, gateTop + gateH * 0.55, 25 + 3 * pulse, 64 + 3 * pulse, 0, 0, Math.PI * 2);
        ctx.stroke();
        ctx.shadowBlur = 0;

        ctx.fillStyle = "#dfffff";
        ctx.font = "bold 22px Arial";
        ctx.textAlign = "center";
        ctx.shadowColor = "#00eaff";
        ctx.shadowBlur = 15;
        ctx.fillText("FINISH", finishX, gateTop - 18);
        ctx.shadowBlur = 0;
        ctx.restore();
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
    // VỆT CẦU VỒNG KHI KHỐI VUÔNG ĐANG BAY TỚI FINISH
    // ========================================================
    if (gameState === "WINNING") {
        ctx.save();
        for (const p of victoryTrail) {
            ctx.globalAlpha = Math.max(0, p.life) * 0.85;
            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 15;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size * 0.55, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.restore();
        ctx.globalAlpha = 1;
        ctx.shadowBlur = 0;
    }

    // ========================================================
    // PLAYER
    // ========================================================

    if (gameState !== "DYING" && gameState !== "GAMEOVER" && gameState !== "VICTORY") {
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
            canvas.height / 2 - 35
        );


        ctx.font = "18px Arial";

        ctx.fillStyle = "#ffffff";

        ctx.fillText(
            "Nhấn SPACE hoặc Click chuột để bắt đầu!",
            canvas.width / 2,
            canvas.height / 2 + 25
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
            "bold 54px Arial";

        ctx.textAlign = "center";

        ctx.shadowColor = "#ff0055";

        ctx.shadowBlur = 15;

        ctx.fillText(
            "GAME OVER",
            canvas.width / 2,
            90
        );

        ctx.shadowBlur = 0;


        // ====================================================
        // 😈 TROLL FACE
        // ====================================================

        if (trollImg.complete) {

            let trollSize = 220;

            ctx.drawImage(
                trollImg,

                canvas.width / 2 -
                trollSize / 2,

                canvas.height * 0.25,

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
            canvas.height * 0.78
        );


        ctx.font = "16px Arial";

        ctx.fillText(
            "Nhấn SPACE hoặc Click để chơi lại",
            canvas.width / 2,
            canvas.height * 0.86
        );

    }


    // ========================================================
    // 🏆 VICTORY: khối vuông bay, vệt cầu vồng và hạt vàng
    // ========================================================
    if (gameState === "VICTORY") {
        const t = performance.now() - winStarted;

        // Giữ nền xanh đen, núi hình học, thành phố neon và mặt đất đã vẽ.
        // Không phủ lại bằng nền tím hoặc một ảnh nền cũ.

        // Cổng cyan ở trung tâm hiệu ứng chiến thắng.
        const gx = canvas.width * 0.62;
        const gateTop = floorY - 205;
        const pulse = 0.8 + 0.2 * Math.sin(t / 100);
        const portalGlow = ctx.createRadialGradient(gx, gateTop + 105, 5, gx, gateTop + 105, 190);
        portalGlow.addColorStop(0, "rgba(100,255,255,0.75)");
        portalGlow.addColorStop(0.38, "rgba(0,200,255,0.28)");
        portalGlow.addColorStop(1, "rgba(0,100,255,0)");
        ctx.fillStyle = portalGlow;
        ctx.fillRect(gx - 195, gateTop - 25, 390, 255);

        ctx.save();
        ctx.globalAlpha = pulse;
        ctx.fillStyle = "rgba(0,150,255,0.32)";
        ctx.beginPath();
        ctx.moveTo(gx - 50, floorY);
        ctx.lineTo(gx - 50, gateTop + 42);
        ctx.quadraticCurveTo(gx - 50, gateTop, gx, gateTop);
        ctx.quadraticCurveTo(gx + 50, gateTop, gx + 50, gateTop + 42);
        ctx.lineTo(gx + 50, floorY);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = "#00f5ff";
        ctx.lineWidth = 10;
        ctx.shadowColor = "#00eaff";
        ctx.shadowBlur = 35;
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.strokeStyle = "#e5ffff";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.ellipse(gx, gateTop + 112, 26, 64, 0, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();

        // Vệt sáng dọc và ánh lóe ngay thời điểm khối vuông chạm tường
        const flashAlpha = Math.max(0, 0.55 - t / 900);
        const flash = ctx.createRadialGradient(canvas.width * 0.62, canvas.height * 0.48, 5, canvas.width * 0.62, canvas.height * 0.48, canvas.width * 0.72);
        flash.addColorStop(0, `rgba(235,255,255,${flashAlpha})`);
        flash.addColorStop(0.28, `rgba(0,220,255,${flashAlpha * 0.62})`);
        flash.addColorStop(1, "rgba(0,120,255,0)");
        ctx.fillStyle = flash;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Tia sáng bung ra quanh màn hình như hiệu ứng thắng trong video
        const burstX = canvas.width * 0.57;
        const burstY = canvas.height * 0.53;
        const burstFade = Math.max(0, 1 - t / 1900);
        ctx.save();
        ctx.globalAlpha = burstFade * (0.5 + 0.5 * Math.sin(t / 45));
        for (let i = 0; i < 18; i++) {
            const a = (Math.PI * 2 * i / 18) + 0.12;
            const reach = Math.max(canvas.width, canvas.height) * 1.15;
            const spread = 0.045 + (i % 3) * 0.018;
            ctx.beginPath();
            ctx.moveTo(burstX, burstY);
            ctx.lineTo(burstX + Math.cos(a - spread) * reach, burstY + Math.sin(a - spread) * reach);
            ctx.lineTo(burstX + Math.cos(a + spread) * reach, burstY + Math.sin(a + spread) * reach);
            ctx.closePath();
            ctx.fillStyle = i % 3 === 0 ? "#fff176" : (i % 3 === 1 ? "#ffffff" : "#43e8ff");
            ctx.shadowColor = ctx.fillStyle;
            ctx.shadowBlur = 16;
            ctx.fill();
        }
        ctx.restore();

        // Các khối hình học mờ phía sau
        ctx.save();
        ctx.globalAlpha = 0.18;
        ctx.strokeStyle = "#168dff";
        ctx.lineWidth = 10;
        for (let i = 0; i < 7; i++) {
            const x = ((i * 205 - t * 0.035) % (canvas.width + 230) + canvas.width + 230) % (canvas.width + 230) - 115;
            ctx.strokeRect(x, 35 + (i % 3) * 125, 135, 100);
        }
        ctx.restore();

        // Ánh sáng trắng hồng rực ở cạnh phải
        const glowX = canvas.width * 0.88;
        const glow = ctx.createLinearGradient(glowX - 45, 0, glowX + 40, 0);
        glow.addColorStop(0, "rgba(255,255,255,0)");
        glow.addColorStop(0.55, "rgba(180,255,255,0.9)");
        glow.addColorStop(1, "rgba(255,255,255,0)");
        ctx.fillStyle = glow;
        ctx.fillRect(glowX - 45, 0, 85, canvas.height);

        // Vệt cầu vồng nhiều lớp, nằm phía sau nhân vật
        ctx.save();
        ctx.lineCap = "round";
        const tx = canvas.width * 0.62;
        const ty = canvas.height * 0.52;
        const trailColors = ["#ff3b9d", "#ff8a35", "#ffe84a", "#58ff85", "#43e8ff", "#6875ff", "#d66bff"];
        for (let i = 0; i < trailColors.length; i++) {
            ctx.beginPath();
            ctx.moveTo(tx - 4, ty + (i - 3) * 3);
            ctx.bezierCurveTo(tx - 65, ty - 22 + (i - 3) * 5, tx - 120, ty + 28 + (i - 3) * 5, tx - 205, ty + 8 + (i - 3) * 5);
            ctx.strokeStyle = trailColors[i];
            ctx.globalAlpha = 0.72;
            ctx.lineWidth = 5;
            ctx.shadowColor = trailColors[i];
            ctx.shadowBlur = 13;
            ctx.stroke();
        }
        ctx.restore();

        // Những đốm sáng vuông nhỏ nằm trên vệt cầu vồng
        ctx.save();
        for (const p of victoryTrail) {
            ctx.globalAlpha = Math.max(0, p.life) * 0.85;
            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 13;
            ctx.fillRect(p.x, p.y, p.size, p.size);
        }
        ctx.restore();

        // Hạt vuông vàng bay tung tóe
        ctx.save();
        for (const p of victoryBurst) {
            ctx.globalAlpha = Math.max(0, p.life);
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rotation);
            ctx.fillStyle = p.color;
            ctx.shadowColor = "#fff176";
            ctx.shadowBlur = 12;
            ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);
            ctx.setTransform(1, 0, 0, 1, 0, 0);
        }
        ctx.restore();

        // Các hạt vuông vàng lấp lánh trong nền
        ctx.save();
        for (const p of winParticles) {
            ctx.globalAlpha = p.alpha;
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rotation);
            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 8;
            ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);
            ctx.setTransform(1, 0, 0, 1, 0, 0);
        }
        ctx.restore();
        ctx.globalAlpha = 1;
        ctx.shadowBlur = 0;

        // Không dùng banner/ảnh cũ; tập trung vào cổng FINISH và hiệu ứng hoàn thành.

        // Chữ LEVEL COMPLETE xanh lá kiểu pixel game
        ctx.save();
        ctx.textAlign = "center";
        ctx.font = `900 ${Math.min(58, canvas.width * 0.052)}px monospace`;
        ctx.lineJoin = "round";
        ctx.lineWidth = 7;
        ctx.strokeStyle = "#164b17";
        ctx.shadowColor = "#83ff35";
        ctx.shadowBlur = 18;
        ctx.strokeText("LEVEL COMPLETE!", canvas.width * 0.5, canvas.height * 0.70);
        ctx.fillStyle = "#7cff35";
        ctx.fillText("LEVEL COMPLETE!", canvas.width * 0.5, canvas.height * 0.31);
        ctx.lineWidth = 2;
        ctx.strokeStyle = "#d6ff9d";
        ctx.strokeText("LEVEL COMPLETE!", canvas.width * 0.5, canvas.height * 0.70);
        ctx.restore();

        ctx.textAlign = "center";
        ctx.fillStyle = "#ffffff";
        ctx.font = `bold ${Math.min(20, canvas.width * 0.017)}px monospace`;
        ctx.shadowColor = "#000000";
        ctx.shadowBlur = 5;
        ctx.fillText("100%  •  Nhấn SPACE hoặc Click để chơi lại", canvas.width * 0.5, canvas.height * 0.88);
        ctx.shadowBlur = 0;
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
    height=760
)
