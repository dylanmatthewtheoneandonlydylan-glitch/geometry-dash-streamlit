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
# 🎵 ĐỌC NHẠC POP STAR
# ============================================================

with open("pop_star.mp3", "rb") as f:
    music_data = base64.b64encode(f.read()).decode()

music_url = f"data:audio/mpeg;base64,{music_data}"


# ============================================================
# 💥 ĐỌC ÂM THANH VINE BOOM
# ============================================================

with open("vine-boom.mp3", "rb") as f:
    death_data = base64.b64encode(f.read()).decode()

death_url = f"data:audio/mpeg;base64,{death_data}"


# ============================================================
# 🎮 GAME HTML
# ============================================================

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

    box-shadow:
        0 0 25px rgba(0, 240, 255, 0.5);

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


<canvas
    id="gameCanvas"
    width="800"
    height="400">
</canvas>


<div id="info">
    Nhấn SPACE để bắt đầu!
</div>


<!-- =====================================================
     🎵 NHẠC NỀN
====================================================== -->

<audio
    id="bgMusic"
    src="MUSIC_URL_HERE"
    loop
    preload="auto">
</audio>


<!-- =====================================================
     💥 ÂM THANH KHI THUA
====================================================== -->

<audio
    id="deathSound"
    src="DEATH_SOUND_HERE"
    preload="auto">
</audio>


<script>


// ========================================================
// CANVAS
// ========================================================

const canvas =
    document.getElementById("gameCanvas");

const ctx =
    canvas.getContext("2d");

const info =
    document.getElementById("info");


// ========================================================
// 🎵 AUDIO
// ========================================================

const bgMusic =
    document.getElementById("bgMusic");

const deathSound =
    document.getElementById("deathSound");


bgMusic.volume = 0.5;

deathSound.volume = 0.8;


// ========================================================
// 🟨 CUSTOM SKIN
// ========================================================

const playerImg =
    new Image();

playerImg.src =
    "https://i.imgur.com/8Q8S4wD.png";


// ========================================================
// 🎮 GAME STATE
// ========================================================

let gameState = "START";

let speed = 6;

let distance = 0;


// ========================================================
// 🟨 PLAYER
// ========================================================

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


// ========================================================
// LEVEL
// ========================================================

const floorY = 330;

const LEVEL_LENGTH = 3500;


// ========================================================
// 🚧 OBSTACLES
// ========================================================

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


// ========================================================
// 🎵 PLAY MUSIC
// ========================================================

function playMusic() {

    bgMusic.currentTime = 0;

    bgMusic.play().catch(function(error) {

        console.log(
            "Không thể tự động phát nhạc:",
            error
        );

    });

}


// ========================================================
// 🛑 STOP MUSIC
// ========================================================

function stopMusic() {

    bgMusic.pause();

    bgMusic.currentTime = 0;

}


// ========================================================
// 💥 PLAY DEATH SOUND
// ========================================================

function playDeathSound() {

    deathSound.currentTime = 0;

    deathSound.play().catch(function(error) {

        console.log(
            "Không thể phát âm thanh:",
            error
        );

    });

}


// ========================================================
// 🦘 JUMP / START
// ========================================================

function jump() {


    // ====================================================
    // START / GAMEOVER / VICTORY
    // ====================================================

    if (

        gameState === "START" ||

        gameState === "GAMEOVER" ||

        gameState === "VICTORY"

    ) {


        resetGame();


        gameState = "PLAYING";


        playMusic();

    }


    // ====================================================
    // JUMP
    // ====================================================

    else if (

        gameState === "PLAYING" &&

        player.isGrounded

    ) {


        player.vy =
            player.jumpPower;


        player.isGrounded =
            false;

    }

}


// ========================================================
// ⌨️ KEYBOARD
// ========================================================

window.addEventListener(
    "keydown",
    function(e) {

        if (

            e.code === "Space" ||

            e.code === "ArrowUp"

        ) {

            e.preventDefault();

            jump();

        }

    }
);


// ========================================================
// 🖱️ MOUSE
// ========================================================

canvas.addEventListener(
    "mousedown",
    function() {

        jump();

    }
);


// ========================================================
// 🔄 RESET GAME
// ========================================================

function resetGame() {


    player.y =
        floorY - player.size;


    player.vy = 0;


    player.rotation = 0;


    player.isGrounded = true;


    distance = 0;


    activeObstacles =
        levelObstacles.map(
            function(obs) {

                return {

                    x: obs.x,

                    width: 35,

                    height: 35,

                    type: obs.type

                };

            }
        );

}


// ========================================================
// ⚙️ UPDATE
// ========================================================

function update() {


    if (
        gameState !== "PLAYING"
    ) {

        return;

    }


    // ====================================================
    // DI CHUYỂN
    // ====================================================

    distance += speed;


    let progress =
        Math.min(
            100,
            Math.floor(
                (distance /
                LEVEL_LENGTH) *
                100
            )
        );


    // ====================================================
    // GRAVITY
    // ====================================================

    player.vy +=
        player.gravity;


    player.y +=
        player.vy;


    // ====================================================
    // CHẠM ĐẤT
    // ====================================================

    if (

        player.y +
        player.size >=
        floorY

    ) {


        player.y =
            floorY -
            player.size;


        player.vy = 0;


        player.isGrounded =
            true;


        player.rotation =
            Math.round(
                player.rotation /
                (Math.PI / 2)
            ) *
            (Math.PI / 2);

    }

    else {

        player.rotation +=
            0.15;

    }


    // ====================================================
    // 💥 KIỂM TRA VA CHẠM
    // ====================================================

    for (
        let obs of activeObstacles
    ) {


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


            // ================================
            // 💥 GAME OVER
            // ================================

            gameState =
                "GAMEOVER";


            // Dừng nhạc Kirby

            stopMusic();


            // Phát Vine Boom

            playDeathSound();


            // Thông báo

            info.innerText =
                "💥 THẤT BẠI! Tiến độ: " +
                progress +
                "% | Nhấn SPACE để chơi lại";


            // Thoát vòng lặp

            break;

        }

    }


    // ====================================================
    // 🏁 VỀ ĐÍCH
    // ====================================================

    if (
        distance >= LEVEL_LENGTH
    ) {


        gameState =
            "VICTORY";


        stopMusic();


        info.innerText =
            "🎉 XUẤT SẮC! BẠN ĐÃ HOÀN THÀNH 100%!";

    }

    else if (
        gameState === "PLAYING"
    ) {


        info.innerText =
            "Tiến độ: " +
            progress +
            "%";

    }

}


// ========================================================
// 🌌 BACKGROUND
// ========================================================

function drawBackground() {


    let grad =
        ctx.createLinearGradient(
            0,
            0,
            0,
            canvas.height
        );


    grad.addColorStop(
        0,
        "#1a0033"
    );


    grad.addColorStop(
        1,
        "#000000"
    );


    ctx.fillStyle =
        grad;


    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    const colors = [

        "#ff0055",

        "#00f0ff",

        "#ffcc00",

        "#00ff66",

        "#cc00ff"

    ];


    for (
        let i = 0;
        i < 16;
        i++
    ) {


        let x =
            i * 55 -
            (distance * 0.2) %
            55;


        ctx.fillStyle =
            colors[
                i %
                colors.length
            ];


        ctx.shadowColor =
            colors[
                i %
                colors.length
            ];


        ctx.shadowBlur = 10;


        ctx.fillRect(
            x,
            0,
            8,
            40 +
            (i % 3) * 25
        );

    }


    ctx.shadowBlur = 0;

}


// ========================================================
// 🎨 DRAW
// ========================================================

function draw() {


    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    // ====================================================
    // BACKGROUND
    // ====================================================

    drawBackground();


    // ====================================================
    // FLOOR
    // ====================================================

    ctx.fillStyle =
        "#00f0ff";


    ctx.shadowColor =
        "#00f0ff";


    ctx.shadowBlur = 12;


    ctx.fillRect(
        0,
        floorY,
        canvas.width,
        4
    );


    ctx.shadowBlur = 0;


    ctx.fillStyle =
        "#0d001a";


    ctx.fillRect(
        0,
        floorY + 4,
        canvas.width,
        canvas.height -
        floorY
    );


    // ====================================================
    // PROGRESS BAR
    // ====================================================

    let progressRatio =
        Math.min(
            1,
            distance /
            LEVEL_LENGTH
        );


    ctx.fillStyle =
        "rgba(255, 255, 255, 0.2)";


    ctx.fillRect(
        200,
        15,
        400,
        10
    );


    ctx.fillStyle =
        "#00ffcc";


    ctx.fillRect(
        200,
        15,
        400 *
        progressRatio,
        10
    );


    // ====================================================
    // 🏁 FINISH
    // ====================================================

    let finishX =
        LEVEL_LENGTH -
        distance +
        player.x;


    if (
        finishX <
        canvas.width + 100
    ) {


        ctx.fillStyle =
            "#00ffcc";


        ctx.shadowColor =
            "#00ffcc";


        ctx.shadowBlur = 15;


        ctx.fillRect(
            finishX,
            floorY - 130,
            15,
            130
        );


        ctx.shadowBlur = 0;


        ctx.fillStyle =
            "#ffffff";


        ctx.font =
            "bold 16px Arial";


        ctx.fillText(
            "FINISH",
            finishX - 15,
            floorY - 140
        );

    }


    // ====================================================
    // 🚧 OBSTACLES
    // ====================================================

    for (
        let obs of activeObstacles
    ) {


        let currentX =
            obs.x -
            distance +
            player.x;


        if (

            currentX > -50 &&

            currentX <
            canvas.width + 50

        ) {


            // ==================================================
            // SPIKE
            // ==================================================

            if (
                obs.type === "spike"
            ) {


                ctx.fillStyle =
                    "#ff0055";


                ctx.shadowColor =
                    "#ff0055";


                ctx.shadowBlur = 10;


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


                ctx.strokeStyle =
                    "#ffffff";


                ctx.lineWidth = 2;


                ctx.stroke();


                ctx.shadowBlur = 0;

            }


            // ==================================================
            // BLOCK
            // ==================================================

            else {


                ctx.fillStyle =
                    "#ff9900";


                ctx.shadowColor =
                    "#ff9900";


                ctx.shadowBlur = 10;


                ctx.fillRect(
                    currentX,
                    floorY -
                    obs.height,
                    obs.width,
                    obs.height
                );


                ctx.strokeStyle =
                    "#ffffff";


                ctx.lineWidth = 2;


                ctx.strokeRect(
                    currentX,
                    floorY -
                    obs.height,
                    obs.width,
                    obs.height
                );


                ctx.shadowBlur = 0;

            }

        }

    }


    // ====================================================
    // 🟨 PLAYER
    // ====================================================

    ctx.save();


    ctx.translate(

        player.x +
        player.size / 2,

        player.y +
        player.size / 2

    );


    ctx.rotate(
        player.rotation
    );


    ctx.strokeStyle =
        "#00f0ff";


    ctx.lineWidth = 3;


    ctx.shadowColor =
        "#00f0ff";


    ctx.shadowBlur = 10;


    ctx.strokeRect(

        -player.size / 2,

        -player.size / 2,

        player.size,

        player.size

    );


    ctx.shadowBlur = 0;


    if (
        playerImg.complete
    ) {


        ctx.drawImage(

            playerImg,

            -player.size / 2,

            -player.size / 2,

            player.size,

            player.size

        );

    }

    else {


        ctx.fillStyle =
            "#00ffcc";


        ctx.fillRect(

            -player.size / 2,

            -player.size / 2,

            player.size,

            player.size

        );

    }


    ctx.restore();


    // ====================================================
    // START SCREEN
    // ====================================================

    if (
        gameState === "START"
    ) {


        ctx.fillStyle =
            "rgba(0, 0, 0, 0.7)";


        ctx.fillRect(

            0,
            0,
            canvas.width,
            canvas.height

        );


        ctx.fillStyle =
            "#00f0ff";


        ctx.font =
            "bold 28px Arial";


        ctx.textAlign =
            "center";


        ctx.fillText(

            "FACE DASH - POP STAR EDITION",

            canvas.width / 2,

            canvas.height / 2 - 20

        );


        ctx.font =
            "18px Arial";


        ctx.fillStyle =
            "#ffffff";


        ctx.fillText(

            "Nhấn SPACE hoặc Click chuột để bắt đầu!",

            canvas.width / 2,

            canvas.height / 2 + 30

        );

    }


    // ====================================================
    // VICTORY SCREEN
    // ====================================================

    if (
        gameState === "VICTORY"
    ) {


        ctx.fillStyle =
            "rgba(0, 0, 0, 0.8)";


        ctx.fillRect(

            0,
            0,
            canvas.width,
            canvas.height

        );


        ctx.fillStyle =
            "#00ffcc";


        ctx.font =
            "bold 36px Arial";


        ctx.textAlign =
            "center";


        ctx.fillText(

            "VICTORY! 100%",

            canvas.width / 2,

            canvas.height / 2 - 20

        );


        ctx.font =
            "20px Arial";


        ctx.fillStyle =
            "#ffffff";


        ctx.fillText(

            "Chúc mừng bạn đã hoàn thành màn chơi!",

            canvas.width / 2,

            canvas.height / 2 + 25

        );

    }


    // ====================================================
    // GAME OVER SCREEN
    // ====================================================

    if (
        gameState === "GAMEOVER"
    ) {


        ctx.fillStyle =
            "rgba(0, 0, 0, 0.65)";


        ctx.fillRect(

            0,
            0,
            canvas.width,
            canvas.height

        );


        ctx.fillStyle =
            "#ff0055";


        ctx.font =
            "bold 38px Arial";


        ctx.textAlign =
            "center";


        ctx.fillText(

            "GAME OVER",

            canvas.width / 2,

            canvas.height / 2 - 20

        );


        ctx.font =
            "18px Arial";


        ctx.fillStyle =
            "#ffffff";


        ctx.fillText(

            "Nhấn SPACE để chơi lại",

            canvas.width / 2,

            canvas.height / 2 + 30

        );

    }

}


// ========================================================
// 🔄 GAME LOOP
// ========================================================

function gameLoop() {

    update();

    draw();

    requestAnimationFrame(
        gameLoop
    );

}


// ========================================================
// ▶️ START
// ========================================================

gameLoop();

</script>

</body>

</html>
"""


# ============================================================
# 🔗 GẮN FILE NHẠC VÀO GAME
# ============================================================

game_html = game_html.replace(
    "MUSIC_URL_HERE",
    music_url
)


game_html = game_html.replace(
    "DEATH_SOUND_HERE",
    death_url
)


# ============================================================
# 🚀 HIỂN THỊ GAME
# ============================================================

components.html(
    game_html,
    height=480
)
