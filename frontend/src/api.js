import axios from "axios";

console.log("=== FRONTEND BUILD CHECK ===");
console.log("VITE_API_BASE_URL =", import.meta.env.VITE_API_BASE_URL);

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";

console.log("USING BASE URL:", API_BASE_URL);

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});
