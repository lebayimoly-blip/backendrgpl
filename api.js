const API_BASE_URL = "/api";

// 🔐 Authentification
export async function loginUser(username, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password }),
  });
  if (!response.ok) throw new Error("Échec de la connexion");
  return response.json();
}

export async function getCurrentUser(token) {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Utilisateur non authentifié");
  return response.json();
}

// 👨‍👩‍👧 Familles
export async function getFamilles(token) {
  const response = await fetch(`${API_BASE_URL}/familles/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Erreur lors du chargement des familles");
  return response.json();
}

export async function createFamille(formData, token) {
  const response = await fetch(`${API_BASE_URL}/familles/`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  if (!response.ok) throw new Error("Erreur lors de la création de la famille");
  return response.json();
}

export async function addMembre(familleId, membreData, token) {
  const response = await fetch(`${API_BASE_URL}/familles/${familleId}/members`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(membreData),
  });
  if (!response.ok) throw new Error("Erreur lors de l'ajout du membre");
  return response.json();
}

// 👥 Utilisateurs
export async function getUsers(token) {
  const response = await fetch(`${API_BASE_URL}/users/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Erreur lors du chargement des utilisateurs");
  return response.json();
}

// 📊 Statistiques
export async function getStats(token) {
  const response = await fetch(`${API_BASE_URL}/stats/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Erreur lors du chargement des statistiques");
  return response.json();
}

// 🔁 Doublons
export async function getDoublons(token) {
  const response = await fetch(`${API_BASE_URL}/doublons/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Erreur lors du chargement des doublons");
  return response.json();
}

// 🔄 Synchronisation
export async function syncData(token) {
  const response = await fetch(`${API_BASE_URL}/sync/`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Erreur lors de la synchronisation");
  return response.json();
}

// 🗺️ Zone de travail
export async function getZones(token) {
  const response = await fetch(`${API_BASE_URL}/zones/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Erreur lors du chargement des zones");
  return response.json();
}

export async function setZone(zoneId, token) {
  const response = await fetch(`${API_BASE_URL}/zones/active`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ zone_id: zoneId }),
  });
  if (!response.ok) throw new Error("Erreur lors de la définition de la zone");
  return response.json();
}
