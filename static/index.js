document.addEventListener("DOMContentLoaded", () => {
  // Theme toggle
  const themeToggle = document.getElementById("themeToggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      document.body.classList.toggle("dark");
      themeToggle.textContent = document.body.classList.contains("dark")
        ? "☀️"
        : "🌙";
    });
  }

  // Menu toggle
  const menuToggle = document.getElementById("menuToggle");
  const sidebar = document.getElementById("sidebar");
  const closeSidebar = document.querySelector(".close-sidebar");
  if (menuToggle && sidebar) {
    menuToggle.addEventListener("click", () => {
      sidebar.classList.toggle("active");
      menuToggle.classList.toggle("active");
    });
  }
  if (closeSidebar && sidebar) {
    closeSidebar.addEventListener("click", () => {
      sidebar.classList.remove("active");
      menuToggle.classList.remove("active");
    });
  }

  // Wire up sidebar buttons
  document.querySelectorAll(".options button").forEach((btn) => {
    btn.addEventListener("click", () => {
      const chartLoader = document.getElementById("chartLoader");
      const chartImg = document.getElementById("chartImg");
      chartLoader.classList.add("active");
      chartImg.classList.remove("loaded");
      fetchPlot(btn.dataset.type);
      // Close menu on mobile after selection
      if (sidebar.classList.contains("active")) {
        sidebar.classList.remove("active");
        menuToggle.classList.remove("active");
      }
    });
  });

  // Download chart
  const downloadChart = document.getElementById("downloadChart");
  if (downloadChart) {
    downloadChart.addEventListener("click", () => {
      const chartImg = document.getElementById("chartImg");
      if (chartImg.src) {
        const link = document.createElement("a");
        link.href = chartImg.src;
        link.download = "ev_chart.png";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    });
  }

  // Full view toggle
  const fullViewChart = document.getElementById("fullViewChart");
  if (fullViewChart) {
    fullViewChart.addEventListener("click", () => {
      const chartCard = document.querySelector(".chart-card");
      chartCard.classList.toggle("full-view");
      fullViewChart.textContent = chartCard.classList.contains("full-view")
        ? "↙️"
        : "⛶";
    });
  }

  // VIN lookup
  const getEvBtn = document.getElementById("getEvBtn");
  const vinMessage = document.getElementById("vinMessage");
  if (getEvBtn) {
    getEvBtn.addEventListener("click", async () => {
      const vin = document.getElementById("vinInput").value.trim();
      if (!vin) {
        vinMessage.textContent = "Please enter a VIN.";
        vinMessage.classList.add("error", "show");
        setTimeout(() => vinMessage.classList.remove("show"), 3000);
        return;
      }
      getEvBtn.classList.add("loading");
      getEvBtn.disabled = true;
      vinMessage.classList.remove("show", "success", "error");
      try {
        const { record } = await fetchEv(vin);
        const table = document.getElementById("evTable");
        table.innerHTML = "";
        // header
        const hdr = document.createElement("tr");
        Object.keys(record).forEach((k) => {
          const th = document.createElement("th");
          th.textContent = k
            .replace(/_/g, " ")
            .replace(/\b\w/g, (c) => c.toUpperCase());
          hdr.appendChild(th);
        });
        table.appendChild(hdr);
        // data
        const row = document.createElement("tr");
        Object.values(record).forEach((v) => {
          const td = document.createElement("td");
          td.textContent = v || "N/A";
          row.appendChild(td);
        });
        table.appendChild(row);
        table.classList.add("show");
        vinMessage.textContent = "Vehicle data loaded successfully!";
        vinMessage.classList.add("success", "show");
        setTimeout(() => vinMessage.classList.remove("show"), 3000);
      } catch {
        vinMessage.textContent = "Vehicle not found.";
        vinMessage.classList.add("error", "show");
        setTimeout(() => vinMessage.classList.remove("show"), 3000);
      } finally {
        getEvBtn.classList.remove("loading");
        getEvBtn.disabled = false;
      }
    });
  }
});

// Fetch and display a plot
async function fetchPlot(type) {
  const chartLoader = document.getElementById("chartLoader");
  const chartImg = document.getElementById("chartImg");
  try {
    const res = await fetch(`/plot?type=${type}`);
    const { img } = await res.json();
    chartImg.src = `data:image/png;base64,${img}`;
    chartImg.classList.add("loaded");
  } finally {
    chartLoader.classList.remove("active");
  }
}

// Fetch and display a single EV record
async function fetchEv(vin) {
  const res = await fetch(`/ev?vin=${vin}`);
  if (!res.ok) throw new Error("Not found");
  return res.json();
}
