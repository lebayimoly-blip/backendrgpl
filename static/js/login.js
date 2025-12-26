document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  try {
    const res = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    if (!res.ok) {
      document.getElementById("errorMsg").style.display = "block";
      return;
    }

    // Rediriger vers la page d'accueil ou dashboard
    window.location.href = "/menu.html";
  } catch (err) {
    alert("Erreur de connexion : " + err.message);
  }
});
