
import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path

st.set_page_config(page_title="Geometry Dash Custom Face", layout="wide")

ASSETS = {
    "MUSIC_URL_HERE": ("pop_star.mp3", "audio/mpeg"),
    "DEATH_SOUND_HERE": ("vine-boom.mp3", "audio/mpeg"),
    "VICTORY_SOUND_HERE": ("final-fantasy-vii-victory-fanfare-1.mp3", "audio/mpeg"),
    "PLAYER_IMAGE_HERE": ("player.png", "image/png"),
    "TROLL_FACE_HERE": ("trollface.png", "image/png"),
}

st.markdown("""
<style>
.stApp {background:#03091f;color:white}
header[data-testid="stHeader"] {background:#03091f}
.block-container {padding-top:1rem;max-width:1500px}
</style>
""", unsafe_allow_html=True)

st.title("GEOMETRY DASH — CUSTOM FACE EDITION")
st.caption("Chọn cấp độ trong sảnh chờ, sau đó nhấn PLAY. Dùng SPACE, mũi tên lên hoặc click để nhảy.")

game_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#03091f;color:white;font-family:Arial,sans-serif;overflow:hidden}
#wrap{width:100%;max-width:1400px;margin:auto}
canvas{width:100%;height:auto;display:block;border:2px solid #00dfff;border-radius:8px;box-shadow:0 0 24px #00bfff55;touch-action:manipulation}
#info{text-align:center;font-size:17px;font-weight:bold;padding:10px;color:#eafaff}
</style>
</head>
<body>
<div id="wrap">
<canvas id="game" width="1200" height="650"></canvas>
<div id="info">Chọn cấp độ rồi nhấn PLAY</div>
</div>
<audio id="music" src="MUSIC_URL_HERE" loop></audio>
<audio id="death" src="DEATH_SOUND_HERE"></audio>
<audio id="victory" src="VICTORY_SOUND_HERE"></audio>
<script>
const canvas=document.getElementById("game"),ctx=canvas.getContext("2d");
const info=document.getElementById("info");
const music=document.getElementById("music"),deathSound=document.getElementById("death"),victorySound=document.getElementById("victory");
const playerImg=new Image();playerImg.src="PLAYER_IMAGE_HERE";
const trollImg=new Image();trollImg.src="TROLL_FACE_HERE";

const W=canvas.width,H=canvas.height,FLOOR=535;
const difficulties={
 EASY:{speed:5.2,gap:360,jump:-14.2,gravity:.72,label:"EASY"},
 NORMAL:{speed:6.7,gap:300,jump:-14.7,gravity:.78,label:"NORMAL"},
 HARD:{speed:8.1,gap:255,jump:-15.1,gravity:.82,label:"HARD"}
};
let selected="NORMAL",state="MENU",progress=0,distance=0;
let speed=6.7,gravity=.78,jumpPower=-14.7;
let obstacles=[],particles=[],burst=[],trail=[];
let menuCube={x:90,y:FLOOR-44,vy:0,rot:0,ground:true,nextJump:0};
let menuDistance=0,menuLast=0,menuObs=[];
let player={x:180,y:FLOOR-48,size:48,vy:0,rot:0,ground:true};
let gateX=0,finishStart=0,finishPhase=0,finishX=0,finishY=0;
let deathStart=0,shake=0,startedAt=0;

function rand(a,b){return a+Math.random()*(b-a)}
function choice(a){return a[Math.floor(Math.random()*a.length)]}
function audioPlay(a){try{a.currentTime=0;a.play().catch(()=>{})}catch(e){}}
function stopAudio(a){a.pause();a.currentTime=0}
function stopAllAudio(){stopAudio(music);stopAudio(victorySound)}

function background(t,offset=0){
 const g=ctx.createLinearGradient(0,0,0,H);
 g.addColorStop(0,"#02071d");g.addColorStop(.55,"#071744");g.addColorStop(1,"#020617");
 ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
 for(let i=0;i<90;i++){
  let x=(i*149-offset*(.025+(i%4)*.012)+W*4)%W;
  let y=(i*83)%390;
  ctx.globalAlpha=.25+.65*Math.abs(Math.sin(t/700+i));
  ctx.fillStyle=i%5===0?"#00eaff":"#dcefff";
  ctx.fillRect(x,y,i%7===0?3:2,i%7===0?3:2);
 }
 ctx.globalAlpha=1;
 // Núi hình học xanh đen
 for(let layer=0;layer<2;layer++){
  ctx.beginPath();ctx.moveTo(0,FLOOR);
  let step=layer?72:95,base=layer?405:365;
  for(let x=-step;x<W+step;x+=step){
   let xx=x-(offset*(layer?.14:.08))%step;
   ctx.lineTo(xx,base-((Math.floor((x+step)/step)%2===0)?70:0));
  }
  ctx.lineTo(W,FLOOR);ctx.closePath();
  ctx.fillStyle=layer?"#07102e":"#0b1c50";ctx.fill();
 }
 // Thành phố neon
 for(let i=0;i<31;i++){
  let bw=18+(i%3)*8,bh=25+(i*31%90);
  let x=(i*43-offset*.35+5000)%(W+40)-20;
  ctx.fillStyle="#040b25";ctx.fillRect(x,FLOOR-bh,bw,bh);
  ctx.fillStyle=i%2?"#ff35ce":"#00dfff";
  ctx.shadowColor=ctx.fillStyle;ctx.shadowBlur=7;
  for(let y=FLOOR-bh+8;y<FLOOR-4;y+=14){
   ctx.fillRect(x+4,y,4,5);
   if(bw>23)ctx.fillRect(x+13,y,4,5);
  }
  ctx.shadowBlur=0;
 }
 ctx.fillStyle="#020718";ctx.fillRect(0,FLOOR,W,H-FLOOR);
 ctx.fillStyle="#dffcff";ctx.shadowColor="#00eaff";ctx.shadowBlur=17;
 ctx.fillRect(0,FLOOR,W,4);ctx.shadowBlur=0;
}

function drawCube(x,y,size,rot,skin=true){
 ctx.save();ctx.translate(x+size/2,y+size/2);ctx.rotate(rot);
 ctx.shadowColor="#00f5ff";ctx.shadowBlur=15;
 if(skin&&playerImg.complete&&playerImg.naturalWidth){
  ctx.drawImage(playerImg,-size/2,-size/2,size,size);
 }else{
  ctx.fillStyle="#00edff";ctx.fillRect(-size/2,-size/2,size,size);
  ctx.strokeStyle="#baffff";ctx.lineWidth=3;ctx.strokeRect(-size/2,-size/2,size,size);
  ctx.fillStyle="#031126";ctx.fillRect(-size*.28,-size*.2,size*.17,size*.2);
  ctx.fillRect(size*.1,-size*.2,size*.17,size*.2);
  ctx.fillRect(-size*.25,size*.15,size*.5,size*.1);
 }
 ctx.restore();ctx.shadowBlur=0;
}

function drawSpike(x,y,size=35){
 ctx.save();ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+size/2,y-size);ctx.lineTo(x+size,y);ctx.closePath();
 ctx.fillStyle="#081638";ctx.strokeStyle="#00dfff";ctx.lineWidth=3;
 ctx.shadowColor="#00cfff";ctx.shadowBlur=10;ctx.fill();ctx.stroke();ctx.restore();
}
function drawBlock(x,y,w=48,h=48){
 ctx.save();ctx.fillStyle="#0b1e4a";ctx.strokeStyle="#00eaff";ctx.lineWidth=3;
 ctx.shadowColor="#00dfff";ctx.shadowBlur=10;ctx.fillRect(x,y-h,w,h);ctx.strokeRect(x,y-h,w,h);ctx.restore();
}
function addBurst(x,y,count=120){
 const colors=["#fff176","#ffe95b","#ffffff","#00eaff","#f8fdff"];
 for(let i=0;i<count;i++){
  let a=rand(0,Math.PI*2),v=rand(2,9);
  burst.push({x,y,vx:Math.cos(a)*v,vy:Math.sin(a)*v,size:rand(3,9),life:1,rot:rand(0,6),spin:rand(-.2,.2),color:choice(colors)});
 }
}
function drawGate(x,active=false,t=0){
 const top=FLOOR-220,w=84,h=220;
 ctx.save();
 const pulse=active?1+.2*Math.sin(t/65):1;
 ctx.shadowColor="#00eaff";ctx.shadowBlur=active?38:22;
 ctx.lineWidth=active?9:8;ctx.strokeStyle="#00eaff";
 ctx.beginPath();ctx.moveTo(x, FLOOR);ctx.lineTo(x,top+40);
 ctx.quadraticCurveTo(x,top,x+w/2,top);ctx.quadraticCurveTo(x+w,top,x+w,top+40);
 ctx.lineTo(x+w,FLOOR);ctx.stroke();
 const gr=ctx.createLinearGradient(x,top,x+w,FLOOR);
 gr.addColorStop(0,"rgba(0,180,255,.4)");gr.addColorStop(.5,"rgba(80,245,255,.13)");gr.addColorStop(1,"rgba(0,130,255,.45)");
 ctx.fillStyle=gr;ctx.fillRect(x+7,top+40,w-14,h-40);
 ctx.beginPath();ctx.ellipse(x+w/2,top+h*.56,24,78,0,0,Math.PI*2);
 ctx.strokeStyle="#dfffff";ctx.lineWidth=2.5;ctx.stroke();
 if(active){
  const glow=ctx.createRadialGradient(x+w/2,top+120,1,x+w/2,top+120,130*pulse);
  glow.addColorStop(0,"rgba(255,255,255,.9)");glow.addColorStop(.35,"rgba(0,240,255,.4)");glow.addColorStop(1,"rgba(0,100,255,0)");
  ctx.fillStyle=glow;ctx.fillRect(x-90,top-20,w+180,h+40);
 }
 ctx.restore();
 ctx.fillStyle="#8efaff";ctx.font="bold 26px Arial";ctx.textAlign="center";
 ctx.shadowColor="#00eaff";ctx.shadowBlur=12;ctx.fillText("FINISH",x+w/2,top-17);ctx.shadowBlur=0;
}

function drawTrail(x,y,t){
 const colors=["#ff3b9d","#ff8a35","#ffe84a","#58ff85","#43e8ff","#6875ff","#d66bff"];
 ctx.save();ctx.lineCap="round";
 for(let i=0;i<colors.length;i++){
  ctx.beginPath();ctx.moveTo(-20,FLOOR-60+(i-3)*4);
  ctx.bezierCurveTo(W*.13,FLOOR-145+(i-3)*4,W*.24,FLOOR-190+(i-3)*4,x-20,y+20);
  ctx.strokeStyle=colors[i];ctx.globalAlpha=Math.max(0,.82-t/3500);ctx.lineWidth=i===3?7:5;
  ctx.shadowColor=colors[i];ctx.shadowBlur=14;ctx.stroke();
 }
 ctx.restore();ctx.globalAlpha=1;ctx.shadowBlur=0;
}

function drawVictory(t){
 const gx=W*.62,top=FLOOR-220,gy=top+120;
 ctx.fillStyle=`rgba(2,7,25,${Math.max(0,.25-t/6500)})`;ctx.fillRect(0,0,W,H);
 const halo=ctx.createRadialGradient(gx,gy,2,gx,gy,220);
 halo.addColorStop(0,"rgba(220,255,255,.75)");halo.addColorStop(.25,"rgba(0,235,255,.48)");halo.addColorStop(1,"rgba(0,100,255,0)");
 ctx.fillStyle=halo;ctx.fillRect(gx-230,top-30,460,300);
 for(let i=0;i<3;i++){
  let r=45+((t*.16+i*60)%155);
  ctx.beginPath();ctx.ellipse(gx,gy,r*.85,r,0,0,Math.PI*2);
  ctx.strokeStyle=i===0?"#ffffff":"#00dfff";ctx.globalAlpha=Math.max(0,1-(r-45)/155);
  ctx.lineWidth=2;ctx.stroke();
 }
 ctx.globalAlpha=1;
 drawGate(gx-42,true,t);
 drawTrail(gx,gy,t);
 for(const p of burst){
  ctx.save();ctx.globalAlpha=Math.max(0,p.life);ctx.translate(p.x,p.y);ctx.rotate(p.rot);
  ctx.fillStyle=p.color;ctx.shadowColor=p.color;ctx.shadowBlur=12;
  ctx.fillRect(-p.size/2,-p.size/2,p.size,p.size);ctx.restore();
 }
 for(const p of particles){
  ctx.save();ctx.globalAlpha=Math.max(0,p.life);ctx.fillStyle=p.color;ctx.shadowColor=p.color;ctx.shadowBlur=8;
  ctx.fillRect(p.x,p.y,p.size,p.size);ctx.restore();
 }
 ctx.save();ctx.textAlign="center";ctx.textBaseline="middle";
 const fs=52;ctx.font=`900 ${fs}px monospace`;ctx.lineJoin="round";
 ctx.lineWidth=10;ctx.strokeStyle="#06131b";ctx.shadowColor="#8cff36";ctx.shadowBlur=18;
 ctx.strokeText("LEVEL COMPLETE!",W/2,195);
 ctx.lineWidth=5;ctx.strokeStyle="#3c9e18";ctx.strokeText("LEVEL COMPLETE!",W/2,195);
 ctx.fillStyle="#83ff35";ctx.fillText("LEVEL COMPLETE!",W/2,195);
 ctx.lineWidth=1.5;ctx.strokeStyle="#e8ffc7";ctx.strokeText("LEVEL COMPLETE!",W/2,195);
 ctx.restore();
 ctx.textAlign="center";ctx.font="bold 18px monospace";ctx.fillStyle="#e8faff";
 ctx.fillText("100%  •  Nhấn SPACE hoặc Click để chơi lại",W/2,H-28);
}

function drawMenu(t){
 background(t,menuDistance);
 // Tiêu đề
 ctx.textAlign="center";ctx.font="900 72px monospace";
 ctx.lineJoin="round";ctx.lineWidth=12;ctx.strokeStyle="#00214d";
 ctx.shadowColor="#00dfff";ctx.shadowBlur=22;ctx.strokeText("GEOMETRY DASH",W/2,100);
 ctx.lineWidth=5;ctx.strokeStyle="#00dfff";ctx.strokeText("GEOMETRY DASH",W/2,100);
 ctx.fillStyle="#b7fbff";ctx.fillText("GEOMETRY DASH",W/2,100);ctx.shadowBlur=0;
 ctx.font="bold 25px monospace";ctx.fillStyle="#00eaff";
 ctx.fillText("— CUSTOM FACE EDITION —",W/2,145);
 // Thẻ cấp độ
 const cards=[
  {id:"EASY",x:190,color:"#00ff70",stars:"★☆☆",face:"☺"},
  {id:"NORMAL",x:455,color:"#00cfff",stars:"★★☆",face:"◉"},
  {id:"HARD",x:720,color:"#d900ff",stars:"★★★",face:"⌁"}
 ];
 for(const c of cards){
  let chosen=selected===c.id;
  ctx.save();ctx.shadowColor=c.color;ctx.shadowBlur=chosen?25:12;
  ctx.fillStyle=chosen?"rgba(0,100,140,.25)":"rgba(5,12,45,.8)";
  ctx.strokeStyle=c.color;ctx.lineWidth=chosen?5:3;
  roundRect(c.x,185,230,245,22);ctx.fill();ctx.stroke();ctx.shadowBlur=0;
  // Cube icon
  ctx.fillStyle=c.color;ctx.strokeStyle="#020b20";ctx.lineWidth=5;
  roundRect(c.x+70,210,90,85,12);ctx.fill();ctx.stroke();
  ctx.fillStyle="#031126";ctx.fillRect(c.x+88,232,15,18);ctx.fillRect(c.x+128,232,15,18);
  ctx.fillRect(c.x+91,265,52,8);
  ctx.fillStyle="#ffffff";ctx.font="bold 28px monospace";ctx.fillText(c.id,c.x+115,326);
  ctx.fillStyle="#ffd94a";ctx.font="28px Arial";ctx.fillText(c.stars,c.x+115,360);
  ctx.fillStyle=c.color;ctx.shadowColor=c.color;ctx.shadowBlur=14;
  roundRect(c.x+22,380,186,38,13);ctx.fill();ctx.shadowBlur=0;
  ctx.fillStyle="#ffffff";ctx.font="bold 23px monospace";ctx.fillText("▶ PLAY",c.x+115,407);
  ctx.restore();
 }
 // Sảnh có chướng ngại vật
 for(const o of menuObs){
  if(o.type==="spike")drawSpike(o.x,FLOOR,35);
  else drawBlock(o.x,FLOOR,45,45);
 }
 // Vệt cầu vồng và khối tự chạy
 ctx.save();ctx.globalAlpha=.72;drawTrail(menuCube.x,menuCube.y,0);ctx.restore();
 drawCube(menuCube.x,menuCube.y,44,menuCube.rot,false);
 ctx.fillStyle="#e8faff";ctx.font="16px Arial";
 ctx.fillText("Chọn cấp độ và nhấn PLAY",W/2,480);
}

function roundRect(x,y,w,h,r){
 ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);
 ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);
 ctx.arcTo(x,y,x+w,y,r);ctx.closePath();
}

function startGame(){
 state="PLAYING";distance=0;progress=0;obstacles=[];
 particles=[];burst=[];trail=[];
 speed=difficulties[selected].speed;
 gravity=difficulties[selected].gravity;
 jumpPower=difficulties[selected].jump;
 player={x:180,y:FLOOR-48,size:48,vy:0,rot:0,ground:true};
 for(let i=0;i<18;i++){
  let x=480+i*difficulties[selected].gap;
  obstacles.push({x,type:i%4===2?"block":"spike",w:35,h:i%4===2?45:35});
 }
 finishX=4800;finishPhase=0;
 stopAudio(victorySound);audioPlay(music);
 info.innerText="Độ khó: "+selected+" • Tiến độ: 0%";
}
function die(){
 if(state!=="PLAYING")return;
 state="GAMEOVER";deathStart=performance.now();stopAudio(music);audioPlay(deathSound);
 particles=[];
 for(let i=0;i<35;i++){
  let a=rand(0,Math.PI*2),v=rand(2,7);
  particles.push({x:player.x+24,y:player.y+24,vx:Math.cos(a)*v,vy:Math.sin(a)*v,size:rand(3,8),life:1,color:choice(["#ff1744","#ff3d81","#ffffff","#00e5ff","#ff9100"])});
 }
}
function win(){
 if(state!=="PLAYING")return;
 state="VICTORY";finishPhase=2;finishStart=performance.now();
 stopAudio(music);audioPlay(victorySound);addBurst(W*.62,FLOOR-330,145);
 info.innerText="LEVEL COMPLETE!";
}
function jump(){
 if(state==="MENU"){startGame();return}
 if(state==="GAMEOVER"||state==="VICTORY"){startGame();return}
 if(state==="PLAYING"&&player.ground){player.vy=jumpPower;player.ground=false}
}
function hit(a,b){
 return a.x+a.w>b.x&&a.x<b.x+b.w&&a.y+a.h>b.y&&a.y<b.y+b.h;
}
canvas.addEventListener("click",e=>{
 const r=canvas.getBoundingClientRect(),x=(e.clientX-r.left)*W/r.width,y=(e.clientY-r.top)*H/r.height;
 if(state==="MENU"){
  if(y>=185&&y<=435){
   if(x>=190&&x<=420)selected="EASY";
   else if(x>=455&&x<=685)selected="NORMAL";
   else if(x>=720&&x<=950)selected="HARD";
   info.innerText="Đã chọn "+selected+" — nhấn PLAY để bắt đầu";
   return;
  }
  if(y>440){startGame();return}
  return;
 }
 jump();
});
window.addEventListener("keydown",e=>{
 if(e.code==="Space"||e.code==="ArrowUp"){
  e.preventDefault();
  if(state==="MENU"){startGame()}else{jump()}
 }
});
function updateMenu(t){
 menuDistance+=1.8;
 menuCube.x+=2.3;
 if(menuCube.x>W+60)menuCube.x=-50;
 if(menuCube.ground&&t>menuCube.nextJump){
  menuCube.vy=-rand(10,15);menuCube.ground=false;menuCube.nextJump=t+rand(500,1800);
 }
 menuCube.vy+=.48;menuCube.y+=menuCube.vy;
 if(menuCube.y>=FLOOR-44){menuCube.y=FLOOR-44;menuCube.vy=0;menuCube.ground=true}
 if(!menuLast||t-menuLast>rand(650,1150)){
  menuObs.push({x:W+20,type:Math.random()<.25?"block":"spike"});menuLast=t;
 }
 for(const o of menuObs)o.x-=3.1;
 menuObs=menuObs.filter(o=>o.x>-60);
}
function update(){
 const t=performance.now();
 if(state==="MENU"){updateMenu(t);return}
 if(state==="PLAYING"){
  distance+=speed;progress=Math.min(99,Math.floor(distance/finishX*100));
  player.vy+=gravity;player.y+=player.vy;
  if(player.y+player.size>=FLOOR){player.y=FLOOR-player.size;player.vy=0;player.ground=true}
  else player.ground=false;
  if(!player.ground)player.rot+=.13;
  for(const o of obstacles){
   o.x-=speed;
   let box={x:player.x+7,y:player.y+7,w:player.size-14,h:player.size-14};
   let obstacleBox=o.type==="spike"?{x:o.x+8,y:FLOOR-27,w:19,h:27}:{x:o.x,y:FLOOR-o.h,w:o.w||45,h:o.h};
   if(hit(box,obstacleBox)){die();break}
  }
  obstacles=obstacles.filter(o=>o.x>-60);
  if(distance>=finishX){win()}
  info.innerText="Độ khó: "+selected+" • Tiến độ: "+progress+"%";
 }
 if(state==="GAMEOVER"){
  for(const p of particles){p.x+=p.vx;p.y+=p.vy;p.vy+=.15;p.life-=.018}
  particles=particles.filter(p=>p.life>0);
 }
 if(state==="VICTORY"){
  let elapsed=t-finishStart;
  for(const p of burst){p.x+=p.vx;p.y+=p.vy;p.vy+=.045;p.vx*=.99;p.life-=.009;p.rot+=p.spin}
  burst=burst.filter(p=>p.life>0);
  for(const p of particles){p.x+=p.vx;p.y+=p.vy;p.life-=.02}
  particles=particles.filter(p=>p.life>0);
 }
}
function draw(){
 const t=performance.now();
 ctx.clearRect(0,0,W,H);
 background(t,state==="MENU"?menuDistance:distance);
 if(state==="MENU"){drawMenu(t);return}
 if(state==="PLAYING"){
  for(const o of obstacles){
   if(o.type==="spike")drawSpike(o.x,FLOOR,o.h);
   else drawBlock(o.x,FLOOR,o.w||45,o.h);
  }
  if(distance>finishX-500){
   let gx=W*.72;
   drawGate(gx,false,t);
  }
  drawCube(player.x,player.y,player.size,player.rot,true);
 }
 if(state==="GAMEOVER"){
  for(const p of particles){ctx.globalAlpha=p.life;ctx.fillStyle=p.color;ctx.fillRect(p.x,p.y,p.size,p.size)}
  ctx.globalAlpha=1;ctx.fillStyle="rgba(0,0,0,.76)";ctx.fillRect(0,0,W,H);
  ctx.textAlign="center";ctx.fillStyle="#ff1744";ctx.font="bold 58px Arial";
  ctx.shadowColor="#ff1744";ctx.shadowBlur=18;ctx.fillText("GAME OVER",W/2,100);ctx.shadowBlur=0;
  if(trollImg.complete&&trollImg.naturalWidth)ctx.drawImage(trollImg,W/2-105,155,210,210);
  ctx.fillStyle="#ffffff";ctx.font="bold 22px Arial";ctx.fillText("Bạn đã thua!",W/2,410);
  ctx.font="18px Arial";ctx.fillText("Nhấn SPACE hoặc click để chơi lại",W/2,450);
 }
 if(state==="VICTORY")drawVictory(t-finishStart);
}
function loop(){
 update();draw();requestAnimationFrame(loop);
}
loop();
</script>
</body>
</html>
"""

for token, (filename, mime) in ASSETS.items():
    path = Path(filename)
    if not path.exists():
        st.error(f"Thiếu file {filename}. Hãy tải file này lên cùng thư mục với app.py trên GitHub.")
        st.stop()
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    game_html = game_html.replace(token, f"data:{mime};base64,{encoded}")

components.html(game_html, height=790, scrolling=False)
