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
})();
