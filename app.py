import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Geometry Dash - Custom Level",
    layout="centered"
)

st.title("🟨 Geometry Dash - Custom Level")
st.caption("SPACE / ↑ / CLICK để nhảy • R để chơi lại")

gd_game_code = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
    html, body {
        margin: 0;
        padding: 0;
        background: #080b18;
        display: flex;
        justify-content: center;
        align-items: center;
        font-family: Arial, sans-serif;
    }

    canvas {
        border: 3px solid #00eaff;
        box-shadow: 0 0 25px #00eaff;
        cursor: pointer;
        background: #15183b;
    }
</style>
</head>

<body>

<canvas id="game" width="900" height="500"></canvas>

<script>

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");


// =========================
// GAME SETTINGS
// =========================

const WIDTH = canvas.width;
const HEIGHT = canvas.height;

const FLOOR = 400;

let cameraX = 0;
let gameSpeed = 6;

let score = 0;
let attempts = 1;

let gameOver = false;
let gameWon = false;


// =========================
// PLAYER
// =========================

const player = {

    x: 160,
    y: FLOOR - 42,

    size: 42,

    velocityY: 0,

    gravity: 0.72,
    jumpPower: -14,

    grounded: false,

    rotation: 0,

    color: "#00ffcc"
};


// =========================
// FIXED LEVEL
// =========================
//
// Không spawn ngẫu nhiên nữa.
// Map được thiết kế cố định.
// =========================

const level = [

    // ---- START ----

    {type:"spike", x:700, y:FLOOR, w:42, h:42},

    {type:"spike", x:900, y:FLOOR, w:42, h:42},
    {type:"spike", x:942, y:FLOOR, w:42, h:42},

    {type:"spike", x:1200, y:FLOOR, w:42, h:42},

    // ---- BLOCK ----

    {type:"block", x:1450, y:FLOOR-42, w:42, h:42},
    {type:"spike", x:1530, y:FLOOR, w:42, h:42},

    {type:"block", x:1650, y:FLOOR-42, w:42, h:42},
    {type:"block", x:1692, y:FLOOR-42, w:42, h:42},

    {type:"spike", x:1810, y:FLOOR, w:42, h:42},

    // ---- DOUBLE SPIKE ----

    {type:"spike", x:2050, y:FLOOR, w:42, h:42},
    {type:"spike", x:2092, y:FLOOR, w:42, h:42},

    // ---- STAIRS ----

    {type:"block", x:2300, y:FLOOR-42, w:42, h:42},
    {type:"block", x:2342, y:FLOOR-84, w:42, h:84},

    {type:"block", x:2384, y:FLOOR-126, w:42, h:126},

    {type:"spike", x:2470, y:FLOOR-42, w:42, h:42},

    // ---- LOW SECTION ----

    {type:"block", x:2700, y:FLOOR-42, w:42, h:42},
    {type:"block", x:2742, y:FLOOR-42, w:42, h:42},

    {type:"spike", x:2870, y:FLOOR, w:42, h:42},

    // ---- BIG JUMP ----

    {type:"spike", x:3150, y:FLOOR, w:42, h:42},
    {type:"spike", x:3192, y:FLOOR, w:42, h:42},

    {type:"spike", x:3400, y:FLOOR, w:42, h:42},

    // ---- PLATFORM ----

    {type:"block", x:3650, y:FLOOR-42, w:42, h:42},
    {type:"block", x:3692, y:FLOOR-42, w:42, h:42},
    {type:"block", x:3734, y:FLOOR-42, w:42, h:42},

    {type:"spike", x:3830, y:FLOOR, w:42, h:42},

    // ---- FINAL SECTION ----

    {type:"spike", x:4100, y:FLOOR, w:42, h:42},
    {type:"spike", x:4142, y:FLOOR, w:42, h:42},

    {type:"block", x:4350, y:FLOOR-42, w:42, h:42},

    {type:"spike", x:4480, y:FLOOR, w:42, h:42},

    {type:"spike", x:4650, y:FLOOR, w:42, h:42},
    {type:"spike", x:4692, y:FLOOR, w:42, h:42},

    {type:"finish", x:5000, y:0, w:20, h:FLOOR}

];


// =========================
// INPUT
// =========================

function jump() {

    if (gameOver || gameWon) {

        restart();

        return;
    }

    if (player.grounded) {

        player.velocityY = player.jumpPower;

        player.grounded = false;

    }

}


window.addEventListener("keydown", function(e) {

    if (
        e.code === "Space" ||
        e.code === "ArrowUp"
    ) {

        e.preventDefault();

        jump();

    }

    if (e.code === "KeyR") {

        restart();

    }

});


canvas.addEventListener("mousedown", jump);


// =========================
// RESTART
// =========================

function restart() {

    player.x = 160;
    player.y = FLOOR - player.size;

    player.velocityY = 0;

    player.rotation = 0;

    player.grounded = true;

    cameraX = 0;

    score = 0;

    gameOver = false;
    gameWon = false;

    attempts++;

}


// =========================
// COLLISION
// =========================

function collision(a, b) {

    return (

        a.x < b.x + b.w &&
        a.x + a.size > b.x &&

        a.y < b.y + b.h &&
        a.y + a.size > b.y

    );

}


// =========================
// UPDATE
// =========================

function update() {

    if (gameOver || gameWon)
        return;


    // Player movement

    player.velocityY += player.gravity;

    player.y += player.velocityY;


    // Ground

    if (player.y + player.size >= FLOOR) {

        player.y = FLOOR - player.size;

        player.velocityY = 0;

        player.grounded = true;

        player.rotation =
            Math.round(player.rotation / 90) * 90;

    }

    else {

        player.grounded = false;

        player.rotation += 8;

    }


    // Camera

    cameraX += gameSpeed;


    // Collision with objects

    for (const obj of level) {

        const screenX = obj.x - cameraX + 160;


        if (obj.type === "spike") {

            const hitbox = {

                x: screenX + 6,

                y: obj.y - obj.h + 8,

                w: obj.w - 12,

                h: obj.h - 8

            };


            if (collision(player, hitbox)) {

                gameOver = true;

            }

        }


        if (obj.type === "block") {

            const block = {

                x: screenX,

                y: obj.y,

                w: obj.w,

                h: obj.h

            };


            if (collision(player, block)) {

                // Landing on top

                if (
                    player.velocityY >= 0 &&
                    player.y + player.size <= block.y + 15
                ) {

                    player.y = block.y - player.size;

                    player.velocityY = 0;

                    player.grounded = true;

                }

                else {

                    gameOver = true;

                }

            }

        }


        if (obj.type === "finish") {

            if (screenX < player.x + player.size) {

                gameWon = true;

            }

        }

    }


    score = Math.floor(cameraX / 10);

}


// =========================
// DRAW BACKGROUND
// =========================

function drawBackground() {

    // Gradient sky

    const gradient =
        ctx.createLinearGradient(0, 0, 0, HEIGHT);

    gradient.addColorStop(0, "#17154b");
    gradient.addColorStop(1, "#29245c");

    ctx.fillStyle = gradient;

    ctx.fillRect(0, 0, WIDTH, HEIGHT);


    // Background mountains

    ctx.fillStyle = "#202052";

    for (let i = -500; i < 3000; i += 220) {

        let x = i - (cameraX * 0.25) % 220;

        ctx.beginPath();

        ctx.moveTo(x, FLOOR);

        ctx.lineTo(x + 110, 220);

        ctx.lineTo(x + 220, FLOOR);

        ctx.closePath();

        ctx.fill();

    }


    // Background grid

    ctx.strokeStyle = "rgba(0,240,255,0.08)";

    ctx.lineWidth = 1;

    for (let x = 0; x < WIDTH; x += 45) {

        ctx.beginPath();

        ctx.moveTo(x, 0);

        ctx.lineTo(x, FLOOR);

        ctx.stroke();

    }

    for (let y = 40; y < FLOOR; y += 45) {

        ctx.beginPath();

        ctx.moveTo(0, y);

        ctx.lineTo(WIDTH, y);

        ctx.stroke();

    }

}


// =========================
// DRAW FLOOR
// =========================

function drawFloor() {

    ctx.fillStyle = "#08091a";

    ctx.fillRect(
        0,
        FLOOR,
        WIDTH,
        HEIGHT - FLOOR
    );


    ctx.fillStyle = "#00eaff";

    ctx.fillRect(
        0,
        FLOOR,
        WIDTH,
        5
    );


    // Moving floor pattern

    ctx.strokeStyle = "rgba(0,240,255,0.25)";

    for (
        let x = -(cameraX % 50);
        x < WIDTH;
        x += 50
    ) {

        ctx.beginPath();

        ctx.moveTo(x, FLOOR + 5);

        ctx.lineTo(x - 25, HEIGHT);

        ctx.stroke();

    }

}


// =========================
// DRAW LEVEL
// =========================

function drawLevel() {

    for (const obj of level) {

        const x =
            obj.x - cameraX + 160;


        if (
            x < -100 ||
            x > WIDTH + 100
        )
            continue;


        // SPIKE

        if (obj.type === "spike") {

            ctx.fillStyle = "#ff145c";

            ctx.strokeStyle = "#ffffff";

            ctx.lineWidth = 2;

            ctx.beginPath();

            ctx.moveTo(
                x,
                obj.y
            );

            ctx.lineTo(
                x + obj.w / 2,
                obj.y - obj.h
            );

            ctx.lineTo(
                x + obj.w,
                obj.y
            );

            ctx.closePath();

            ctx.fill();

            ctx.stroke();

        }


        // BLOCK

        if (obj.type === "block") {

            ctx.fillStyle = "#3a36a3";

            ctx.fillRect(
                x,
                obj.y,
                obj.w,
                obj.h
            );


            ctx.strokeStyle = "#00eaff";

            ctx.lineWidth = 2;

            ctx.strokeRect(
                x,
                obj.y,
                obj.w,
                obj.h
            );


            // Inner square

            ctx.strokeStyle =
                "rgba(255,255,255,0.3)";

            ctx.strokeRect(
                x + 7,
                obj.y + 7,
                obj.w - 14,
                obj.h - 14
            );

        }


        // FINISH

        if (obj.type === "finish") {

            ctx.fillStyle = "#00ff88";

            ctx.fillRect(
                x,
                100,
                8,
                FLOOR - 100
            );

        }

    }

}


// =========================
// DRAW PLAYER
// =========================

function drawPlayer() {

    ctx.save();


    ctx.translate(
        player.x + player.size / 2,
        player.y + player.size / 2
    );


    ctx.rotate(
        player.rotation *
        Math.PI / 180
    );


    // Glow

    ctx.shadowBlur = 15;

    ctx.shadowColor = "#00ffcc";


    // Cube

    ctx.fillStyle =
        player.color;

    ctx.fillRect(
        -player.size / 2,
        -player.size / 2,
        player.size,
        player.size
    );


    ctx.shadowBlur = 0;


    // Border

    ctx.strokeStyle =
        "#ffffff";

    ctx.lineWidth = 3;

    ctx.strokeRect(
        -player.size / 2,
        -player.size / 2,
        player.size,
        player.size
    );


    // Eyes

    ctx.fillStyle = "#071016";

    ctx.fillRect(
        -12,
        -10,
        8,
        8
    );

    ctx.fillRect(
        5,
        -10,
        8,
        8
    );


    // Mouth

    ctx.fillRect(
        -10,
        7,
        20,
        5
    );


    ctx.restore();

}


// =========================
// HUD
// =========================

function drawHUD() {

    ctx.fillStyle = "#ffffff";

    ctx.font =
        "bold 20px Arial";

    ctx.fillText(
        "ATTEMPT " + attempts,
        20,
        30
    );


    ctx.fillText(
        "SCORE " + score,
        20,
        58
    );


    // Progress bar

    const progress =
        Math.min(
            cameraX / 4850,
            1
        );


    ctx.fillStyle =
        "rgba(255,255,255,0.2)";

    ctx.fillRect(
        200,
        20,
        500,
        10
    );


    ctx.fillStyle =
        "#00ffcc";

    ctx.fillRect(
        200,
        20,
        500 * progress,
        10
    );

}


// =========================
// GAME OVER
// =========================

function drawGameOver() {

    if (!gameOver && !gameWon)
        return;


    ctx.fillStyle =
        "rgba(0,0,0,0.72)";

    ctx.fillRect(
        0,
        0,
        WIDTH,
        HEIGHT
    );


    ctx.textAlign =
        "center";


    if (gameWon) {

        ctx.fillStyle =
            "#00ff88";

        ctx.font =
            "bold 55px Arial";

        ctx.fillText(
            "LEVEL COMPLETE!",
            WIDTH / 2,
            220
        );

        ctx.font =
            "22px Arial";

        ctx.fillStyle =
            "#ffffff";

        ctx.fillText(
            "Bạn đã hoàn thành màn chơi!",
            WIDTH / 2,
            265
        );

        ctx.fillText(
            "CLICK hoặc SPACE để chơi lại",
            WIDTH / 2,
            310
        );

    }

    else {

        ctx.fillStyle =
            "#ff145c";

        ctx.font =
            "bold 55px Arial";

        ctx.fillText(
            "ATTEMPT FAILED!",
            WIDTH / 2,
            220
        );


        ctx.fillStyle =
            "#ffffff";

        ctx.font =
            "22px Arial";

        ctx.fillText(
            "Score: " + score,
            WIDTH / 2,
            265
        );

        ctx.fillText(
            "CLICK / SPACE để thử lại",
            WIDTH / 2,
            310
        );

    }


    ctx.textAlign =
        "left";

}


// =========================
// MAIN LOOP
// =========================

function draw() {

    ctx.clearRect(
        0,
        0,
        WIDTH,
        HEIGHT
    );


    drawBackground();

    drawFloor();

    drawLevel();

    drawPlayer();

    drawHUD();

    drawGameOver();

}


function gameLoop() {

    update();

    draw();

    requestAnimationFrame(
        gameLoop
    );

}


player.grounded = true;

gameLoop();

</script>

</body>
</html>
"""

components.html(
    gd_game_code,
    height=530,
    scrolling=False
)
