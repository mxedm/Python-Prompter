// Simple prompter client: handles load, scroll, flip, font size, and fit-to-screen
const socket = io();
const container = document.getElementById("container");
const content = document.getElementById("content");
let paragraphs = [];
let position = 0; // px scrolled
let speed = 0; // px/sec
let lastTs = null;
let rafId = null;
let currentFontSize = 48;
let flipX = 1;
let flipY = 1;

socket.on("connect", () => {
  socket.emit("join", {});
});

socket.on("control_event", (data) => {
  const t = data.type;
  if (t === "load") {
    paragraphs = data.paragraphs || [];
    renderParagraphs();
    position = 0;
    applyPosition();
    // If the control requested autoscale on load, run fit-to-screen
    if (data.autoscale) {
      // small timeout to allow layout to settle
      setTimeout(() => fitToScreen(), 50);
    }
  } else if (t === "scroll") {
    speed = Number(data.speed) || 0;
    if (speed > 0) startLoop();
    else stopLoop();
  } else if (t === "set_font") {
    document.body.style.fontFamily = `${data.font}, Verdana, Arial, sans-serif`;
  } else if (t === "set_uppercase") {
    content.style.textTransform = data.enabled ? "uppercase" : "none";
  } else if (t === "jump") {
    position += Number(data.pixels) || 0;
    applyPosition();
  } else if (t === "set_position") {
    position = Number(data.pos) || 0;
    applyPosition();
  } else if (t === "flip") {
    flipX = data.x ? -1 : 1;
    flipY = data.y ? -1 : 1;
    applyPosition();
  } else if (t === "set_font_size") {
    currentFontSize = Number(data.size) || currentFontSize;
    applyFontSize();
  } else if (t === "fit_to_screen") {
    fitToScreen();
  }
});

function renderParagraphs() {
  content.innerHTML = "";
  for (const p of paragraphs) {
    const el = document.createElement("div");
    el.className = "paragraph";
    el.textContent = p.text;
    content.appendChild(el);
  }
  applyFontSize();
}

function applyFontSize() {
  const nodes = content.querySelectorAll(".paragraph");
  nodes.forEach((n) => (n.style.fontSize = currentFontSize + "px"));
}

function applyPosition() {
  // Apply transforms in correct order:
  // 1. First flip (scale) from the center
  // 2. Then translate for scrolling
  container.style.transform = `scaleX(${flipX}) scaleY(${flipY})`;
  content.style.transform = `translateY(${-position}px)`;
}

function step(ts) {
  if (!lastTs) lastTs = ts;
  const dt = (ts - lastTs) / 1000; // sec
  lastTs = ts;
  position += speed * dt;
  // clamp
  const max = Math.max(0, content.scrollHeight - container.clientHeight);
  if (position > max) {
    position = max;
    stopLoop();
  }
  if (position < 0) position = 0;
  applyPosition();
  rafId = requestAnimationFrame(step);
}

function startLoop() {
  if (!rafId) rafId = requestAnimationFrame(step);
}

function stopLoop() {
  if (rafId) cancelAnimationFrame(rafId);
  rafId = null;
  lastTs = null;
}

function fitToScreen() {
  // Reduce font size until content fits vertically
  let fs = currentFontSize;
  const min = 8;
  applyFontSize();
  while (content.scrollHeight > container.clientHeight && fs > min) {
    fs -= 1;
    currentFontSize = fs;
    applyFontSize();
  }
}
