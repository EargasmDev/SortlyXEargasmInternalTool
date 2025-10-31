import axios from "axios";

// 👇 Add this line (temporary for debugging)
console.log("Frontend built with API base URL:", import.meta.env.VITE_API_BASE_URL);

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});
