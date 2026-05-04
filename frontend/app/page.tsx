"use client";

import { FormEvent, useState } from "react";

type HigherSelfReading = {
  surface_request: string;
  underlying_need: string;
  deeper_intention: string;
  guidance_note: string;
};

type ChatResponse = {
  response: string;
  selected_mode: string;
  higher_self_reading: HigherSelfReading | null;
  distortion_applied: boolean;
  distortion_dominant: string | null;
  qtvl_verdict: "pass" | "enrich" | "revise";
  qtvl_checks_passed: number;
  shadow_audit_flags: string[];
  constitutional_flags: Record<string, boolean>;
};

type Message = {
  role: "user" | "assistant";
  text: string;
  mode?: string;
};

function DiagnosticsPanel({ diagnostics }: { diagnostics: ChatResponse | null }) {
  if (!diagnostics) return null;
  const hs = diagnostics.higher_self_reading;
  const cf = diagnostics.constitutional_flags || {};

  return (
    <div className="mt-4 space-y-3 font-mono text-sm">
      <div className="rounded-lg bg-[#0f172a] p-4 text-gray-100">
        <div className="mb-2 text-base">🔍 Анализ запроса</div>
        <div className="text-gray-300">Поверхностный запрос:</div>
        <div>{hs?.surface_request ?? "—"}</div>
        <div className="mt-2 text-gray-300">Глубинная потребность:</div>
        <div>{hs?.underlying_need ?? "—"}</div>
        <div className="mt-2 text-gray-300">Намерение:</div>
        <div>{hs?.deeper_intention ?? "—"}</div>
      </div>

      <div className="rounded-lg bg-[#0f172a] p-4 text-gray-100">
        <div className="mb-2 text-base">⚡ Обработка</div>
        <div>Режим: {diagnostics.selected_mode}</div>
        <div>
          QTVL: {diagnostics.qtvl_verdict} ({diagnostics.qtvl_checks_passed}/4)
        </div>
        <div>Искажение: {diagnostics.distortion_dominant ?? "не обнаружено"}</div>
        <div>Коррекция: {diagnostics.distortion_applied ? "да" : "нет"}</div>
      </div>

      <div className="rounded-lg bg-[#0f172a] p-4 text-gray-100">
        <div className="mb-2 text-base">🛡️ Конституционные проверки</div>
        <div>{cf.preserve_agency ? "✅" : "❌"} preserve_agency</div>
        <div>{cf.anti_manipulation ? "✅" : "❌"} anti_manipulation</div>
        <div>{cf.dignity_guard ? "✅" : "❌"} dignity_guard</div>
        <div>{cf.telos_integrity ? "✅" : "❌"} telos_integrity</div>
      </div>
    </div>
  );
}

export default function Home() {
  const API_URL = (
    process.env.NEXT_PUBLIC_API_URL || "https://backend-production-eeb8.up.railway.app"
  ).replace(/\/+$/, "");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showDiagnostics, setShowDiagnostics] = useState(false);
  const [diagnostics, setDiagnostics] = useState<ChatResponse | null>(null);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data: ChatResponse = await response.json();
      setDiagnostics(data);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.response, mode: data.selected_mode },
      ]);
    } catch (error) {
      console.error("Fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-950 px-4 py-8 text-gray-100">
      <div className="mx-auto max-w-[700px]">
        <header className="mb-6">
          <h1 className="text-2xl font-semibold">Archi</h1>
          <p className="text-sm text-gray-400">Guide Intelligence</p>
        </header>

        <section className="rounded-xl bg-gray-900 p-4">
          <div className="mb-4 h-[52vh] space-y-3 overflow-y-auto pr-1">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`max-w-[85%] rounded-lg px-3 py-2 ${
                  m.role === "user"
                    ? "ml-auto bg-blue-700 text-white"
                    : "mr-auto bg-gray-800 text-gray-100"
                }`}
              >
                {m.role === "assistant" && m.mode ? (
                  <div className="mb-1 text-xs text-gray-400">Mode: {m.mode}</div>
                ) : null}
                <div className="whitespace-pre-wrap">{m.text}</div>
              </div>
            ))}
          </div>

          <form onSubmit={onSubmit} className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Напиши что тебя беспокоит или о чём думаешь..."
              className="flex-1 rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-gray-100 outline-none"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-blue-700 px-4 py-2 text-white disabled:opacity-50"
            >
              {loading ? "..." : "Отправить"}
            </button>
          </form>
        </section>

        <div className="mt-4">
          <button
            type="button"
            onClick={() => setShowDiagnostics((v) => !v)}
            className="rounded-md border border-gray-700 px-3 py-2 text-sm text-gray-200"
          >
            {showDiagnostics ? "Скрыть диагностику" : "Показать диагностику"}
          </button>
          {showDiagnostics ? <DiagnosticsPanel diagnostics={diagnostics} /> : null}
        </div>
      </div>
    </main>
  );
}
