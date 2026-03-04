export default {
    content: ["./index.html", "./src/**/*.{ts,tsx}"],
    theme: {
        extend: {
            colors: {
                uni: {
                    primary: "#1e3a8a",
                    accent: "#3b82f6",
                    light: "#60a5fa",
                    white: "#ffffff",
                    neutral: "#f3f4f6"
                }
            },
            boxShadow: {
                card: "0 8px 30px rgba(30,58,138,0.08)"
            }
        }
    },
    plugins: []
};
