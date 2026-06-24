// Cloudflare Worker — the "brain" behind the dashboard chatbox.
// It holds your Gemini key as a SECRET (never exposed to the public page),
// receives a question + the relevant comments, asks Gemini, and returns the answer.
//
// Deploy: paste this into a new Cloudflare Worker, then add two settings:
//   • Secret variable  GEMINI_API_KEY   = your free Gemini key
//   • (optional) plain variable GEMINI_MODEL = gemini-2.5-flash
// See CLOUDFLARE_SETUP.md for click-by-click steps.

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

function json(obj) {
  return new Response(JSON.stringify(obj), {
    headers: { ...CORS, "Content-Type": "application/json" },
  });
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") return new Response(null, { headers: CORS });
    if (request.method !== "POST") return json({ answer: "Send a POST request." });

    let body;
    try { body = await request.json(); } catch { return json({ answer: "Bad request." }); }

    const question = String(body.question || "").slice(0, 500).trim();
    const comments = Array.isArray(body.comments) ? body.comments.slice(0, 40) : [];
    if (!question) return json({ answer: "Ask a question about the comments." });
    if (!comments.length) return json({ answer: "No relevant comments found — try different words." });

    const block = comments
      .map((c, i) => `[${i + 1}] (${c.source}, ${c.sentiment}) ${c.text}`)
      .join("\n");

    const prompt =
      "You are a customer-insight analyst. Answer strictly from these real Argos " +
      "customer comments (from YouTube and Google Play). Never invent feedback, " +
      "numbers, or quotes. Be concise and useful.\n\n" +
      block +
      `\n\nQuestion: ${question}\n\nAnswer using ONLY the comments above. Where it ` +
      "helps, note roughly how many comments raise a point and whether they came " +
      "from YouTube or Google Play.";

    const model = env.GEMINI_MODEL || "gemini-2.5-flash";
    const url =
      `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${env.GEMINI_API_KEY}`;

    try {
      const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { maxOutputTokens: 2048, thinkingConfig: { thinkingBudget: 0 } },
        }),
      });
      const data = await r.json();
      const text =
        data?.candidates?.[0]?.content?.parts?.[0]?.text ||
        ("(no answer — " + (data?.error?.message || "unknown error") + ")");
      return json({ answer: text });
    } catch (e) {
      return json({ answer: "(AI service unavailable: " + e + ")" });
    }
  },
};
