// App.jsx — ConcertCloud Tickets + Map (React MVP)
// Setup:
//   npm create vite@latest concertcloud-web -- --template react
//   cd concertcloud-web && npm i
//   echo "VITE_API_URL=http://127.0.0.1:8000" > .env
//   npm run dev  (http://127.0.0.1:5173)

import { useEffect, useMemo, useState } from "react";
import LandingPage from "./pages/LandingPage";
export default function App() {
  return <LandingPage />;
}

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function App() {
  // Filters / state
  const [eventId, setEventId] = useState(1);
  const [qty, setQty] = useState(1);
  const [maxPrice, setMaxPrice] = useState("");
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [sort, setSort] = useState("best");
  const [sectionId, setSectionId] = useState(null);
  const [together, setTogether] = useState(false);

  // Data
  const [listings, setListings] = useState([]);
  const [mapData, setMapData] = useState(null);

  // UI
  const [loadingList, setLoadingList] = useState(false);
  const [loadingMap, setLoadingMap] = useState(false);
  const [error, setError] = useState("");

  const params = useMemo(() => {
    const p = new URLSearchParams();
    p.set("sort", sort);
    p.set("qty", String(qty || 1));
    if (maxPrice) p.set("max_price", String(maxPrice));
    if (verifiedOnly) p.set("verified_only", "true");
    if (sectionId != null) p.set("section_id", String(sectionId));
    if (together) p.set("together", "true");
    return p.toString();
  }, [sort, qty, maxPrice, verifiedOnly, sectionId, together]);

  async function fetchJSON(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return await r.json();
  }

  async function loadListings() {
    setLoadingList(true); setError("");
    try {
      const data = await fetchJSON(`${API}/events/${eventId}/listings?${params}`);
      setListings(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(`Listings error: ${e.message}`);
      setListings([]);
    } finally {
      setLoadingList(false);
    }
  }

  async function loadMap() {
    setLoadingMap(true); setError("");
    try {
      const data = await fetchJSON(`${API}/events/${eventId}/map`);
      setMapData(data);
    } catch (e) {
      setError(`Map error: ${e.message}`);
      setMapData(null);
    } finally {
      setLoadingMap(false);
    }
  }

  function resetSectionFilter() {
    setSectionId(null);
  }

  useEffect(() => {
    // initial load
    loadListings();
    loadMap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const viewBox = mapData ? `0 0 ${mapData.venue.w} ${mapData.venue.h}` : "0 0 1000 700";

  const Header = (
    <div style={headerStyle}>
      <strong style={{ fontSize: 18 }}>ConcertCloud — Tickets</strong>

      <label>Event ID
        <input
          type="number" min={1} value={eventId}
          onChange={e => setEventId(Number(e.target.value || 1))}
          style={inpStyle}
        />
      </label>

      <label>Qty
        <input
          type="number" min={1} max={8} value={qty}
          onChange={e => setQty(Number(e.target.value || 1))}
          style={inpStyle}
        />
      </label>

      <label>Max $
        <input
          type="number" placeholder="e.g. 120" value={maxPrice}
          onChange={e => setMaxPrice(e.target.value)}
          style={inpStyle}
        />
      </label>

      <label style={{ display: "flex", alignItems: "center", gap: 6 }}>
        Verified
        <input type="checkbox" checked={verifiedOnly} onChange={e => setVerifiedOnly(e.target.checked)} />
      </label>

      <label style={{ display: "flex", alignItems: "center", gap: 6 }}>
        Together
        <input type="checkbox" checked={together} onChange={e => setTogether(e.target.checked)} />
      </label>

      <label>Sort
        <select value={sort} onChange={e => setSort(e.target.value)} style={selStyle}>
          <option value="best">best</option>
          <option value="cheapest">cheapest</option>
        </select>
      </label>

      <div style={{ flex: 1 }} />

      <button onClick={() => { resetSectionFilter(); loadListings(); }} style={btnStyle}>Apply</button>
      <button onClick={() => loadMap()} style={btnStyle}>
        <svg width="18" height="18" viewBox="0 0 24 24" style={{ marginRight: 6 }}>
          <path d="M9 3l6 2 6-2v16l-6 2-6-2-6 2V5l6-2zM9 5v14l6 2V7L9 5z" fill="#5a2c82"/>
        </svg>
        Map
      </button>
    </div>
  );

  return (
    <div style={pageStyle}>
      {Header}

      {error && <div style={errStyle}>{error}</div>}

      <div style={cardStyle}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#f0b8ff" }}>
              <Th>Section</Th>
              <Th>Row</Th>
              <Th>Seat</Th>
              <Th>Price</Th>
            </tr>
          </thead>
          <tbody>
            {loadingList ? (
              <tr><td colSpan={4} style={{ padding: 14 }}>Loading listings…</td></tr>
            ) : listings.length === 0 ? (
              <tr><td colSpan={4} style={{ padding: 14 }}>No listings match your filters.</td></tr>
            ) : (
              listings.slice(0, 100).map(x => (
                <tr key={x.id} style={{ borderTop: "1px solid #e9c9ff" }}>
                  <Td>{x.section ?? ""}</Td>
                  <Td>{x.row ?? ""}</Td>
                  <Td>{x.seat ?? ""}</Td>
                  <Td>${Number(x.price).toFixed(2)}</Td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        <div style={{ padding: 12 }}>
          <svg width="100%" viewBox={viewBox} style={{ background: "#faf2ff", borderRadius: 12 }}>
            {mapData ? (
              <SeatMap
                map={mapData}
                sectionId={sectionId}
                onToggleSection={(id) => setSectionId(prev => prev === id ? null : id)}
              />
            ) : (
              <text x="20" y="40" fill="#5a2c82" fontSize="18">
                {loadingMap ? "Loading map…" : "Click Map to load the venue layout."}
              </text>
            )}
          </svg>
          <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 8 }}>
            <span style={{ fontSize: 13, color: "#5a2c82" }}>Tip: click a section to filter listings; click again to clear.</span>
            {sectionId && <button onClick={resetSectionFilter} style={linkBtn}>Clear section filter</button>}
          </div>
        </div>
      </div>
    </div>
  );
}

function Th({ children }) {
  return <th style={{ textAlign: "left", padding: 10, fontWeight: 700 }}>{children}</th>;
}
function Td({ children }) {
  return <td style={{ padding: 10 }}>{children}</td>;
}

function SeatMap({ map, sectionId, onToggleSection }) {
  const stageX = map.venue.stage_x - 120;
  const stageY = map.venue.stage_y - 20;

  return (
    <g>
      <rect x={stageX} y={stageY} width={240} height={40} rx={8} fill="#5a2c82" />
      <text x={stageX + 120} y={stageY - 10} textAnchor="middle" fill="#5a2c82" fontSize="14">STAGE</text>

      {map.sections.map(s => (
        <g key={s.id} onClick={() => onToggleSection(s.id)} style={{ cursor: "pointer" }}>
          <circle cx={s.cx} cy={s.cy} r={40} fill={sectionId===s.id ? "#e6a8ff" : "#f0b8ff"} stroke="#5a2c82" strokeWidth={2} />
          <text x={s.cx} y={s.cy + 6} textAnchor="middle" fontSize="18" fill="#2a1436">{s.name}</text>
        </g>
      ))}

      {map.cheapest?.[0] && (
        <MapLabel sections={map.sections} sectionId={map.cheapest[0].section_id} label="★ cheapest" color="#0b6" />
      )}
      {map.best?.[0] && (
        <MapLabel sections={map.sections} sectionId={map.best[0].section_id} label="💜 best" color="#a020f0" />
      )}
    </g>
  );
}

function MapLabel({ sections, sectionId, label, color }) {
  const sec = sections.find(z => z.id === sectionId);
  if (!sec) return null;
  return <text x={sec.cx} y={sec.cy - 48} textAnchor="middle" fontWeight={700} fill={color}>{label}</text>;
}

// Styles
const pageStyle = { fontFamily: "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif", color: "#2a1436", padding: 16, maxWidth: 1200, margin: "0 auto" };
const headerStyle = { display: "flex", gap: 12, alignItems: "center", padding: "10px 14px", background: "#8d3daf", color: "white", borderRadius: 16, marginBottom: 12, boxShadow: "0 6px 16px rgba(141,61,175,0.25)" };
const inpStyle = { width: 90, marginLeft: 6, borderRadius: 8, border: 0, padding: "6px 8px" };
const selStyle = { marginLeft: 6, borderRadius: 8, border: 0, padding: "6px 8px" };
const btnStyle = { display: "inline-flex", alignItems: "center", background: "#f2a7ff", color: "#2a1436", border: 0, borderRadius: 10, padding: "8px 12px", cursor: "pointer", fontWeight: 600 };
const cardStyle = { background: "#f6d6ff", borderRadius: 16, overflow: "hidden", boxShadow: "0 6px 16px rgba(141,61,175,0.12)" };
const errStyle = { background: "#ffe0e0", color: "#8a1f1f", padding: 10, borderRadius: 12, marginBottom: 12 };
const linkBtn = { background: "transparent", border: 0, color: "#5a2c82", cursor: "pointer", textDecoration: "underline" };
