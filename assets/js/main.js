/* =========================================================
   Premiere Research Institute — interactions
   ========================================================= */
(function () {
  "use strict";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- footer year ---------- */
  var yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();

  /* ---------- header scroll state ---------- */
  var header = document.getElementById("siteHeader");
  function onScroll() {
    if (!header) return;
    header.classList.toggle("scrolled", window.scrollY > 24);
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---------- mobile nav ---------- */
  var toggle = document.getElementById("navToggle");
  var nav = document.getElementById("primaryNav");
  function closeNav() {
    if (!nav) return;
    nav.classList.remove("open");
    toggle.classList.remove("active");
    toggle.setAttribute("aria-expanded", "false");
    document.body.classList.remove("nav-open");
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.classList.toggle("active", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.classList.toggle("nav-open", open);
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) closeNav();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeNav();
    });
  }

  /* ---------- reveal on scroll ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if (reduceMotion || !("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("in"); });
  } else {
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          ro.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    reveals.forEach(function (el) { ro.observe(el); });
  }

  /* ---------- count-up stats ---------- */
  function animateCount(el) {
    var target = parseFloat(el.getAttribute("data-count")) || 0;
    var prefix = el.getAttribute("data-prefix") || "";
    var suffix = el.getAttribute("data-suffix") || "";
    if (reduceMotion || target === 0) {
      el.textContent = prefix + target + suffix;
      return;
    }
    var dur = 1500, start = null;
    function ease(t) { return 1 - Math.pow(1 - t, 3); }
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      el.textContent = prefix + Math.round(ease(p) * target) + suffix;
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = prefix + target + suffix;
    }
    requestAnimationFrame(step);
  }
  var counters = document.querySelectorAll("[data-count]");
  if (!("IntersectionObserver" in window)) {
    counters.forEach(animateCount);
  } else {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          co.unobserve(entry.target);
        }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { co.observe(el); });
  }

  /* ---------- FAQ single-open accordion ---------- */
  var faqItems = document.querySelectorAll(".faq-item");
  faqItems.forEach(function (item) {
    item.addEventListener("toggle", function () {
      if (item.open) {
        faqItems.forEach(function (other) {
          if (other !== item) other.open = false;
        });
      }
    });
  });

  /* ---------- form handling ---------- */
  function validateForm(form) {
    var ok = true;
    form.querySelectorAll("[required]").forEach(function (input) {
      var val = (input.value || "").trim();
      var bad = !val || (input.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val));
      input.classList.toggle("invalid", bad);
      if (bad && ok) { input.focus(); ok = false; }
    });
    return ok;
  }
  function clearInvalidOnInput(form) {
    form.addEventListener("input", function (e) {
      if (e.target.classList) e.target.classList.remove("invalid");
    });
  }

  // Overlay-style forms (enroll + invite)
  [["enrollForm", "efSuccess"], ["inviteForm", "ivSuccess"]].forEach(function (pair) {
    var form = document.getElementById(pair[0]);
    var success = document.getElementById(pair[1]);
    if (!form) return;
    clearInvalidOnInput(form);
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validateForm(form)) return;
      if (success) success.hidden = false;
      /* NOTE: no backend wired yet — connect to email/CRM (e.g. FormSubmit)
         here by POSTing new FormData(form) before showing success. */
    });
  });

  // Inline-success form (newsletter)
  var newsForm = document.getElementById("newsForm");
  if (newsForm) {
    clearInvalidOnInput(newsForm);
    newsForm.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validateForm(newsForm)) return;
      var msg = document.getElementById("nlSuccess");
      var btn = newsForm.querySelector("button[type=submit]");
      if (msg) msg.hidden = false;
      newsForm.querySelectorAll("input").forEach(function (i) { i.value = ""; i.disabled = true; });
      if (btn) { btn.disabled = true; btn.textContent = "Subscribed"; }
    });
  }

  /* ---------- hero neural network ---------- */
  var canvas = document.getElementById("neuralCanvas");
  if (canvas && canvas.getContext) {
    var ctx = canvas.getContext("2d");
    var nodes = [];
    var W = 0, H = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);
    var pointer = { x: -9999, y: -9999, active: false };
    var raf = null, visible = true;

    function size() {
      var rect = canvas.getBoundingClientRect();
      W = rect.width; H = rect.height;
      canvas.width = Math.floor(W * dpr);
      canvas.height = Math.floor(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      buildNodes();
    }

    function buildNodes() {
      var area = W * H;
      var count = Math.max(26, Math.min(80, Math.round(area / 15000)));
      nodes = [];
      for (var i = 0; i < count; i++) {
        nodes.push({
          x: Math.random() * W,
          y: Math.random() * H,
          vx: (Math.random() - 0.5) * 0.28,
          vy: (Math.random() - 0.5) * 0.28,
          r: Math.random() * 1.6 + 0.9
        });
      }
    }

    var LINK = 140, LINK2 = LINK * LINK;
    function draw() {
      ctx.clearRect(0, 0, W, H);
      // links
      for (var i = 0; i < nodes.length; i++) {
        var a = nodes[i];
        for (var j = i + 1; j < nodes.length; j++) {
          var b = nodes[j];
          var dx = a.x - b.x, dy = a.y - b.y;
          var d2 = dx * dx + dy * dy;
          if (d2 < LINK2) {
            var alpha = (1 - d2 / LINK2) * 0.5;
            ctx.strokeStyle = "rgba(120,200,235," + alpha.toFixed(3) + ")";
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
        // link to pointer
        if (pointer.active) {
          var pdx = a.x - pointer.x, pdy = a.y - pointer.y;
          var pd2 = pdx * pdx + pdy * pdy;
          var PR = 180, PR2 = PR * PR;
          if (pd2 < PR2) {
            var pa = (1 - pd2 / PR2) * 0.7;
            ctx.strokeStyle = "rgba(47,215,224," + pa.toFixed(3) + ")";
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(pointer.x, pointer.y);
            ctx.stroke();
          }
        }
      }
      // nodes
      for (var k = 0; k < nodes.length; k++) {
        var n = nodes[k];
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(180,230,245,0.85)";
        ctx.fill();
      }
    }

    function tickPositions() {
      for (var i = 0; i < nodes.length; i++) {
        var n = nodes[i];
        n.x += n.vx; n.y += n.vy;
        if (n.x < -20) n.x = W + 20; else if (n.x > W + 20) n.x = -20;
        if (n.y < -20) n.y = H + 20; else if (n.y > H + 20) n.y = -20;
      }
    }

    function loop() {
      tickPositions();
      draw();
      raf = requestAnimationFrame(loop);
    }

    function stop() { if (raf) { cancelAnimationFrame(raf); raf = null; } }
    function start() { if (!raf && visible) loop(); }

    canvas.addEventListener("pointermove", function (e) {
      var rect = canvas.getBoundingClientRect();
      pointer.x = e.clientX - rect.left;
      pointer.y = e.clientY - rect.top;
      pointer.active = true;
    });
    canvas.addEventListener("pointerleave", function () { pointer.active = false; });

    document.addEventListener("visibilitychange", function () {
      visible = !document.hidden;
      if (visible) start(); else stop();
    });

    var resizeT;
    window.addEventListener("resize", function () {
      clearTimeout(resizeT);
      resizeT = setTimeout(size, 200);
    });

    size();
    if (reduceMotion) {
      draw(); // single static frame
    } else {
      // stop the loop once the hero scrolls out of view (perf)
      if ("IntersectionObserver" in window) {
        var hero = canvas.closest(".hero");
        if (hero) {
          new IntersectionObserver(function (entries) {
            visible = entries[0].isIntersecting && !document.hidden;
            if (visible) start(); else stop();
          }, { threshold: 0 }).observe(hero);
        }
      }
      start();
    }
  }

  /* ---------- 3D particle brain (Who We Are) ---------- */
  var brainC = document.getElementById("brainCanvas");
  if (brainC && brainC.getContext) {
    var bx = brainC.getContext("2d");
    var BW = 0, BH = 0, bdpr = Math.min(window.devicePixelRatio || 1, 2);
    var bPts = [], bEdges = [];
    var TEAL = [88, 226, 233], VIOLET = [126, 112, 255];
    var bPtr = { x: 0, y: 0, tx: 0, ty: 0 };
    var bRaf = null, bOn = true, bT = 0;

    // deterministic PRNG so the model is identical on every load
    var bSeed = 1337;
    function bRnd() {
      bSeed |= 0; bSeed = bSeed + 0x6D2B79F5 | 0;
      var t = Math.imul(bSeed ^ bSeed >>> 15, 1 | bSeed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    }

    function buildBrain() {
      bPts = []; bEdges = [];
      var N = 820;
      for (var i = 0; i < N; i++) {
        var u = bRnd() * 2 - 1, th = bRnd() * Math.PI * 2;
        var s = Math.sqrt(Math.max(0, 1 - u * u));
        var x = s * Math.cos(th), y = u, z = s * Math.sin(th);
        var kind = bRnd(), p;
        if (kind < 0.15) {
          // cerebellum — tucked low at the back
          p = { x: -0.78 + x * 0.40, y: -0.46 + y * 0.28, z: z * 0.55 };
        } else if (kind < 0.19) {
          // brainstem
          p = { x: -0.44 + x * 0.14, y: -0.68 + y * 0.24, z: z * 0.14 };
        } else {
          // cerebrum
          var px = x * 1.30, py = y * 0.94, pz = z * 1.04;
          // cortical folds — gyri/sulci texture
          var d = 1 + 0.06 * Math.sin(6.5 * px + 1.7) * Math.sin(8.3 * py) * Math.sin(7.1 * pz + 0.6);
          px *= d; py *= d; pz *= d;
          if (px > 0.62) py *= 0.90;                       // frontal taper
          if (py < -0.5) py = -0.5 - (Math.abs(py) - 0.5) * 0.3; // flat underside
          if (py > -0.05 && Math.abs(pz) < 0.09)           // longitudinal fissure
            pz = (pz < 0 ? -1 : 1) * (0.09 + 0.02 * bRnd());
          p = { x: px, y: py + 0.10, z: pz };
        }
        bPts.push(p);
      }
      // synaptic edges between near neighbours
      for (var a = 0; a < bPts.length; a++) {
        var links = 0;
        for (var b = a + 1; b < bPts.length && links < 3; b++) {
          var dx = bPts[a].x - bPts[b].x, dy = bPts[a].y - bPts[b].y, dz = bPts[a].z - bPts[b].z;
          if (dx * dx + dy * dy + dz * dz < 0.05) { bEdges.push([a, b]); links++; }
        }
      }
    }

    function bSize() {
      var r = brainC.getBoundingClientRect();
      BW = r.width; BH = r.height;
      brainC.width = Math.max(1, Math.floor(BW * bdpr));
      brainC.height = Math.max(1, Math.floor(BH * bdpr));
      bx.setTransform(bdpr, 0, 0, bdpr, 0, 0);
    }

    function bCol(t, alpha) {
      var r = Math.round(TEAL[0] + (VIOLET[0] - TEAL[0]) * t);
      var g = Math.round(TEAL[1] + (VIOLET[1] - TEAL[1]) * t);
      var b2 = Math.round(TEAL[2] + (VIOLET[2] - TEAL[2]) * t);
      return "rgba(" + r + "," + g + "," + b2 + "," + alpha.toFixed(3) + ")";
    }

    function bDraw() {
      bT += 0.0038;
      // eased pointer for a weighty, expensive feel
      bPtr.x += (bPtr.tx - bPtr.x) * 0.06;
      bPtr.y += (bPtr.ty - bPtr.y) * 0.06;
      var rotY = bT + bPtr.x * 0.55, rotX = -0.14 + bPtr.y * 0.35;
      var cosY = Math.cos(rotY), sinY = Math.sin(rotY);
      var cosX = Math.cos(rotX), sinX = Math.sin(rotX);
      var S = Math.min(BW, BH) * 0.315, CX = BW / 2, CY = BH / 2 + Math.sin(bT * 1.6) * 5;
      bx.clearRect(0, 0, BW, BH);
      var proj = new Array(bPts.length);
      for (var i = 0; i < bPts.length; i++) {
        var p = bPts[i];
        var x1 = p.x * cosY - p.z * sinY, z1 = p.x * sinY + p.z * cosY;
        var y1 = p.y * cosX - z1 * sinX, z2 = p.y * sinX + z1 * cosX;
        var f = 2.9 / (2.9 - z2);
        proj[i] = { x: CX + x1 * S * f, y: CY - y1 * S * f, z: z2, f: f };
      }
      bx.lineWidth = 1;
      for (var e = 0; e < bEdges.length; e++) {
        var A = proj[bEdges[e][0]], B = proj[bEdges[e][1]];
        var zt = ((A.z + B.z) / 2 + 1.5) / 3;
        bx.strokeStyle = bCol(1 - zt, 0.05 + zt * 0.17);
        bx.beginPath(); bx.moveTo(A.x, A.y); bx.lineTo(B.x, B.y); bx.stroke();
      }
      for (var j = 0; j < bPts.length; j++) {
        var P = proj[j];
        var zt2 = (P.z + 1.5) / 3;
        bx.fillStyle = bCol(1 - zt2, 0.30 + zt2 * 0.65);
        bx.beginPath(); bx.arc(P.x, P.y, (0.7 + zt2 * 1.6) * P.f, 0, Math.PI * 2); bx.fill();
      }
    }

    function bLoop() { bDraw(); bRaf = requestAnimationFrame(bLoop); }
    function bStop() { if (bRaf) { cancelAnimationFrame(bRaf); bRaf = null; } }
    function bStart() { if (!bRaf && bOn) bLoop(); }

    var bCard = brainC.closest(".orb-card") || brainC;
    bCard.addEventListener("pointermove", function (e) {
      var r = bCard.getBoundingClientRect();
      bPtr.tx = ((e.clientX - r.left) / r.width - 0.5) * 1.7;
      bPtr.ty = ((e.clientY - r.top) / r.height - 0.5) * 1.2;
    });
    bCard.addEventListener("pointerleave", function () { bPtr.tx = 0; bPtr.ty = 0; });

    var bResizeT;
    window.addEventListener("resize", function () {
      clearTimeout(bResizeT); bResizeT = setTimeout(function () { bSize(); }, 200);
    });

    bSize(); buildBrain();
    if (reduceMotion) {
      bT = 0.9; bDraw();          // elegant static three-quarter view
    } else {
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (en) {
          bOn = en[0].isIntersecting && !document.hidden;
          if (bOn) bStart(); else bStop();
        }, { threshold: 0 }).observe(bCard);
      }
      document.addEventListener("visibilitychange", function () {
        bOn = !document.hidden; if (bOn) bStart(); else bStop();
      });
      bStart();
    }
  }

})();
