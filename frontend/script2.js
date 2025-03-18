const apiBaseUrl = 'https://khgb.pythonanywhere.com'; // Change if needed

// Login
document.getElementById("loginForm")?.addEventListener("submit", async function (e) {
    e.preventDefault();
    const MaHS = document.getElementById("loginMaHS").value;
    const password = document.getElementById("loginPassword").value;

    const response = await fetch(`${apiBaseUrl}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ MaHS, password }),
    });

    const result = await response.json();
    document.getElementById("loginMessage").innerText = result.message || result.error;

    if (response.ok) {
        localStorage.setItem("MaHS", result.MaHS);
        localStorage.setItem("TenHS", result.TenHS);
        window.location.href = "edit.html";
    }
});

// Register
document.getElementById("registerForm")?.addEventListener("submit", async function (e) {
    e.preventDefault();
    const MaHS = document.getElementById("registerMaHS").value;
    const TenHS = document.getElementById("registerTenHS").value;
    const Lop = document.getElementById("registerLop").value;
    const SoDienThoai = document.getElementById("registerSoDienThoai").value;
    const Email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;

    const response = await fetch(`${apiBaseUrl}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({MaHS, TenHS, Lop, SoDienThoai, Email ,password }),
    });

    const result = await response.json();
    document.getElementById("registerMessage").innerText = result.message || result.error;

    if (response.ok) {
        window.location.href = "login.html";
    }
});

// Edit Info
document.getElementById("editForm")?.addEventListener("submit", async function (e) {
    e.preventDefault();
    const MaHS = localStorage.getItem("MaHS"); // Get stored ID
    if (!MaHS) {
        document.getElementById("editMessage").innerText = "Bạn cần đăng nhập trước!";
        return;
    }
    const TenHS = document.getElementById("editTenHS").value;
    const Lop = document.getElementById("editLop").value;
    const SoDienThoai = document.getElementById("editSoDienThoai").value;
    const Email = document.getElementById("editEmail").value;
    const password = document.getElementById("editPassword").value;

    const payload = { MaHS };
    if (TenHS) payload.TenHS = TenHS;
    if (Lop) payload.Lop = Lop;
    if (SoDienThoai) payload.SoDienThoai = SoDienThoai;
    if (Email) payload.Email = Email
    if (password) payload.password = password;

    const response = await fetch(`${apiBaseUrl}/edit_info`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    const result = await response.json();
    document.getElementById("editMessage").innerText = result.message || result.error;
});
