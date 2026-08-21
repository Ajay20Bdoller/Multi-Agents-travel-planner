"use client";

import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// html2pdf.js does not always have TypeScript typings.
// The @ts-expect-error below prevents a TypeScript import warning.
// import html2pdf from "html2pdf.js";


interface TravelApiResponse {
  success: boolean;
  thread_id?: string;
  trip_id?: string;
  answer?: string;
  flight_results?: string;
  hotel_results?: string;
  itinerary?: string;
  llm_calls?: number;
  error?: string;
}

interface SavedTrip {
  trip_id: string;
  thread_id: string;
  user_query: string;
  created_at: string;
}

export default function Home() {
  // ---------------------------------------------------------
  // STATE
  // ---------------------------------------------------------

  const [message, setMessage] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<TravelApiResponse | null>(null);
  const [copied, setCopied] = useState<boolean>(false);
  const [pdfLoading, setPdfLoading] = useState<boolean>(false);
  const [trips, setTrips] = useState<SavedTrip[]>([]);
const [historyLoading, setHistoryLoading] = useState<boolean>(false);
const [showHistory, setShowHistory] = useState<boolean>(false);

  // This ref points to the content that will be converted to PDF.
  const pdfRef = useRef<HTMLDivElement>(null);


  // ---------------------------------------------------------
// LOAD SAVED TRIPS
// ---------------------------------------------------------

const loadTrips = async (): Promise<void> => {
  setHistoryLoading(true);

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/trips"
    );

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(
        data.error || "Failed to load trips."
      );
    }

    setTrips(data.trips || []);
  } catch (error: unknown) {
    if (error instanceof Error) {
      alert(error.message);
    } else {
      alert("Unable to load trip history.");
    }
  } finally {
    setHistoryLoading(false);
  }
};

// ---------------------------------------------------------
// OPEN SAVED TRIP
// ---------------------------------------------------------

const openTrip = async (tripId: string): Promise<void> => {
  try {
    const response = await fetch(
      `http://127.0.0.1:8000/api/trips/${tripId}`
    );

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(
        data.error || "Failed to load trip."
      );
    }

    const trip = data.trip;

    setResult({
      success: true,
      trip_id: trip.trip_id,
      thread_id: trip.thread_id,
      answer: trip.answer,
      flight_results: trip.flight_results,
      hotel_results: trip.hotel_results,
      itinerary: trip.itinerary,
    });

    setShowHistory(false);

    // Scroll to the result
    setTimeout(() => {
      window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth",
      });
    }, 100);

  } catch (error: unknown) {
    if (error instanceof Error) {
      alert(error.message);
    } else {
      alert("Unable to open trip.");
    }
  }
};

  // ---------------------------------------------------------
  // GENERATE TRAVEL PLAN
  // ---------------------------------------------------------

  const generatePlan = async (): Promise<void> => {
    if (!message.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/travel",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: message,
          }),
        }
      );

      const data: TravelApiResponse = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data.error || "Failed to generate travel plan."
        );
      }

      setResult(data);
      // Refresh history so the newly generated trip
// immediately appears in My Trips.
if (showHistory) {
  loadTrips();
}
    } catch (error: unknown) {
      if (error instanceof Error) {
        alert(error.message);
      } else {
        alert("Something went wrong.");
      }
    } finally {
      setLoading(false);
    }
  };

  // ---------------------------------------------------------
  // QUICK PROMPT BUTTONS
  // ---------------------------------------------------------

  const quickPrompt = (text: string): void => {
    setMessage(text);
  };

  // ---------------------------------------------------------
  // COPY PLAN
  // ---------------------------------------------------------

  const copyPlan = async (): Promise<void> => {
    if (!result?.answer) return;

    try {
      await navigator.clipboard.writeText(result.answer);

      setCopied(true);

      // Change "Copied" back to "Copy" after 2 seconds.
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch {
      alert("Unable to copy the plan.");
    }
  };

  // ---------------------------------------------------------
  // DOWNLOAD PDF
  // ---------------------------------------------------------

  const downloadPDF = async (): Promise<void> => {
  if (!pdfRef.current) return;

  setPdfLoading(true);

  try {
    const html2pdf = (await import("html2pdf.js")).default;

    const element = pdfRef.current;

    const options = {
      margin: [10, 10, 12, 10] as [
        number,
        number,
        number,
        number
      ],
      filename: "TripMate-AI-Travel-Plan.pdf",

      image: {
        type: "jpeg" as const,
        quality: 0.98,
      },

      html2canvas: {
        scale: 2,
        useCORS: true,
        logging: false,
      },

      jsPDF: {
        unit: "mm",
        format: "a4",
        orientation: "portrait" as const,
      },
    };

    await html2pdf()
      .set(options)
      .from(element)
      .save();

  } catch (error) {
    console.error("PDF generation error:", error);
    alert("Unable to generate PDF.");
  } finally {
    setPdfLoading(false);
  }
};

  // ---------------------------------------------------------
  // UI
  // ---------------------------------------------------------

  return (
    <main className="min-h-screen bg-[#080d1d] text-white">

      {/* =====================================================
          BACKGROUND GLOW
      ====================================================== */}

      <div className="fixed inset-0 -z-0 overflow-hidden">
        <div className="absolute left-1/4 top-0 h-96 w-96 rounded-full bg-blue-600/20 blur-[120px]" />

        <div className="absolute right-1/4 top-20 h-96 w-96 rounded-full bg-purple-600/20 blur-[120px]" />
      </div>


      <div className="relative z-10 mx-auto max-w-6xl px-6 py-10">

        {/* =====================================================
            HEADER
        ====================================================== */}

        <section className="text-center">

  <div className="flex flex-col items-center justify-between gap-5 md:flex-row">

    <div className="text-left">

      <h1 className="text-5xl font-bold tracking-tight md:text-6xl">
        Plan Your Perfect Trip{" "}

        <span className="bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          with AI
        </span>
      </h1>

      <p className="mx-auto mt-5 max-w-3xl text-lg text-gray-400">
        Search flights, discover hotels, and generate a complete
        travel itinerary using a multi-agent LangGraph system.
      </p>

    </div>

    <button
      onClick={() => {
        const nextState = !showHistory;

        setShowHistory(nextState);

        if (nextState) {
          loadTrips();
        }
      }}
      className="shrink-0 rounded-2xl border border-white/10 bg-[#10172b] px-6 py-3 font-semibold shadow-lg transition hover:bg-white/10"
    >
      🕘 My Trips
    </button>

  </div>

</section>



{/* =====================================================
    TRIP HISTORY
====================================================== */}

{showHistory && (

  <section className="mx-auto mt-8 rounded-3xl border border-white/10 bg-[#10172b]/90 p-6 shadow-2xl">

    <div className="flex items-center justify-between">

      <div>
        <h2 className="text-2xl font-bold">
          My Trips
        </h2>

        <p className="mt-1 text-sm text-gray-400">
          Your previously generated travel plans.
        </p>
      </div>

      <button
        onClick={() => setShowHistory(false)}
        className="rounded-xl border border-white/10 px-4 py-2 text-sm hover:bg-white/10"
      >
        Close
      </button>

    </div>


    {/* LOADING */}

    {historyLoading && (

      <div className="mt-8 text-center text-gray-400">
        Loading your trips...
      </div>

    )}


    {/* EMPTY */}

    {!historyLoading && trips.length === 0 && (

      <div className="mt-8 rounded-2xl border border-dashed border-white/10 p-8 text-center">

        <p className="text-gray-400">
          No saved trips yet.
        </p>

        <p className="mt-2 text-sm text-gray-500">
          Generate your first travel plan to see it here.
        </p>

      </div>

    )}


    {/* TRIP LIST */}

    {!historyLoading && trips.length > 0 && (

      <div className="mt-6 space-y-4">

        {trips.map((trip) => (

          <div
            key={trip.trip_id}
            className="rounded-2xl border border-white/10 bg-[#060b18] p-5 transition hover:border-blue-500/40"
          >

            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

              <div className="min-w-0">

                <h3 className="font-semibold text-white">
                  {trip.user_query}
                </h3>

                <p className="mt-2 text-sm text-gray-500">
                  {new Date(trip.created_at).toLocaleString()}
                </p>

              </div>


              <button
                onClick={() => openTrip(trip.trip_id)}
                className="shrink-0 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-5 py-2 text-sm font-semibold transition hover:scale-[1.02]"
              >
                View Trip →
              </button>

            </div>

          </div>

        ))}

      </div>

    )}

  </section>

)}

        {/* =====================================================
            INPUT CARD
        ====================================================== */}

        <section className="mx-auto mt-10 rounded-3xl border border-white/10 bg-[#10172b]/90 p-6 shadow-2xl backdrop-blur">

          {/* Heading + Online status */}

          <div className="flex items-center justify-between">

            <div>

              <h2 className="text-xl font-bold">
                Where do you want to go?
              </h2>

              <p className="mt-2 text-sm text-gray-400">
                Example: Plan a complete 7 days Japan trip from Delhi
                under ₹2 lakhs.
              </p>

            </div>

            <div className="rounded-full border border-green-500/30 bg-green-500/10 px-4 py-2 text-sm text-green-400">
              🟢 Online
            </div>

          </div>


          {/* =================================================
              TEXTAREA + GENERATE BUTTON
          ================================================== */}

          <div className="mt-6 flex flex-col gap-4 md:flex-row">

            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Plan a 5 days Dubai trip from Delhi with flights, hotels and sightseeing."
              className="min-h-32 flex-1 resize-none rounded-2xl border border-white/10 bg-[#060b18] p-5 text-white outline-none placeholder:text-gray-600 focus:border-blue-500"
            />

            <button
              onClick={generatePlan}
              disabled={loading || !message.trim()}
              className="rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-4 font-bold shadow-lg transition hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-50 md:w-44"
            >
              {loading ? "Generating..." : "Generate Plan"}
            </button>

          </div>


          {/* =================================================
              QUICK PROMPTS
          ================================================== */}

          <div className="mt-5 flex flex-wrap gap-3">

            <button
              onClick={() =>
                quickPrompt(
                  "Plan a 7 day Japan trip from Delhi with flights, hotels and sightseeing."
                )
              }
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-gray-300 hover:bg-white/10"
            >
              Japan Trip
            </button>


            <button
              onClick={() =>
                quickPrompt(
                  "Plan a 5 day Dubai trip from Delhi with flights, hotels and sightseeing."
                )
              }
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-gray-300 hover:bg-white/10"
            >
              Dubai Trip
            </button>


            <button
              onClick={() =>
                quickPrompt(
                  "Plan a 6 day Thailand trip from Delhi with flights, hotels and sightseeing."
                )
              }
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-gray-300 hover:bg-white/10"
            >
              Thailand Trip
            </button>


            <button
              onClick={() =>
                quickPrompt(
                  "Find flights from Delhi to London."
                )
              }
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-gray-300 hover:bg-white/10"
            >
              Global Flights
            </button>

          </div>

        </section>


        {/* =====================================================
            RESULT SECTION
        ====================================================== */}

        {result && (

          <section className="mt-8 rounded-3xl border border-white/10 bg-[#10172b]/90 p-6 shadow-2xl">

            {/* =================================================
                RESULT HEADER
            ================================================== */}

            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

              <div>

                <h2 className="text-2xl font-bold">
                  Your AI Travel Plan
                </h2>

                <p className="mt-1 text-sm text-gray-400">
  Trip ID: {result.trip_id}
</p>

<p className="mt-1 text-xs text-gray-500">
  Thread ID: {result.thread_id}
</p>

              </div>


              {/* =================================================
                  ACTION BUTTONS
              ================================================== */}

              <div className="flex gap-3">

                {/* COPY BUTTON */}

                <button
                  onClick={copyPlan}
                  className="rounded-xl border border-white/20 px-5 py-2 text-sm transition hover:bg-white/10"
                >
                  {copied ? "✓ Copied" : "Copy"}
                </button>


                {/* DOWNLOAD PDF BUTTON */}

                <button
                  onClick={downloadPDF}
                  disabled={pdfLoading}
                  className="rounded-xl bg-green-500 px-5 py-2 text-sm font-bold text-black transition hover:bg-green-400 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {pdfLoading ? "Creating PDF..." : "Download PDF"}
                </button>

              </div>

            </div>


            {/* =================================================
                VISIBLE AI RESPONSE
            ================================================== */}

            <div className="mt-6 rounded-2xl bg-white p-6 text-gray-800">

              <article className="travel-markdown">

                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {result.answer || ""}
                </ReactMarkdown>

              </article>

            </div>


            {/* =================================================
                PDF CONTENT

                This section is NOT displayed separately.

                It is the clean document that html2pdf.js
                converts into an A4 PDF.
            ================================================== */}

            <div className="fixed left-[-10000px] top-0">

              <div
                ref={pdfRef}
                className="pdf-document"
              >

                {/* PDF HEADER */}

                <div className="pdf-header">

                  <h1>Trip planner</h1>

                  <p>
                    AI Generated Travel Plan
                  </p>

                  <div className="pdf-line" />

                  <p className="pdf-thread">
                    Thread ID: {result.thread_id}
                  </p>

                </div>


                {/* PDF BODY */}

                <article className="pdf-markdown">

                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {result.answer || ""}
                  </ReactMarkdown>

                </article>


                {/* PDF FOOTER */}

                <div className="pdf-footer">

                  Generated by Trip planner

                </div>

              </div>

            </div>

          </section>

        )}

      </div>


      {/* =====================================================
          PDF / MARKDOWN STYLES
      ====================================================== */}

      <style jsx global>{`

        /* =====================================================
           NORMAL PAGE MARKDOWN
        ====================================================== */

        .travel-markdown {
          font-size: 15px;
          line-height: 1.8;
        }

        .travel-markdown h1 {
          font-size: 28px;
          font-weight: 800;
          margin-top: 20px;
          margin-bottom: 12px;
        }

        .travel-markdown h2 {
          font-size: 22px;
          font-weight: 800;
          margin-top: 28px;
          margin-bottom: 12px;
          border-bottom: 1px solid #d1d5db;
          padding-bottom: 6px;
        }

        .travel-markdown h3 {
          font-size: 18px;
          font-weight: 700;
          margin-top: 20px;
          margin-bottom: 8px;
        }

        .travel-markdown p {
          margin: 10px 0;
        }

        .travel-markdown ul {
          margin: 10px 0;
          padding-left: 25px;
          list-style-type: disc;
        }

        .travel-markdown ol {
          margin: 10px 0;
          padding-left: 25px;
          list-style-type: decimal;
        }

        .travel-markdown li {
          margin: 5px 0;
        }

        .travel-markdown strong {
          font-weight: 700;
        }

        .travel-markdown table {
          width: 100%;
          border-collapse: collapse;
          margin: 18px 0;
          font-size: 14px;
        }

        .travel-markdown th {
          background: #e5e7eb;
          font-weight: 700;
          text-align: left;
          padding: 9px;
          border: 1px solid #9ca3af;
        }

        .travel-markdown td {
          padding: 9px;
          border: 1px solid #d1d5db;
          vertical-align: top;
        }


        /* =====================================================
           PDF DOCUMENT
        ====================================================== */

        .pdf-document {
          width: 190mm;
          min-height: 270mm;
          padding: 12mm;
          background: white;
          color: #111827;
          font-family: Arial, Helvetica, sans-serif;
          box-sizing: border-box;
        }


        /* PDF HEADER */

        .pdf-header h1 {
          margin: 0;
          font-size: 30px;
          font-weight: 800;
          color: #111827;
        }

        .pdf-header p {
          margin: 4px 0;
          font-size: 13px;
          color: #6b7280;
        }

        .pdf-line {
          height: 2px;
          background: #111827;
          margin-top: 12px;
          margin-bottom: 8px;
        }

        .pdf-thread {
          font-size: 10px !important;
          color: #9ca3af !important;
        }


        /* =====================================================
           PDF MARKDOWN
        ====================================================== */

        .pdf-markdown {
          margin-top: 18px;
          font-size: 12px;
          line-height: 1.55;
          color: #111827;
        }

        .pdf-markdown h1 {
          font-size: 22px;
          font-weight: 800;
          margin-top: 20px;
          margin-bottom: 10px;
        }

        .pdf-markdown h2 {
          font-size: 17px;
          font-weight: 800;
          margin-top: 18px;
          margin-bottom: 8px;
          padding-bottom: 4px;
          border-bottom: 1px solid #6b7280;
          page-break-after: avoid;
        }

        .pdf-markdown h3 {
          font-size: 14px;
          font-weight: 700;
          margin-top: 14px;
          margin-bottom: 6px;
          page-break-after: avoid;
        }

        .pdf-markdown p {
          margin: 7px 0;
        }

        .pdf-markdown ul {
          padding-left: 20px;
          margin: 7px 0;
        }

        .pdf-markdown ol {
          padding-left: 20px;
          margin: 7px 0;
        }

        .pdf-markdown li {
          margin: 3px 0;
        }

        .pdf-markdown strong {
          font-weight: 700;
        }


        /* =====================================================
           PDF TABLE
        ====================================================== */

        .pdf-markdown table {
          width: 100%;
          border-collapse: collapse;
          margin: 12px 0;
          font-size: 10px;
          page-break-inside: auto;
        }

        .pdf-markdown thead {
          display: table-header-group;
        }

        .pdf-markdown tr {
          page-break-inside: avoid;
          page-break-after: auto;
        }

        .pdf-markdown th {
          background: #e5e7eb;
          color: #111827;
          font-weight: 700;
          text-align: left;
          padding: 6px;
          border: 1px solid #9ca3af;
        }

        .pdf-markdown td {
          padding: 6px;
          border: 1px solid #d1d5db;
          vertical-align: top;
        }


        /* =====================================================
           PDF FOOTER
        ====================================================== */

        .pdf-footer {
          margin-top: 25px;
          padding-top: 8px;
          border-top: 1px solid #d1d5db;
          text-align: center;
          font-size: 9px;
          color: #9ca3af;
        }

      `}</style>

    </main>
  );
}