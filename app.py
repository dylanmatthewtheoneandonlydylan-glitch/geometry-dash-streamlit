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
# ĐỌC FILE ÂM THANH + TROLL FACE + NỀN SẢNH CHỜ
# ============================================================

with open("pop_star.mp3", "rb") as f:
    music_url = "data:audio/mpeg;base64," + base64.b64encode(f.read()).decode()

with open("vine-boom.mp3", "rb") as f:
    death_url = "data:audio/mpeg;base64," + base64.b64encode(f.read()).decode()

with open("final-fantasy-vii-victory-fanfare-1.mp3", "rb") as f:
    victory_url = "data:audio/mpeg;base64," + base64.b64encode(f.read()).decode()

with open("lobby-music.mp3", "rb") as f:
    lobby_music_url = "data:audio/mpeg;base64," + base64.b64encode(f.read()).decode()

with open("trollface.png", "rb") as f:
    troll_url = "data:image/png;base64," + base64.b64encode(f.read()).decode()

with open("player.png", "rb") as f:
    player_url = "data:image/png;base64," + base64.b64encode(f.read()).decode()

try:
    with open("bg.png", "rb") as f:
        lobby_bg_url = "data:image/png;base64," + base64.b64encode(f.read()).decode()
except FileNotFoundError:
    try:
        with open("bg.jpg", "rb") as f:
            lobby_bg_url = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        lobby_bg_url = ""


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
    Hãy trả lời câu hỏi bắt buộc để tiếp tục!
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

<audio
    id="victorySound"
    src="VICTORY_SOUND_HERE"
    preload="auto">
</audio>

<audio
    id="lobbyMusic"
    src="LOBBY_MUSIC_URL_HERE"
    loop
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
const victorySound = document.getElementById("victorySound");
const lobbyMusic = document.getElementById("lobbyMusic");

bgMusic.volume = 0.5;
deathSound.volume = 0.8;
victorySound.volume = 1.0;
lobbyMusic.volume = 0.35;


// ============================================================
// IMAGES
// ============================================================

const playerImg = new Image();
playerImg.src = "PLAYER_IMAGE_HERE";

const trollImg = new Image();
trollImg.src = "TROLL_FACE_HERE";

const lobbyBgImg = new Image();
lobbyBgImg.src = "LOBBY_BG_HERE";


// ============================================================
// GAME STATE
// ============================================================

let gameState = "MODAL_QUESTION"; 
let selectedDifficulty = "NORMAL";
let menuDistance = 0;
let menuCube = { x: 80, y: 0, vy: 0, rotation: 0, grounded: true, nextJump: 0 };
let menuObstacles = [];
let menuLastObstacle = 0;
let mouseHeld = false;

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
let lastFrameTime = 0;
let frameScale = 1;

function startDeathEffect(cx, cy) {
    gameState = "DYING";
    deathStarted = performance.now();
    screenShake = 12;
    particles = [];

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
let LEVEL_LENGTH = 5000;


// ============================================================
// OBSTACLES
// ============================================================

const levelObstacles = [
    { x: 600, type: "spike" },
    { x: 900, type: "spike" },
    { x: 1200, type: "block" },
    { x: 1500, type: "spike" },
    { x: 1535, type: "spike" },
    { x: 1900, type: "block" },
    { x: 2100, type: "spike" },
    { x: 2320, type: "block" },
    { x: 2620, type: "spike" },
    { x: 2655, type: "spike" },
    { x: 2690, type: "spike" },
    { x: 3050, type: "block" },
    { x: 3270, type: "spike" },
    { x: 3305, type: "spike" }
];

const normalObstacles = levelObstacles.concat([
    { x: 3650, type: "spike" }, { x: 3685, type: "spike" },
    { x: 4020, type: "block" }, { x: 4330, type: "spike" },
    { x: 4365, type: "spike" }, { x: 4700, type: "block" },
    { x: 5020, type: "spike" }, { x: 5055, type: "spike" },
    { x: 5400, type: "block" }, { x: 5730, type: "spike" },
    { x: 5765, type: "spike" }, { x: 6100, type: "block" }
]);

const hardObstacles = [
    { x: 600, type: "spike" },
    { x: 900, type: "spike" }, { x: 935, type: "spike" },
    { x: 1250, type: "block", width: 42, height: 42 },
    { x: 1580, type: "pillar", width: 92, height: 48 },
    { x: 1700, type: "spike" },
    { x: 1780, type: "pillar", width: 92, height: 82 },
    { x: 1905, type: "spike" },
    { x: 1980, type: "pillar", width: 100, height: 116 },
    { x: 2310, type: "bar", width: 112, height: 38 },
    { x: 2650, type: "spike" }, { x: 2685, type: "spike" },
    { x: 3010, type: "block", width: 44, height: 44 },
    { x: 3350, type: "pillar", width: 92, height: 58 },
    { x: 3470, type: "spike" },
    { x: 3560, type: "pillar", width: 100, height: 98 },
    { x: 3890, type: "spike" }, { x: 3925, type: "spike" },
    { x: 4260, type: "bar", width: 118, height: 42 },
    { x: 4610, type: "block", width: 44, height: 44 },
    { x: 4950, type: "spike" }, { x: 4985, type: "spike" },
    { x: 5320, type: "pillar", width: 96, height: 72 },
    { x: 5445, type: "spike" },
    { x: 5535, type: "pillar", width: 100, height: 108 },
    { x: 5870, type: "bar", width: 120, height: 40 },
    { x: 6210, type: "spike" }, { x: 6245, type: "spike" },
    { x: 6580, type: "block", width: 44, height: 44 },
    { x: 6920, type: "spike" }, { x: 6955, type: "spike" },
    { x: 7290, type: "bar", width: 118, height: 38 }
];

let activeObstacles = [];


// ============================================================
// AUDIO CONTROLS
// ============================================================

function playLobbyMusic() {
    bgMusic.pause();
    victorySound.pause();
    lobbyMusic.play().catch(function(error) {
        console.log("Lobby music blocked:", error);
    });
}

function stopLobbyMusic() {
    lobbyMusic.pause();
    lobbyMusic.currentTime = 0;
}

function playMusic() {
    stopLobbyMusic();
    stopVictorySound();
    bgMusic.currentTime = 0;
    bgMusic.play().catch(function(error) { console.log("Music blocked:", error); });
}

function stopMusic() {
    bgMusic.pause();
    bgMusic.currentTime = 0;
}

function playDeathSound() {
    deathSound.currentTime = 0;
    deathSound.play().catch(function(error) { console.log("Death sound blocked:", error); });
}

function playVictorySound() {
    stopMusic();
    stopLobbyMusic();
    victorySound.pause();
    victorySound.currentTime = 0;
    const result = victorySound.play();
    if (result && typeof result.catch === "function") {
        result.catch(function(error) {
            console.error("Không phát được nhạc FINISH:", error);
        });
    }
}

function stopVictorySound() {
    victorySound.pause();
    victorySound.currentTime = 0;
}


// ============================================================
// START / JUMP
// ============================================================

function jump() {
    if (
        gameState === "MENU" ||
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
// INPUT EVENTS
// ============================================================

window.addEventListener("keydown", function(e) {
    if (e.code === "Space" || e.code === "ArrowUp") {
        if (gameState === "MODAL_QUESTION") return;
        e.preventDefault();
        if (gameState === "MENU") {
            resetGame();
            gameState = "PLAYING";
            playMusic();
            info.innerText = "Độ khó: " + selectedDifficulty + " • Tiến độ: 0%";
        } else {
            jump();
        }
    }
});

canvas.addEventListener("mousedown", function(e) {
    if (e.button !== 0) return;
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * canvas.width / rect.width;
    const y = (e.clientY - rect.top) * canvas.height / rect.height;

    if (gameState === "MODAL_QUESTION") {
        handleModalClick(x, y);
        return;
    }

    if (gameState !== "MENU" && x >= 18 && x <= 145 && y >= 16 && y <= 62) {
        mouseHeld = false;
        goToMenu();
        return;
    }
    if (gameState === "MENU") {
        handleMenuClick(x, y);
        return;
    }
    mouseHeld = true;
    jump();
});

window.addEventListener("mouseup", function() { mouseHeld = false; });
window.addEventListener("blur", function() { mouseHeld = false; });

function goToMenu() {
    stopMusic(); stopVictorySound();
    deathSound.pause(); deathSound.currentTime = 0;
    gameState = "MENU";
    playLobbyMusic();
    distance = 0;
    particles = []; winParticles = []; victoryTrail = []; victoryBurst = [];
    menuCube.x = 80; menuCube.y = floorY - 44; menuCube.vy = 0;
    menuCube.grounded = true; menuCube.nextJump = performance.now() + 300;
    info.innerText = "Chọn EASY, NORMAL hoặc HARD để bắt đầu!";
}


// ============================================================
// RESET
// ============================================================

function resetGame() {
    stopVictorySound();

    player.x = 180;
    victoryPlayerX = player.x;
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

    const difficultyConfig = {
        EASY:   { speed: 6.0, length: 5000, obstacles: levelObstacles.slice(0, 7) },
        NORMAL: { speed: 7.0, length: 6500, obstacles: normalObstacles },
        HARD:   { speed: 7.4, length: 7900, obstacles: hardObstacles }
    };
    const cfg = difficultyConfig[selectedDifficulty] || difficultyConfig.NORMAL;
    speed = cfg.speed;
    LEVEL_LENGTH = cfg.length;
    activeObstacles = cfg.obstacles
        .filter(function(obs) { return obs.x < LEVEL_LENGTH - 850; })
        .map(function(obs) {
            return { x: obs.x, width: obs.width || 35, height: obs.height || 35, type: obs.type };
        });
}


// ============================================================
// UPDATE
// ============================================================

function update() {
    if (gameState === "MODAL_QUESTION") {
        return;
    }

    if (gameState === "MENU") {
        menuDistance += 3.2 * frameScale;
        menuCube.x += 2.4 * frameScale;
        if (menuCube.x > canvas.width + 50) menuCube.x = -55;
        if (!menuCube.y) menuCube.y = floorY - 44;
        menuCube.vy += 0.72 * frameScale;
        menuCube.y += menuCube.vy * frameScale;
        if (menuCube.y >= floorY - 44) {
            menuCube.y = floorY - 44;
            menuCube.vy = 0;
            menuCube.grounded = true;
            menuCube.rotation = Math.round(menuCube.rotation / (Math.PI / 2)) * (Math.PI / 2);
            if (performance.now() > menuCube.nextJump) {
                if (Math.random() < 0.78) {
                    menuCube.vy = -(10.5 + Math.random() * 1.8);
                    menuCube.grounded = false;
                }
                menuCube.nextJump = performance.now() + 450 + Math.random() * 1100;
            }
        } else {
            menuCube.grounded = false;
            menuCube.rotation += 0.12 * frameScale;
        }

        if (performance.now() - menuLastObstacle > 1050 + Math.random() * 750) {
            const size = 25 + Math.random() * 12;
            const last = menuObstacles.length ? menuObstacles[menuObstacles.length - 1] : null;
            if (!last || last.x < canvas.width - 220) {
                menuObstacles.push({ x: canvas.width + 35, type: "spike", size: size });
                if (Math.random() < 0.22) {
                    menuObstacles.push({ x: canvas.width + 35 + size + 12, type: "spike", size: size });
                }
            }
            menuLastObstacle = performance.now();
        }
        menuObstacles.forEach(o => o.x -= 4.0 * frameScale);
        menuObstacles = menuObstacles.filter(o => o.x > -90);

        const approachingSpike = menuObstacles.some(o =>
            o.type === "spike" && o.x + o.size > menuCube.x + 32 &&
            o.x < menuCube.x + 118 && menuCube.grounded
        );
        if (approachingSpike && menuCube.grounded) {
            menuCube.vy = -(10.8 + Math.random() * 0.6);
            menuCube.grounded = false;
        }
        return;
    }

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
            playVictorySound();
            info.innerText = "🎉 XUẤT SẮC! BẠN ĐÃ HOÀN THÀNH 100%!";
        }
        return;
    }

    if (gameState === "VICTORY") {
        const t = performance.now() - winStarted;
        player.y = victoryPlayerY - Math.min(105, t * 0.055) + Math.sin(t / 115) * 8;
        player.rotation += 0.105;

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

    if (mouseHeld && player.isGrounded) {
        player.vy = player.jumpPower;
        player.isGrounded = false;
    }

    distance += speed * frameScale;
    let progress = Math.min(100, Math.floor(distance / LEVEL_LENGTH * 100));

    const previousY = player.y;
    player.vy += player.gravity * frameScale;
    player.y += player.vy * frameScale;

    let landedOnPillar = false;
    for (const obs of activeObstacles) {
        if (obs.type !== "pillar") continue;
        const pillarX = obs.x - distance + player.x;
        const pillarTop = floorY - obs.height;
        const overlapsX = player.x + player.size - 5 > pillarX && player.x + 5 < pillarX + obs.width;
        const wasAbove = previousY + player.size <= pillarTop + 8;
        const crossedTop = player.y + player.size >= pillarTop;
        if (overlapsX && wasAbove && crossedTop && player.vy >= 0) {
            player.y = pillarTop - player.size;
            player.vy = 0;
            player.isGrounded = true;
            landedOnPillar = true;
            break;
        }
    }

    if (!landedOnPillar && player.y + player.size >= floorY) {
        player.y = floorY - player.size;
        player.vy = 0;
        player.isGrounded = true;
        player.rotation = Math.round(player.rotation / (Math.PI / 2)) * (Math.PI / 2);
    } else {
        player.rotation += 0.15 * frameScale;
    }

    for (let obs of activeObstacles) {
        let currentX = obs.x - distance + player.x;
        let hitMargin = 6;

        if (obs.type === "pillar" && player.y + player.size <= floorY - obs.height + 3) continue;

        if (
            player.x + player.size - hitMargin > currentX &&
            player.x + hitMargin < currentX + obs.width &&
            player.y + player.size - hitMargin > floorY - obs.height
        ) {
            startDeathEffect(player.x + player.size / 2, player.y + player.size / 2);
            stopMusic();
            playDeathSound();
            info.innerText = "💥 BÙM! Bạn đã chạm chướng ngại vật...";
            break;
        }
    }

    const finishTargetX = canvas.width * 0.62;
    const finishTriggerDistance = LEVEL_LENGTH - (finishTargetX - player.x);
    if (distance >= finishTriggerDistance) {
        distance = finishTriggerDistance;
        gameState = "WINNING";
        winningStarted = performance.now();
        startVictoryEffect();
        victoryPlayerX = player.x;
        info.innerText = "✨ ĐANG LAO VÀO TƯỜNG FINISH!";
    } else if (gameState === "PLAYING") {
        info.innerText = "Tiến độ: " + progress + "%";
    }
}


// ============================================================
// BACKGROUND
// ============================================================

function drawBackground() {
    if (selectedDifficulty === "NORMAL") {
        const lavaGrad = ctx.createLinearGradient(0, 0, 0, canvas.height);
        lavaGrad.addColorStop(0, "#190509");
        lavaGrad.addColorStop(0.58, "#45100b");
        lavaGrad.addColorStop(1, "#080407");
        ctx.fillStyle = lavaGrad;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        for (let i = 0; i < 30; i++) {
            const w = 24 + (i % 4) * 13;
            const h = 38 + ((i * 31) % 100);
            const x = ((i * 57 - distance * 0.22 + 7000) % (canvas.width + 70) + canvas.width + 70) % (canvas.width + 70) - 35;
            ctx.fillStyle = i % 2 ? "#32100f" : "#240a0b";
            ctx.fillRect(x, floorY - h, w, h);
            ctx.fillStyle = i % 3 ? "#ff5a1f" : "#ffd34d";
            ctx.globalAlpha = 0.45 + 0.35 * Math.abs(Math.sin(performance.now() / 300 + i));
            ctx.fillRect(x + 4, floorY - h + 12, 4, Math.max(8, h - 20));
            ctx.globalAlpha = 1;
        }
        ctx.fillStyle = "#f04412";
        ctx.globalAlpha = 0.45;
        ctx.fillRect(0, floorY + 8, canvas.width, 5);
        for (let i = 0; i < 12; i++) {
            const x = ((i * 93 - distance * 0.7) % (canvas.width + 60) + canvas.width + 60) % (canvas.width + 60) - 30;
            ctx.fillStyle = i % 2 ? "#ffb52e" : "#ff4018";
            ctx.fillRect(x, floorY + 15 + (i % 3) * 8, 25 + (i % 4) * 10, 3);
        }
        ctx.globalAlpha = 1;
        return;
    }
    if (selectedDifficulty === "HARD") {
        const cyberGrad = ctx.createLinearGradient(0, 0, 0, canvas.height);
        cyberGrad.addColorStop(0, "#08051f");
        cyberGrad.addColorStop(0.6, "#171044");
        cyberGrad.addColorStop(1, "#030613");
        ctx.fillStyle = cyberGrad;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        for (let i = 0; i < 65; i++) {
            const x = ((i * 149 - distance * (0.12 + (i % 3) * 0.04) + 9000) % canvas.width + canvas.width) % canvas.width;
            const y = (i * 43 + 17) % 300;
            ctx.globalAlpha = 0.35 + 0.55 * Math.abs(Math.sin(performance.now() / 420 + i));
            ctx.fillStyle = i % 2 ? "#19f5ff" : "#ff39df";
            ctx.fillRect(x, y, i % 5 === 0 ? 4 : 2, i % 5 === 0 ? 4 : 2);
        }
        ctx.globalAlpha = 1;
        ctx.strokeStyle = "#19dfff";
        ctx.globalAlpha = 0.28;
        ctx.lineWidth = 1;
        const gridOffset = (distance * 0.35) % 48;
        for (let x = -48; x < canvas.width + 48; x += 48) {
            ctx.beginPath(); ctx.moveTo(x - gridOffset, 0); ctx.lineTo(x - gridOffset, floorY); ctx.stroke();
        }
        for (let y = 32; y < floorY; y += 32) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
        }
        ctx.globalAlpha = 1;
        return;
    }

    const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
    grad.addColorStop(0, "#020719");
    grad.addColorStop(0.55, "#07143b");
    grad.addColorStop(1, "#020617");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < 78; i++) {
        const x = ((i * 137 - distance * (0.08 + (i % 3) * 0.025) + 4000) % canvas.width + canvas.width) % canvas.width;
        const y = (i * 47 + 19) % 285;
        ctx.globalAlpha = 0.28 + 0.65 * Math.abs(Math.sin(performance.now() / 650 + i));
        ctx.fillStyle = i % 6 === 0 ? "#00eaff" : "#ffffff";
        ctx.fillRect(x, y, i % 4 === 0 ? 3 : 2, i % 4 === 0 ? 3 : 2);
    }
    ctx.globalAlpha = 1;

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
// MÀN HÌNH CÂU HỎI BẮT BUỘC ĐẦU GAME
// ============================================================

function drawModalQuestion() {
    if (lobbyBgImg.complete && lobbyBgImg.naturalWidth !== 0) {
        ctx.drawImage(lobbyBgImg, 0, 0, canvas.width, canvas.height);
    } else {
        drawBackground();
    }

    ctx.fillStyle = "rgba(0, 0, 0, 0.78)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const boxW = 760;
    const boxH = 340;
    const boxX = (canvas.width - boxW) / 2;
    const boxY = (canvas.height - boxH) / 2;

    ctx.save();
    ctx.shadowColor = "#00ffff";
    ctx.shadowBlur = 25;
    ctx.fillStyle = "#050d21";
    ctx.strokeStyle = "#00f0ff";
    ctx.lineWidth = 4;
    roundRect(ctx, boxX, boxY, boxW, boxH, 24, true, true);
    ctx.shadowBlur = 0;

    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 29px monospace";
    ctx.shadowColor = "#ff39df";
    ctx.shadowBlur = 12;
    ctx.fillText("Trần Duy Long Có Bị Gay Không 🌈", canvas.width / 2, boxY + 75);
    ctx.shadowBlur = 0;

    const btnW = 290;
    const btnH = 75;
    const btnY = boxY + 165;
    
    const btn1X = boxX + 55;
    ctx.fillStyle = "#00ff70";
    ctx.shadowColor = "#00ff70";
    ctx.shadowBlur = 15;
    roundRect(ctx, btn1X, btnY, btnW, btnH, 16, true, false);
    ctx.shadowBlur = 0;
    ctx.fillStyle = "#06152c";
    ctx.font = "bold 21px monospace";
    ctx.fillText("Toi Dong Tinh", btn1X + btnW / 2, btnY + btnH / 2);

    const btn2X = boxX + boxW - 55 - btnW;
    ctx.fillStyle = "#ff1744";
    ctx.shadowColor = "#ff1744";
    ctx.shadowBlur = 15;
    roundRect(ctx, btn2X, btnY, btnW, btnH, 16, true, false);
    ctx.shadowBlur = 0;
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 21px monospace";
    ctx.fillText("Toi Khong Dong Tinh", btn2X + btnW / 2, btnY + btnH / 2);

    ctx.restore();
}

function handleModalClick(x, y) {
    const boxW = 760;
    const boxH = 340;
    const boxX = (canvas.width - boxW) / 2;
    const boxY = (canvas.height - boxH) / 2;
    const btnW = 290;
    const btnH = 75;
    const btnY = boxY + 165;
    const btn1X = boxX + 55;
    const btn2X = boxX + boxW - 55 - btnW;

    if (y >= btnY && y <= btnY + btnH) {
        if (x >= btn1X && x <= btn1X + btnW) {
            gameState = "MENU";
            playLobbyMusic();
            info.innerText = "Chọn EASY, NORMAL hoặc HARD để bắt đầu!";
        } else if (x >= btn2X && x <= btn2X + btnW) {
            gameState = "MENU";
            playLobbyMusic();
            info.innerText = "Chọn EASY, NORMAL hoặc HARD để bắt đầu!";
        }
    }
}


// ============================================================
// SẢNH CHỜ (LOBBY)
// ============================================================

const menuCards = [
    { id: "EASY", label: "EASY", color: "#00ff70", x: 175, stars: 1, face: "🙂" },
    { id: "NORMAL", label: "NORMAL", color: "#00dfff", x: 495, stars: 2, face: "😠" },
    { id: "HARD", label: "HARD", color: "#d72cff", x: 815, stars: 3, face: "😈" }
];

function handleMenuClick(x, y) {
    if (y >= 360 && y <= 410) {
        for (const card of menuCards) {
            if (x >= card.x + 15 && x <= card.x + 195) {
                selectedDifficulty = card.id;
                resetGame();
                gameState = "PLAYING";
                playMusic();
                info.innerText = "Độ khó: " + card.label + " • Tiến độ: 0%";
                return;
            }
        }
    }
    if (y >= 175 && y <= 420) {
        for (const card of menuCards) {
            if (x >= card.x && x <= card.x + 210) {
                selectedDifficulty = card.id;
                info.innerText = "Đã chọn cấp độ " + card.label + " • Nhấn PLAY để bắt đầu";
                return;
            }
        }
    }
    if (y > 445) {
        resetGame();
        gameState = "PLAYING";
        playMusic();
        info.innerText = "Độ khó: " + selectedDifficulty + " • Tiến độ: 0%";
    }
}

function drawMenuCube(x, y, size, rotation, color) {
    ctx.save();
    ctx.translate(x + size / 2, y + size / 2);
    ctx.rotate(rotation);
    ctx.shadowColor = color;
    ctx.shadowBlur = 18;
    ctx.fillStyle = color;
    ctx.fillRect(-size / 2, -size / 2, size, size);
    ctx.shadowBlur = 0;
    ctx.strokeStyle = "#06152c";
    ctx.lineWidth = 4;
    ctx.strokeRect(-size / 2, -size / 2, size, size);
    ctx.fillStyle = "#06152c";
    ctx.fillRect(-size * .28, -size * .2, size * .18, size * .23);
    ctx.fillRect(size * .1, -size * .2, size * .18, size * .23);
    ctx.fillRect(-size * .25, size * .15, size * .5, size * .12);
    ctx.restore();
}

function drawLobby() {
    if (lobbyBgImg.complete && lobbyBgImg.naturalWidth !== 0) {
        ctx.drawImage(lobbyBgImg, 0, 0, canvas.width, canvas.height);
    } else {
        drawBackground();
    }

    const pulse = 0.75 + Math.sin(performance.now() / 260) * 0.15;

    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = "900 64px monospace";
    ctx.lineJoin = "round";
    ctx.lineWidth = 10;
    ctx.strokeStyle = "#031126";
    ctx.shadowColor = "#00dfff";
    ctx.shadowBlur = 25;
    ctx.strokeText("GEOMETRY DASH", canvas.width / 2, 78);
    ctx.lineWidth = 4;
    ctx.strokeStyle = "#00dfff";
    ctx.strokeText("GEOMETRY DASH", canvas.width / 2, 78);
    ctx.fillStyle = "#e8ffff";
    ctx.fillText("GEOMETRY DASH", canvas.width / 2, 78);
    ctx.shadowBlur = 0;
    ctx.fillStyle = "#00dfff";
    ctx.font = "bold 22px monospace";
    ctx.fillText("— CUSTOM FACE EDITION —", canvas.width / 2, 132);

    ctx.strokeStyle = "#00dfff";
    ctx.lineWidth = 4;
    ctx.shadowColor = "#00dfff";
    ctx.shadowBlur = 15;
    ctx.beginPath(); ctx.arc(48, 48, 27, 0, Math.PI * 2); ctx.stroke();
    ctx.font = "bold 30px Arial"; ctx.fillStyle = "#c8ffff"; ctx.fillText("⚙", 48, 49);
    ctx.beginPath(); ctx.arc(canvas.width - 75, 48, 27, 0, Math.PI * 2); ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.fillStyle = "#00dfff"; ctx.font = "bold 17px monospace"; ctx.textAlign = "left";
    ctx.fillText("BEST:", canvas.width - 40, 35);
    ctx.fillStyle = "#ffffff"; ctx.fillText("0%", canvas.width - 40, 58);

    for (const card of menuCards) {
        const x = card.x, y = 178, w = 210, h = 240;
        const chosen = selectedDifficulty === card.id;
        ctx.save();
        ctx.globalAlpha = chosen ? 1 : 0.78;
        ctx.shadowColor = card.color;
        ctx.shadowBlur = chosen ? 24 * pulse : 12;
        ctx.fillStyle = card.color + "18";
        ctx.strokeStyle = card.color;
        ctx.lineWidth = chosen ? 4 : 3;
        roundRect(ctx, x, y, w, h, 22, true, true);
        ctx.shadowBlur = 0;

        ctx.fillStyle = card.color + "33";
        ctx.strokeStyle = card.color;
        roundRect(ctx, x + 62, y + 22, 86, 82, 13, true, true);
        drawMenuCube(x + 76, y + 35, 58, 0, card.color);
        ctx.textAlign = "center";
        ctx.fillStyle = "#ffffff";
        ctx.font = "900 27px monospace";
        ctx.fillText(card.label, x + w / 2, y + 128);
        ctx.font = "28px Arial";
        for (let i = 0; i < 3; i++) {
            ctx.fillStyle = i < card.stars ? "#ffe34d" : "#123c67";
            ctx.fillText("★", x + 70 + i * 35, y + 160);
        }

        ctx.fillStyle = card.color + "cc";
        ctx.strokeStyle = card.color;
        ctx.lineWidth = 2;
        roundRect(ctx, x + 20, y + 184, 170, 42, 14, true, true);
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 22px monospace";
        ctx.fillText("▶ PLAY", x + w / 2, y + 206);
        if (chosen) {
            ctx.fillStyle = card.color;
            ctx.font = "bold 12px monospace";
            ctx.fillText("SELECTED", x + w / 2, y + 234);
        }
        ctx.restore();
    }

    const groundY = floorY;
    ctx.fillStyle = "rgba(4, 11, 37, 0.4)";
    ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
    ctx.fillStyle = "#d9ffff"; ctx.shadowColor = "#00dfff"; ctx.shadowBlur = 22;
    ctx.fillRect(0, groundY, canvas.width, 4); ctx.shadowBlur = 0;

    for (const o of menuObstacles) {
        if (o.type === "spike") {
            ctx.beginPath(); ctx.moveTo(o.x, groundY); ctx.lineTo(o.x + o.size / 2, groundY - o.size); ctx.lineTo(o.x + o.size, groundY); ctx.closePath();
            ctx.fillStyle = "#071b40"; ctx.strokeStyle = "#00dfff"; ctx.lineWidth = 3; ctx.shadowColor = "#00dfff"; ctx.shadowBlur = 10; ctx.fill(); ctx.stroke(); ctx.shadowBlur = 0;
        } else {
            ctx.fillStyle = "#071b40"; ctx.strokeStyle = "#00dfff"; ctx.lineWidth = 3; ctx.shadowColor = "#00dfff"; ctx.shadowBlur = 10;
            ctx.fillRect(o.x, groundY - o.size, o.size, o.size); ctx.strokeRect(o.x, groundY - o.size, o.size, o.size); ctx.shadowBlur = 0;
        }
    }

    ctx.save(); ctx.lineCap = "round";
    const trailCols = ["#ff3b9d", "#ff8a35", "#ffe84a", "#58ff85", "#43e8ff", "#6875ff", "#d66bff"];
    for (let i = 0; i < trailCols.length; i++) {
        ctx.strokeStyle = trailCols[i]; ctx.globalAlpha = 0.62; ctx.lineWidth = 4;
        ctx.beginPath(); ctx.moveTo(menuCube.x - 100 + i * 2, menuCube.y + 20 + i * 2); ctx.lineTo(menuCube.x + 8, menuCube.y + 22); ctx.stroke();
    }
    ctx.restore();
    drawMenuCube(menuCube.x, menuCube.y, 42, menuCube.rotation, "#28ff68");

    ctx.textAlign = "center";
    ctx.fillStyle = "#d8faff";
    ctx.font = "bold 15px monospace";
    ctx.shadowColor = "#00dfff"; ctx.shadowBlur = 8;
    ctx.fillText("CHỌN CẤP ĐỘ • CLICK PLAY ĐỂ BẮT ĐẦU", canvas.width / 2, 565);
    ctx.shadowBlur = 0;
}

function roundRect(ctx, x, y, w, h, r, fill, stroke) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
    if (fill) ctx.fill();
    if (stroke) ctx.stroke();
}


// ============================================================
// NÚT VỀ SẢNH
// ============================================================

function drawMenuButton() {
    ctx.save();
    ctx.fillStyle = "rgba(3,18,45,0.92)";
    ctx.strokeStyle = "#00eaff"; ctx.lineWidth = 2.5;
    ctx.shadowColor = "#00dfff"; ctx.shadowBlur = 12;
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(18,16,127,44,10); else ctx.rect(18,16,127,44);
    ctx.fill(); ctx.stroke(); ctx.shadowBlur = 0;
    ctx.fillStyle = "#eaffff"; ctx.font = "bold 17px Arial";
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText("⌂ MENU",81.5,38); ctx.restore();
}


// ============================================================
// DRAW
// ============================================================

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (gameState === "MODAL_QUESTION") {
        drawModalQuestion();
        return;
    }

    if (gameState === "MENU") {
        drawLobby();
        return;
    }

    drawBackground();
    drawMenuButton();

    const floorLineColor = selectedDifficulty === "NORMAL" ? "#ff8a35" : (selectedDifficulty === "HARD" ? "#28f5ff" : "#e5fbff");
    ctx.fillStyle = floorLineColor;
    ctx.shadowColor = floorLineColor;
    ctx.shadowBlur = 18;
    ctx.fillRect(0, floorY, canvas.width, 4);
    ctx.shadowBlur = 0;

    const floorGrad = ctx.createLinearGradient(0, floorY, 0, canvas.height);
    if (selectedDifficulty === "NORMAL") {
        floorGrad.addColorStop(0, "#43130e");
        floorGrad.addColorStop(1, "#100506");
    } else if (selectedDifficulty === "HARD") {
        floorGrad.addColorStop(0, "#171044");
        floorGrad.addColorStop(1, "#050414");
    } else {
        floorGrad.addColorStop(0, "#10163d");
        floorGrad.addColorStop(1, "#050817");
    }
    ctx.fillStyle = floorGrad;
    ctx.fillRect(0, floorY + 4, canvas.width, canvas.height - floorY);

    let progressRatio = Math.min(1, distance / LEVEL_LENGTH);
    ctx.fillStyle = "rgba(255,255,255,0.2)";
    const barWidth = Math.min(560, canvas.width * 0.48);
    const barX = (canvas.width - barWidth) / 2;
    ctx.fillRect(barX, 20, barWidth, 14);
    ctx.fillStyle = "#00ffcc";
    ctx.fillRect(barX, 20, barWidth * progressRatio, 14);

    const finishTargetX = canvas.width * 0.62;
    const finishX = (gameState === "WINNING" || gameState === "VICTORY")
        ? finishTargetX
        : LEVEL_LENGTH - distance + player.x;
    const shouldShowFinish =
        gameState === "WINNING" || gameState === "VICTORY" ||
        (finishX > -120 && finishX < canvas.width + 120);

    if (shouldShowFinish) {
        const gateW = 100;
        const gateH = 205;
        const gateTop = floorY - gateH;
        const pulse = 0.82 + 0.18 * Math.sin(performance.now() / 105);
        ctx.save();
        ctx.globalAlpha = pulse;

        const halo = ctx.createRadialGradient(finishX, gateTop + gateH * 0.52, 8, finishX, gateTop + gateH * 0.52, 180);
        halo.addColorStop(0, "rgba(0,255,255,0.45)");
        halo.addColorStop(0.45, "rgba(0,170,255,0.20)");
        halo.addColorStop(1, "rgba(0,120,255,0)");
        ctx.fillStyle = halo;
        ctx.fillRect(finishX - 185, gateTop - 45, 370, gateH + 90);

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

    for (let obs of activeObstacles) {
        let currentX = obs.x - distance + player.x;

        if (currentX + obs.width > -50 && currentX < canvas.width + 50) {
            if (obs.type === "spike") {
                const spikeColor = selectedDifficulty === "NORMAL" ? "#ff6a1a" : (selectedDifficulty === "HARD" ? "#ff39df" : "#ff245f");
                ctx.fillStyle = spikeColor;
                ctx.shadowColor = spikeColor;
                ctx.shadowBlur = 16;
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
                const isPillar = obs.type === "pillar";
                const isBar = obs.type === "bar";
                const obstacleY = floorY - obs.height;
                const blockColor = (Math.floor(obs.x / 300) % 2 === 0) ? "#18c8ff" : "#ff4fd8";
                const obstacleColor = isPillar ? "#18c8ff" : (isBar ? "#ff4fd8" : blockColor);
                const edgeColor = isPillar ? "#b9f4ff" : (isBar ? "#ffd1f5" : (blockColor === "#18c8ff" ? "#b9f4ff" : "#ffd1f5"));

                ctx.save();
                ctx.shadowColor = obstacleColor;
                ctx.shadowBlur = 18;
                const blockGradient = ctx.createLinearGradient(currentX, obstacleY, currentX + obs.width, obstacleY + obs.height);
                blockGradient.addColorStop(0, edgeColor);
                blockGradient.addColorStop(0.28, obstacleColor);
                blockGradient.addColorStop(1, blockColor === "#18c8ff" ? "#0754d8" : "#b20d91");
                ctx.fillStyle = blockGradient;
                ctx.fillRect(currentX, obstacleY, obs.width, obs.height);

                ctx.shadowBlur = 8;
                ctx.strokeStyle = edgeColor;
                ctx.lineWidth = 2.5;
                ctx.strokeRect(currentX + 1, obstacleY + 1, obs.width - 2, obs.height - 2);
                ctx.shadowBlur = 0;
                ctx.fillStyle = "rgba(255,255,255,0.42)";
                ctx.fillRect(currentX + 5, obstacleY + 5, Math.max(3, obs.width - 10), 3);
                ctx.fillStyle = "rgba(255,255,255,0.18)";
                ctx.fillRect(currentX + 5, obstacleY + 11, 3, Math.max(4, obs.height - 16));
                if (obs.width >= 30 && obs.height >= 30) {
                    ctx.strokeStyle = "rgba(255,255,255,0.45)";
                    ctx.lineWidth = 1;
                    ctx.strokeRect(currentX + 7, obstacleY + 7, obs.width - 14, obs.height - 14);
                }
                if (isBar) {
                    ctx.fillStyle = obstacleColor;
                    ctx.shadowColor = obstacleColor;
                    ctx.shadowBlur = 14;
                    ctx.fillRect(currentX - 5, obstacleY - 4, 8, obs.height + 8);
                    ctx.fillRect(currentX + obs.width - 3, obstacleY - 4, 8, obs.height + 8);
                }
                ctx.restore();
            }
        }
    }

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

    if (gameState !== "DYING" && gameState !== "GAMEOVER" && gameState !== "VICTORY") {
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
    }

    if (gameState === "START") {
        ctx.fillStyle = "rgba(0,0,0,0.7)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "#00f0ff";
        ctx.font = "bold 28px Arial";
        ctx.textAlign = "center";
        ctx.fillText("FACE DASH - POP STAR EDITION", canvas.width / 2, canvas.height / 2 - 35);

        ctx.font = "18px Arial";
        ctx.fillStyle = "#ffffff";
        ctx.fillText("Nhấn SPACE hoặc Click chuột để bắt đầu!", canvas.width / 2, canvas.height / 2 + 25);
    }

    if (gameState === "GAMEOVER") {
        ctx.fillStyle = "rgba(0,0,0,0.75)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "#ff0055";
        ctx.font = "bold 54px Arial";
        ctx.textAlign = "center";
        ctx.shadowColor = "#ff0055";
        ctx.shadowBlur = 15;
        ctx.fillText("GAME OVER", canvas.width / 2, 90);
        ctx.shadowBlur = 0;

        if (trollImg.complete) {
            let trollSize = 220;
            ctx.drawImage(trollImg, canvas.width / 2 - trollSize / 2, canvas.height * 0.25, trollSize, trollSize);
        }

        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 18px Arial";
        ctx.fillText("💀 Bạn đã chết!", canvas.width / 2, canvas.height * 0.78);

        ctx.font = "16px Arial";
        ctx.fillText("Nhấn SPACE hoặc Click để chơi lại", canvas.width / 2, canvas.height * 0.86);
    }

    if (gameState === "VICTORY") {
        const t = performance.now() - winStarted;
        const gx = canvas.width * 0.62;
        const gateTop = floorY - 205;
        const gy = gateTop + 112;
        const pulse = 0.82 + 0.18 * Math.sin(t / 95);
        const burstFade = Math.max(0, 1 - t / 1900);

        ctx.fillStyle = `rgba(2, 7, 25, ${Math.max(0, 0.22 - t / 7000)})`;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const halo = ctx.createRadialGradient(gx, gy, 4, gx, gy, 210);
        halo.addColorStop(0, `rgba(210,255,255,${0.75 * pulse})`);
        halo.addColorStop(0.18, `rgba(0,245,255,${0.50 * pulse})`);
        halo.addColorStop(0.55, `rgba(0,125,255,${0.24 * pulse})`);
        halo.addColorStop(1, "rgba(0,80,255,0)");
        ctx.fillStyle = halo;
        ctx.fillRect(gx - 220, gateTop - 40, 440, 300);

        for (let i = 0; i < 3; i++) {
            const radius = 48 + ((t * 0.16 + i * 58) % 150);
            ctx.beginPath();
            ctx.ellipse(gx, gy, radius * 0.88, radius, 0, 0, Math.PI * 2);
            ctx.strokeStyle = i === 0 ? "#dfffff" : "#18dfff";
            ctx.globalAlpha = Math.max(0, (1 - ((radius - 48) / 150))) * burstFade;
            ctx.lineWidth = i === 0 ? 3 : 2;
            ctx.shadowColor = "#00eaff";
            ctx.shadowBlur = 18;
            ctx.stroke();
        }
        ctx.globalAlpha = 1;
        ctx.shadowBlur = 0;

        ctx.save();
        ctx.globalAlpha = burstFade * (0.72 + 0.28 * Math.sin(t / 42));
        for (let i = 0; i < 30; i++) {
            const a = (Math.PI * 2 * i / 30) + 0.08;
            const inner = 24 + (i % 4) * 7;
            const outer = Math.max(canvas.width, canvas.height) * (0.48 + (i % 5) * 0.11);
            const spread = 0.008 + (i % 3) * 0.009;
            ctx.beginPath();
            ctx.moveTo(gx + Math.cos(a) * inner, gy + Math.sin(a) * inner);
            ctx.lineTo(gx + Math.cos(a - spread) * outer, gy + Math.sin(a - spread) * outer);
            ctx.lineTo(gx + Math.cos(a + spread) * outer, gy + Math.sin(a + spread) * outer);
            ctx.closePath();
            ctx.fillStyle = i % 4 === 0 ? "#ffffff" : (i % 4 === 1 ? "#00eaff" : "#fff176");
            ctx.shadowColor = ctx.fillStyle;
            ctx.shadowBlur = 14;
            ctx.fill();
        }
        ctx.restore();
        ctx.globalAlpha = 1;
        ctx.shadowBlur = 0;

        const coreAlpha = Math.max(0, 0.95 - t / 1050);
        const core = ctx.createRadialGradient(gx, gy, 1, gx, gy, 92);
        core.addColorStop(0, `rgba(255,255,255,${coreAlpha})`);
        core.addColorStop(0.2, `rgba(210,255,255,${coreAlpha * 0.88})`);
        core.addColorStop(0.52, `rgba(0,235,255,${coreAlpha * 0.45})`);
        core.addColorStop(1, "rgba(0,180,255,0)");
        ctx.fillStyle = core;
        ctx.fillRect(gx - 100, gy - 100, 200, 200);

        const trailColors = ["#ff3b9d", "#ff8a35", "#ffe84a", "#58ff85", "#43e8ff", "#6875ff", "#d66bff"];
        ctx.save();
        ctx.lineCap = "round";
        for (let i = 0; i < trailColors.length; i++) {
            const offset = (i - 3) * 4;
            ctx.beginPath();
            ctx.moveTo(-25, floorY - 62 + offset);
            ctx.bezierCurveTo(canvas.width * 0.13, floorY - 155 + offset,
                              canvas.width * 0.24, floorY - 190 + offset,
                              gx - 28, gy + 5 + offset * 0.35);
            ctx.strokeStyle = trailColors[i];
            ctx.globalAlpha = Math.max(0, 0.78 - t / 3500);
            ctx.lineWidth = i === 3 ? 7 : 5;
            ctx.shadowColor = trailColors[i];
            ctx.shadowBlur = 15;
            ctx.stroke();
        }
        ctx.restore();
        ctx.globalAlpha = 1;
        ctx.shadowBlur = 0;

        ctx.save();
        for (const p of victoryTrail) {
            ctx.globalAlpha = Math.max(0, p.life) * Math.max(0, 1 - t / 4200);
            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 12;
            ctx.fillRect(p.x, p.y, p.size, p.size);
        }
        ctx.restore();

        ctx.save();
        for (const p of victoryBurst) {
            ctx.globalAlpha = Math.max(0, p.life);
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rotation);
            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 13;
            ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);
            ctx.setTransform(1, 0, 0, 1, 0, 0);
        }
        ctx.restore();

        ctx.save();
        for (const p of winParticles) {
            ctx.globalAlpha = p.alpha * (0.55 + 0.45 * Math.sin(t / 140 + p.rotation));
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rotation);
            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 9;
            ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);
            ctx.setTransform(1, 0, 0, 1, 0, 0);
        }
        ctx.restore();
        ctx.globalAlpha = 1;
        ctx.shadowBlur = 0;

        ctx.save();
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        const titleSize = Math.min(55, canvas.width * 0.049);
        const titleY = canvas.height * 0.30;
        ctx.font = `900 ${titleSize}px monospace`;
        ctx.lineJoin = "round";
        ctx.lineWidth = 10;
        ctx.strokeStyle = "#06131b";
        ctx.shadowColor = "#8cff36";
        ctx.shadowBlur = 18;
        ctx.strokeText("LEVEL COMPLETE!", canvas.width * 0.5, titleY);
        ctx.lineWidth = 5;
        ctx.strokeStyle = "#3c9e18";
        ctx.strokeText("LEVEL COMPLETE!", canvas.width * 0.5, titleY);
        ctx.fillStyle = "#83ff35";
        ctx.fillText("LEVEL COMPLETE!", canvas.width * 0.5, titleY);
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = "#e8ffc7";
        ctx.strokeText("LEVEL COMPLETE!", canvas.width * 0.5, titleY);
        ctx.restore();

        ctx.textAlign = "center";
        ctx.fillStyle = "#e8faff";
        ctx.font = `bold ${Math.min(18, canvas.width * 0.015)}px monospace`;
        ctx.shadowColor = "#00dfff";
        ctx.shadowBlur = 7;
        ctx.fillText("100%  •  Nhấn SPACE hoặc Click để chơi lại", canvas.width * 0.5, canvas.height * 0.91);
        ctx.shadowBlur = 0;
    }

    if (gameState !== "MENU" && gameState !== "MODAL_QUESTION") drawMenuButton();
}


// ============================================================
// GAME LOOP
// ============================================================

function gameLoop(now) {
    if (!lastFrameTime) lastFrameTime = now;
    frameScale = Math.min(2, Math.max(0.35, (now - lastFrameTime) / 16.6667));
    lastFrameTime = now;
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

# Thay placeholder nhạc sảnh TRƯỚC nhạc chơi game vì tên placeholder
# LOBBY_MUSIC_URL_HERE có chứa chuỗi MUSIC_URL_HERE.
game_html = game_html.replace("LOBBY_MUSIC_URL_HERE", lobby_music_url)
game_html = game_html.replace("MUSIC_URL_HERE", music_url)
game_html = game_html.replace("DEATH_SOUND_HERE", death_url)
game_html = game_html.replace("VICTORY_SOUND_HERE", victory_url)
game_html = game_html.replace("TROLL_FACE_HERE", troll_url)
game_html = game_html.replace("PLAYER_IMAGE_HERE", player_url)
game_html = game_html.replace("LOBBY_BG_HERE", lobby_bg_url)


# ============================================================
# CHẠY GAME
# ============================================================

components.html(
    game_html,
    height=760
)
