import { useState, useMemo, useEffect } from "react";
import { Heart, ExternalLink, Sparkles, X, Shirt, Loader } from "lucide-react";

const COLORS = [
  { name: "Charcoal", hex: "#36454F", group: "blues", neutral: true },
  { name: "Light Navy", hex: "#4E5D73", group: "blues", neutral: true },
  { name: "Charcoal Blue", hex: "#3B4F5C", group: "blues", neutral: true },
  { name: "Light Periwinkle", hex: "#C5CBE3", group: "blues", neutral: false },
  { name: "Sapphire", hex: "#0F52BA", group: "blues", neutral: false },
  { name: "Sky Blue", hex: "#87CEEB", group: "blues", neutral: false },
  { name: "Bluebell", hex: "#6B7DB3", group: "blues", neutral: false },
  { name: "Rose", hex: "#C98B8B", group: "pinks", neutral: false },
  { name: "Soft Fuchsia", hex: "#C85A8A", group: "pinks", neutral: false },
  { name: "Geranium", hex: "#D73B3E", group: "pinks", neutral: false },
  { name: "Claret", hex: "#7F1734", group: "pinks", neutral: false },
  { name: "Blush Pink", hex: "#F4C2C2", group: "pinks", neutral: false },
  { name: "Orchid", hex: "#DA70D6", group: "purples", neutral: false },
  { name: "Amethyst", hex: "#9966CC", group: "purples", neutral: false },
  { name: "Icy Violet", hex: "#C4B7D4", group: "purples", neutral: false },
  { name: "Soft Violet", hex: "#9B7DB8", group: "purples", neutral: false },
  { name: "Purple", hex: "#7B2D8E", group: "purples", neutral: false },
  { name: "Damson", hex: "#5B2C6F", group: "purples", neutral: true },
  { name: "Cocoa", hex: "#6B4226", group: "earth", neutral: true },
  { name: "Taupe", hex: "#B3A494", group: "earth", neutral: true },
  { name: "Stone", hex: "#928E85", group: "earth", neutral: true },
  { name: "Shell", hex: "#F5E6D3", group: "whites", neutral: false },
  { name: "Ivory", hex: "#FFFFF0", group: "whites", neutral: false },
  { name: "Soft White", hex: "#F5F5F0", group: "whites", neutral: false },
  { name: "Rose Brown", hex: "#8E6B5A", group: "earth", neutral: true },
  { name: "Pewter", hex: "#8E9196", group: "earth", neutral: true },
  { name: "Spruce", hex: "#2C5545", group: "greens", neutral: true },
  { name: "Teal", hex: "#008080", group: "greens", neutral: true },
  { name: "Sage", hex: "#9CAF88", group: "greens", neutral: false },
  { name: "Grey Green", hex: "#7A8B7A", group: "greens", neutral: true },
];

const GROUPS = [
  { id: "all", label: "All" },
  { id: "blues", label: "Blues" },
  { id: "pinks", label: "Pinks" },
  { id: "purples", label: "Purples" },
  { id: "greens", label: "Greens" },
  { id: "earth", label: "Earth" },
  { id: "whites", label: "Whites" },
];

const SOURCES = [
  { id: "all", label: "All" },
  { id: "asos", label: "ASOS" },
  { id: "very", label: "Very" },
  { id: "mintvelvet", label: "Mint Velvet" },
  { id: "nobodyschild", label: "Nobody's Child" },
  { id: "johnlewis", label: "John Lewis" },
];

const colorMap = {};
COLORS.forEach(c => { colorMap[c.name] = c; });

const DEMO_PRODUCTS = [
  { id: "demo-1", name: "Relaxed Linen Blazer", price: 65, currency: "EUR", colour: "Charcoal", colour_original: "Charcoal Grey", source: "asos", url: "https://www.asos.com", image_url: "", category: "Jackets" },
  { id: "demo-2", name: "Midi Slip Dress", price: 42, currency: "EUR", colour: "Sapphire", colour_original: "Cobalt Blue", source: "asos", url: "https://www.asos.com", image_url: "", category: "Dresses" },
  { id: "demo-3", name: "Cashmere Blend Jumper", price: 89, currency: "EUR", colour: "Icy Violet", colour_original: "Lilac", source: "very", url: "https://www.very.ie", image_url: "", category: "Knitwear" },
  { id: "demo-4", name: "Wide Leg Trousers", price: 38, currency: "EUR", colour: "Taupe", colour_original: "Mushroom", source: "asos", url: "https://www.asos.com", image_url: "", category: "Trousers" },
  { id: "demo-5", name: "Satin Wrap Top", price: 28, currency: "EUR", colour: "Blush Pink", colour_original: "Pale Pink", source: "asos", url: "https://www.asos.com", image_url: "", category: "Tops" },
  { id: "demo-6", name: "Oversized Shirt Dress", price: 55, currency: "EUR", colour: "Soft White", colour_original: "White", source: "very", url: "https://www.very.ie", image_url: "", category: "Dresses" },
  { id: "demo-7", name: "Pleated Midi Skirt", price: 45, currency: "EUR", colour: "Amethyst", colour_original: "Purple", source: "asos", url: "https://www.asos.com", image_url: "", category: "Skirts" },
  { id: "demo-8", name: "Wool Blend Coat", price: 120, currency: "EUR", colour: "Claret", colour_original: "Burgundy", source: "very", url: "https://www.very.ie", image_url: "", category: "Coats" },
  { id: "demo-9", name: "Cotton Poplin Blouse", price: 32, currency: "EUR", colour: "Shell", colour_original: "Cream", source: "asos", url: "https://www.asos.com", image_url: "", category: "Tops" },
  { id: "demo-10", name: "Tailored Cigarette Trousers", price: 48, currency: "EUR", colour: "Light Navy", colour_original: "Steel Blue", source: "very", url: "https://www.very.ie", image_url: "", category: "Trousers" },
  { id: "demo-11", name: "Knitted Vest Top", price: 22, currency: "EUR", colour: "Sage", colour_original: "Sage Green", source: "asos", url: "https://www.asos.com", image_url: "", category: "Tops" },
  { id: "demo-12", name: "Tiered Maxi Dress", price: 58, currency: "EUR", colour: "Rose", colour_original: "Dusty Rose", source: "asos", url: "https://www.asos.com", image_url: "", category: "Dresses" },
  { id: "demo-13", name: "Belted Trench Coat", price: 95, currency: "EUR", colour: "Stone", colour_original: "Grey", source: "very", url: "https://www.very.ie", image_url: "", category: "Coats" },
  { id: "demo-14", name: "Ribbed Bodycon Dress", price: 35, currency: "EUR", colour: "Teal", colour_original: "Dark Teal", source: "asos", url: "https://www.asos.com", image_url: "", category: "Dresses" },
  { id: "demo-15", name: "Cropped Cardigan", price: 40, currency: "EUR", colour: "Orchid", colour_original: "Pink Purple", source: "very", url: "https://www.very.ie", image_url: "", category: "Knitwear" },
  { id: "demo-16", name: "Ruched Bodysuit", price: 24, currency: "EUR", colour: "Soft Fuchsia", colour_original: "Hot Pink", source: "asos", url: "https://www.asos.com", image_url: "", category: "Tops" },
  { id: "demo-17", name: "Puff Sleeve Midi Dress", price: 68, currency: "EUR", colour: "Damson", colour_original: "Aubergine", source: "asos", url: "https://www.asos.com", image_url: "", category: "Dresses" },
  { id: "demo-18", name: "Jersey Wrap Dress", price: 38, currency: "EUR", colour: "Geranium", colour_original: "Red", source: "asos", url: "https://www.asos.com", image_url: "", category: "Dresses" },
  { id: "demo-19", name: "Relaxed Fit Blazer", price: 78, currency: "EUR", colour: "Charcoal Blue", colour_original: "Petrol Blue", source: "very", url: "https://www.very.ie", image_url: "", category: "Jackets" },
  { id: "demo-20", name: "Silk-feel Cami", price: 26, currency: "EUR", colour: "Sky Blue", colour_original: "Baby Blue", source: "asos", url: "https://www.asos.com", image_url: "", category: "Tops" },
  { id: "demo-21", name: "Pointelle Knit Top", price: 29, currency: "EUR", colour: "Soft Violet", colour_original: "Mauve", source: "asos", url: "https://www.asos.com", image_url: "", category: "Knitwear" },
  { id: "demo-22", name: "Utility Jumpsuit", price: 62, currency: "EUR", colour: "Spruce", colour_original: "Forest Green", source: "asos", url: "https://www.asos.com", image_url: "", category: "Jumpsuits" },
  { id: "demo-23", name: "Smocked Midi Dress", price: 55, currency: "EUR", colour: "Purple", colour_original: "Deep Purple", source: "very", url: "https://www.very.ie", image_url: "", category: "Dresses" },
  { id: "demo-24", name: "Oversized Knit Jumper", price: 44, currency: "EUR", colour: "Rose Brown", colour_original: "Mocha", source: "asos", url: "https://www.asos.com", image_url: "", category: "Knitwear" },
];

function getContrastColor(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.6 ? "#2D2D2D" : "#FFFFFF";
}

function lighten(hex, amt) {
  const r = Math.min(255, parseInt(hex.slice(1, 3), 16) + amt);
  const g = Math.min(255, parseInt(hex.slice(3, 5), 16) + amt);
  const b = Math.min(255, parseInt(hex.slice(5, 7), 16) + amt);
  return `rgb(${r},${g},${b})`;
}

function currencySymbol(code) {
  return { EUR: "€", GBP: "£", USD: "$" }[code] || code + " ";
}

function timeSince(dateStr) {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return "just now";
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return days === 1 ? "yesterday" : `${days}d ago`;
}

function ProductCard({ product, isFav, onToggleFav }) {
  const colorInfo = colorMap[product.colour];
  const hex = colorInfo?.hex || "#ccc";
  const contrast = getContrastColor(hex);
  const [imgError, setImgError] = useState(false);
  const hasImage = product.image_url && !imgError;

  return (
    <div style={{
      borderRadius: "14px", overflow: "hidden", background: "#FFFFFF",
      boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04)",
      transition: "transform 0.2s ease, box-shadow 0.2s ease",
      position: "relative",
    }}
    onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-3px)"; e.currentTarget.style.boxShadow = "0 4px 16px rgba(0,0,0,0.1)"; }}
    onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04)"; }}
    >
      <div style={{
        height: "240px", position: "relative", overflow: "hidden",
        background: hasImage ? "#f5f5f5" : `linear-gradient(135deg, ${hex} 0%, ${lighten(hex, 30)} 100%)`,
      }}>
        {hasImage ? (
          <img src={product.image_url} alt={product.name}
            onError={() => setImgError(true)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
            referrerPolicy="no-referrer" />
        ) : (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%" }}>
            <Shirt size={64} color={contrast} style={{ opacity: 0.12 }} strokeWidth={1} />
          </div>
        )}
        <button onClick={(e) => { e.stopPropagation(); onToggleFav(product.id); }}
          style={{
            position: "absolute", top: "10px", right: "10px",
            background: "rgba(255,255,255,0.88)", backdropFilter: "blur(8px)",
            border: "none", borderRadius: "50%", width: "36px", height: "36px",
            display: "flex", alignItems: "center", justifyContent: "center",
            cursor: "pointer", transition: "transform 0.15s ease",
          }}
          onMouseEnter={e => e.currentTarget.style.transform = "scale(1.1)"}
          onMouseLeave={e => e.currentTarget.style.transform = "scale(1)"}
        >
          <Heart size={16} fill={isFav ? "#C85A8A" : "none"} color={isFav ? "#C85A8A" : "#666"} strokeWidth={2} />
        </button>
        <div style={{
          position: "absolute", bottom: "10px", right: "10px",
          background: "rgba(255,255,255,0.88)", backdropFilter: "blur(8px)",
          borderRadius: "6px", padding: "3px 8px",
          fontSize: "10px", fontWeight: "700", letterSpacing: "0.5px",
          color: product.source === "asos" ? "#2D2D2D" : "#E4002B",
          textTransform: "uppercase",
        }}>
          {({"asos":"ASOS","very":"Very","mintvelvet":"Mint Velvet","nobodyschild":"Nobody's Child","johnlewis":"John Lewis","marksandspencer":"M&S","riverisland":"River Island","sezane":"Sézane"})[product.source] || product.source}
        </div>
      </div>
      <div style={{ padding: "14px 14px 12px" }}>
        {product.brand && (
          <div style={{ fontSize: "10px", color: "#bbb", fontWeight: "600", letterSpacing: "0.5px", marginBottom: "2px", textTransform: "uppercase" }}>
            {product.brand}
          </div>
        )}
        <div style={{ fontSize: "11px", color: "#999", fontWeight: "500", letterSpacing: "0.3px", marginBottom: "3px", textTransform: "uppercase" }}>
          {product.category}
        </div>
        <div style={{ fontSize: "14px", fontWeight: "500", color: "#2D2D2D", marginBottom: "8px", lineHeight: "1.3" }}>
          {product.name}
        </div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div style={{ display: "flex", alignItems: "baseline", gap: "5px" }}>
              {product.sale_price ? (
                <>
                  <span style={{ fontSize: "16px", fontWeight: "600", color: "#D73B3E" }}>
                    {currencySymbol(product.currency)}{product.sale_price.toFixed(2)}
                  </span>
                  <span style={{ fontSize: "12px", color: "#999", textDecoration: "line-through" }}>
                    {currencySymbol(product.currency)}{product.price.toFixed(2)}
                  </span>
                </>
              ) : (
                <span style={{ fontSize: "16px", fontWeight: "600", color: "#2D2D2D" }}>
                  {currencySymbol(product.currency)}{product.price.toFixed(2)}
                </span>
              )}
            </div>
            <div style={{
              width: "14px", height: "14px", borderRadius: "50%",
              background: hex, border: "1.5px solid rgba(0,0,0,0.1)", flexShrink: 0,
            }} title={product.colour} />
          </div>
          <a href={product.url} target="_blank" rel="noopener noreferrer"
            onClick={e => e.stopPropagation()}
            style={{
              display: "flex", alignItems: "center", gap: "4px",
              fontSize: "12px", color: "#7B2D8E", fontWeight: "500", textDecoration: "none",
            }}>
            Shop <ExternalLink size={12} />
          </a>
        </div>
        <div style={{ fontSize: "11px", color: "#ccc", marginTop: "6px" }}>
          {product.colour}{product.colour_original && product.colour_original !== product.colour ? ` · "${product.colour_original}"` : ""}
        </div>
      </div>
    </div>
  );
}

function ColorDot({ color, isActive, onClick, count }) {
  const needsBorder = ["Ivory", "Soft White", "Shell"].includes(color.name);
  return (
    <button onClick={onClick} title={`${color.name}${count ? ` (${count})` : ""}`}
      style={{
        width: "32px", height: "32px", borderRadius: "50%", border: "none",
        background: color.hex, cursor: "pointer", flexShrink: 0,
        outline: isActive ? `2.5px solid ${color.hex}` : "2.5px solid transparent",
        outlineOffset: "2.5px",
        boxShadow: needsBorder ? "inset 0 0 0 1px rgba(0,0,0,0.12)" : "none",
        transition: "outline-color 0.15s ease, transform 0.15s ease",
        transform: isActive ? "scale(1)" : "scale(0.88)",
        position: "relative",
      }}
    >
      {count > 0 && isActive && (
        <span style={{
          position: "absolute", top: "-6px", right: "-6px",
          background: "#2D2D2D", color: "#fff", borderRadius: "8px",
          fontSize: "9px", fontWeight: "600", padding: "1px 4px", minWidth: "14px",
          textAlign: "center", lineHeight: "14px",
        }}>{count}</span>
      )}
    </button>
  );
}

export default function PaletteApp() {
  const [products, setProducts] = useState([]);
  const [scrapedAt, setScrapedAt] = useState(null);
  const [isDemo, setIsDemo] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeGroup, setActiveGroup] = useState("all");
  const [activeColors, setActiveColors] = useState(new Set());
  const [activeSource, setActiveSource] = useState("all");
  const [activeCategory, setActiveCategory] = useState("all");
  const [favorites, setFavorites] = useState(new Set());
  const [showFavsOnly, setShowFavsOnly] = useState(false);
  const [showNeutrals, setShowNeutrals] = useState(true);
  const [sortBy, setSortBy] = useState("newest");

  useEffect(() => {
    async function load() {
      try {
        const resp = await fetch("/data/products.json");
        if (!resp.ok) throw new Error("No data");
        const data = await resp.json();
        setProducts(data.products || []);
        setScrapedAt(data.scraped_at);
        setIsDemo(false);
      } catch {
        setProducts(DEMO_PRODUCTS);
        setIsDemo(true);
      }
      setLoading(false);
    }
    load();
  }, []);

  useEffect(() => {
    async function loadFavs() {
      try {
        const r = await window.storage?.get("Soft & Cool Summer-favourites");
        if (r?.value) setFavorites(new Set(JSON.parse(r.value)));
      } catch {}
    }
    loadFavs();
  }, []);

  const saveFavs = async (f) => {
    try { await window.storage?.set("Soft & Cool Summer-favourites", JSON.stringify([...f])); } catch {}
  };

  const colourCounts = useMemo(() => {
    const c = {};
    products.forEach(p => { c[p.colour] = (c[p.colour] || 0) + 1; });
    return c;
  }, [products]);

  const availableCategories = useMemo(() => {
    const counts = {};
    products.forEach(p => {
      const c = p.category || "Other";
      counts[c] = (counts[c] || 0) + 1;
    });
    const ORDER = ["Dresses","Tops","Knitwear","Trousers","Jeans","Skirts","Shorts","Jackets","Coats","Jumpsuits","Co-ords","Loungewear","Swimwear","Shoes","Bags","Accessories","Other"];
    return ORDER.filter(c => counts[c] > 0).map(c => ({ name: c, count: counts[c] }));
  }, [products]);

  const visibleColors = useMemo(() => {
    let f = COLORS;
    if (activeGroup !== "all") f = f.filter(c => c.group === activeGroup);
    if (!showNeutrals) f = f.filter(c => !c.neutral);
    return f;
  }, [activeGroup, showNeutrals]);

  const filteredProducts = useMemo(() => {
    let items = products;
    if (activeSource !== "all") items = items.filter(p => p.source === activeSource);
    if (activeCategory !== "all") items = items.filter(p => p.category === activeCategory);
    if (activeColors.size > 0) items = items.filter(p => activeColors.has(p.colour));
    if (showFavsOnly) items = items.filter(p => favorites.has(p.id));
    if (sortBy === "price-low") items = [...items].sort((a, b) => (a.sale_price || a.price) - (b.sale_price || b.price));
    else if (sortBy === "price-high") items = [...items].sort((a, b) => (b.sale_price || b.price) - (a.sale_price || a.price));
    return items;
  }, [products, activeSource, activeCategory, activeColors, showFavsOnly, favorites, sortBy]);

  const toggleColor = (n) => {
    setActiveColors(prev => { const s = new Set(prev); s.has(n) ? s.delete(n) : s.add(n); return s; });
  };

  const toggleFav = (id) => {
    setFavorites(prev => { const s = new Set(prev); s.has(id) ? s.delete(id) : s.add(id); saveFavs(s); return s; });
  };

  const clearFilters = () => { setActiveColors(new Set()); setActiveGroup("all"); setActiveSource("all"); setShowFavsOnly(false); setShowNeutrals(true); };
  const hasFilters = activeColors.size > 0 || activeSource !== "all" || activeCategory !== "all" || showFavsOnly || activeGroup !== "all";

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh", background: "#FAFAF7" }}>
      <Loader size={24} style={{ animation: "spin 1s linear infinite", color: "#999" }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );

  return (
    <div style={{ fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", background: "#FAFAF7", minHeight: "100vh", color: "#2D2D2D" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { height: 0; width: 0; }
        button:focus-visible { outline: 2px solid #7B2D8E; outline-offset: 2px; }
      `}</style>

      {isDemo && (
        <div style={{ background: "linear-gradient(90deg, #7B2D8E, #C85A8A)", color: "#fff", padding: "8px 20px", fontSize: "12px", textAlign: "center", fontWeight: "500" }}>
          Demo mode — connect the scraper to see live products
        </div>
      )}

      <div style={{ padding: "28px 20px 20px", background: "linear-gradient(180deg, #FFFFFF 0%, #FAFAF7 100%)", borderBottom: "1px solid rgba(0,0,0,0.04)" }}>
        <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: "4px" }}>
          <h1 style={{ fontFamily: "'Playfair Display', Georgia, serif", fontSize: "28px", fontWeight: "500", letterSpacing: "-0.5px" }}>Soft & Cool Summer</h1>
          <button onClick={() => setShowFavsOnly(!showFavsOnly)}
            style={{
              background: showFavsOnly ? "#7B2D8E" : "transparent",
              border: showFavsOnly ? "none" : "1px solid #E0E0E0",
              borderRadius: "20px", padding: "6px 14px",
              display: "flex", alignItems: "center", gap: "5px",
              fontSize: "13px", fontWeight: "500", cursor: "pointer",
              color: showFavsOnly ? "#fff" : "#666",
            }}>
            <Heart size={13} fill={showFavsOnly ? "#fff" : "none"} />
            {favorites.size > 0 && favorites.size} Saved
          </button>
        </div>
        <p style={{ fontSize: "14px", color: "#999" }}>
          {products.length} pieces · UK M{scrapedAt ? ` · Updated ${timeSince(scrapedAt)}` : ""}
        </p>
      </div>

      <div style={{ display: "flex", gap: "0", overflowX: "auto", padding: "0 20px", background: "#FFFFFF", borderBottom: "1px solid rgba(0,0,0,0.06)" }}>
        {GROUPS.map(g => (
          <button key={g.id} onClick={() => { setActiveGroup(g.id); setActiveColors(new Set()); }}
            style={{
              background: "none", border: "none", padding: "12px 16px",
              fontSize: "13px", fontWeight: activeGroup === g.id ? "600" : "400",
              color: activeGroup === g.id ? "#2D2D2D" : "#999",
              cursor: "pointer", whiteSpace: "nowrap",
              borderBottom: activeGroup === g.id ? "2px solid #2D2D2D" : "2px solid transparent",
            }}>
            {g.label}
          </button>
        ))}
      </div>

      <div style={{ padding: "16px 20px 8px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "12px" }}>
          <span style={{ fontSize: "12px", color: "#999", fontWeight: "500" }}>COLOURS</span>
          {activeColors.size > 0 && (
            <button onClick={() => setActiveColors(new Set())} style={{ background: "none", border: "none", fontSize: "11px", color: "#7B2D8E", cursor: "pointer", fontWeight: "500" }}>Clear</button>
          )}
          <div style={{ flex: 1 }} />
          <button onClick={() => setShowNeutrals(!showNeutrals)}
            style={{
              background: showNeutrals ? "rgba(0,0,0,0.05)" : "rgba(123,45,142,0.08)",
              border: "none", borderRadius: "12px", padding: "4px 10px",
              fontSize: "11px", fontWeight: "500", cursor: "pointer",
              color: showNeutrals ? "#666" : "#7B2D8E",
            }}>
            {showNeutrals ? "Hide neutrals" : "Show neutrals"}
          </button>
        </div>
        <div style={{ display: "flex", gap: "8px", overflowX: "auto", paddingBottom: "8px" }}>
          {visibleColors.map(c => (
            <ColorDot key={c.name} color={c} isActive={activeColors.has(c.name)}
              onClick={() => toggleColor(c.name)} count={colourCounts[c.name] || 0} />
          ))}
        </div>
      </div>

      <div style={{ display: "flex", gap: "8px", padding: "4px 20px 16px", flexWrap: "wrap", alignItems: "center" }}>
        {SOURCES.map(s => (
          <button key={s.id} onClick={() => setActiveSource(s.id)}
            style={{
              background: activeSource === s.id ? "#2D2D2D" : "#FFFFFF",
              color: activeSource === s.id ? "#FFFFFF" : "#666",
              border: activeSource === s.id ? "none" : "1px solid #E0E0E0",
              borderRadius: "20px", padding: "6px 16px",
              fontSize: "12px", fontWeight: "500", cursor: "pointer",
            }}>
            {s.label}
          </button>
        ))}
        <div style={{ flex: 1 }} />
        <select value={sortBy} onChange={e => setSortBy(e.target.value)}
          style={{
            background: "#fff", border: "1px solid #E0E0E0", borderRadius: "20px",
            padding: "6px 28px 6px 12px", fontSize: "12px", color: "#666", cursor: "pointer",
            appearance: "none",
            backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23999' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
            backgroundRepeat: "no-repeat", backgroundPosition: "right 8px center",
          }}>
          <option value="newest">Newest</option>
          <option value="price-low">Price: Low → High</option>
          <option value="price-high">Price: High → Low</option>
        </select>
        {hasFilters && (
          <button onClick={clearFilters}
            style={{
              background: "none", border: "1px solid #E0E0E0", borderRadius: "20px",
              padding: "6px 12px", fontSize: "12px", color: "#999", cursor: "pointer",
              display: "flex", alignItems: "center", gap: "4px",
            }}>
            <X size={12} /> Clear all
          </button>
        )}
      </div>

      {/* Category filter */}
      {availableCategories.length > 0 && (
        <div style={{
          display: "flex", gap: "8px", padding: "0 20px 16px",
          overflowX: "auto",
        }}>
          <button onClick={() => setActiveCategory("all")}
            style={{
              background: activeCategory === "all" ? "#7B2D8E" : "#FFFFFF",
              color: activeCategory === "all" ? "#FFFFFF" : "#666",
              border: activeCategory === "all" ? "none" : "1px solid #E0E0E0",
              borderRadius: "20px", padding: "6px 16px",
              fontSize: "12px", fontWeight: "500", cursor: "pointer",
              whiteSpace: "nowrap", flexShrink: 0,
            }}>
            All Types
          </button>
          {availableCategories.map(cat => (
            <button key={cat.name} onClick={() => setActiveCategory(cat.name)}
              style={{
                background: activeCategory === cat.name ? "#7B2D8E" : "#FFFFFF",
                color: activeCategory === cat.name ? "#FFFFFF" : "#666",
                border: activeCategory === cat.name ? "none" : "1px solid #E0E0E0",
                borderRadius: "20px", padding: "6px 16px",
                fontSize: "12px", fontWeight: "500", cursor: "pointer",
                whiteSpace: "nowrap", flexShrink: 0,
              }}>
              {cat.name} <span style={{ opacity: 0.6, fontSize: "11px" }}>{cat.count}</span>
            </button>
          ))}
        </div>
      )}

      <div style={{ padding: "0 16px 32px" }}>
        {filteredProducts.length === 0 ? (
          <div style={{ textAlign: "center", padding: "60px 20px", color: "#999" }}>
            <Shirt size={40} strokeWidth={1} style={{ marginBottom: "12px", opacity: 0.3 }} />
            <p style={{ fontSize: "15px", fontWeight: "500", marginBottom: "6px", color: "#666" }}>
              {showFavsOnly ? "No saved items yet" : "No matches for these filters"}
            </p>
            <p style={{ fontSize: "13px" }}>
              {showFavsOnly ? "Tap the heart on items you love" : "Try adjusting your colour or source filters"}
            </p>
          </div>
        ) : (
          <>
            <div style={{ fontSize: "12px", color: "#999", marginBottom: "12px", paddingLeft: "4px" }}>
              {filteredProducts.length} {filteredProducts.length === 1 ? "piece" : "pieces"}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(170px, 1fr))", gap: "14px" }}>
              {filteredProducts.map(p => (
                <ProductCard key={p.id} product={p} isFav={favorites.has(p.id)} onToggleFav={toggleFav} />
              ))}
            </div>
          </>
        )}
      </div>

      <div style={{ textAlign: "center", padding: "20px", borderTop: "1px solid rgba(0,0,0,0.04)", fontSize: "12px", color: "#bbb", lineHeight: "1.6" }}>
        <p>Curated daily · UK Medium · ASOS & Very</p>
      </div>
    </div>
  );
}
