# file: app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import re
import numpy as np

# --- Streamlit Page Setup ---
st.set_page_config(page_title="🏭Asphalt Batching Plants - Vietnam", layout="wide")
st.header("🗺️ Investigate Asphalt Batching Plants Map")
st.markdown(
    """
    <div style="
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 10px;
        font-size: 14px;
    ">
        <div style="display:flex; align-items:center; gap:6px;">
            <div style="width:14px; height:14px; border-radius:50%; background-color:green;"></div>
            <span>Viet Nam</span>
        </div>
        <div style="display:flex; align-items:center; gap:6px;">
            <div style="width:14px; height:14px; border-radius:50%; background-color:red;"></div>
            <span>Japan</span>
        </div>
        <div style="display:flex; align-items:center; gap:6px;">
            <div style="width:14px; height:14px; border-radius:50%; background-color:blue;"></div>
            <span>Korea</span>
        </div> <div style="display:flex; align-items:center; gap:6px;">
            <div style="width:14px; height:14px; border-radius:50%; background-color:purple;"></div>
            <span>China</span>
        </div>
        <div style="display:flex; align-items:center; gap:6px;">
            <div style="width:14px; height:14px; border-radius:50%; background-color:grey;"></div>
            <span>Other</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar: File Upload ---
# ------------------------------------------------------------
# 📊 LOAD DATA FROM GOOGLE SHEETS
# ------------------------------------------------------------
SHEET_ID = "1dzA9JJYzI_i9E4NwEGM9mnZlY8s6xf6RQHzhMHTx4y4"  # TODO: replace with your actual sheet ID
SHEET_NAME = "north"  # Change this to match your Google Sheet tab name
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data(ttl=3000)
def load_data_from_gsheet(url):
    """Load data from a public Google Sheet shared as CSV."""
    return pd.read_csv(url)

# Load Google Sheet data with fallback
try:
    df = load_data_from_gsheet(CSV_URL)
    st.sidebar.success("✅ Loaded data from Google Sheets successfully.")
except Exception as e:
    st.sidebar.error(f"⚠️ Failed to load data from Google Sheets: {e}")
    default_data = [
        {"name": "Plant A", "lat": 21.0278, "lon": 105.8342, "capacity": 120, "year": 1999,
         "supplier": "Viet Nam", "product": "5000", "note": "Northern region"},
        {"name": "Plant B", "lat": 10.7626, "lon": 106.6602, "capacity": 100, "year": 2010,
         "supplier": "Nhat Ban", "product": "4000", "note": "Southern region"},
    ]
    df = pd.DataFrame(default_data)

# Manual refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# --- Define Color by Supplier ---
def get_color(supplier: str) -> str:
    if "Viet Nam" in supplier:
        return "green"
    elif "Nhat Ban" in supplier:
        return "red"
    elif "Han Quoc" in supplier:
        return "blue"
    elif "Trung Quoc" in supplier:
        return "purple"
    return "grey"
# --- Sidebar Toggle to Show/Hide Plant Labels ---
show_labels = st.sidebar.toggle("Show Plant Names", value=True)

# --- Sidebar: Filters ---
# supplier_options = ["All"] + sorted(df["supplier"].dropna().unique().tolist())
# year_options = ["All"] + sorted(df["year"].dropna().unique().tolist())

# supplier_filter = st.sidebar.selectbox("Filter by Supplier", supplier_options)
# year_filter = st.sidebar.selectbox("Filter by Year", year_options)

# filtered_df = df.copy()
# if supplier_filter != "All":
#     filtered_df = filtered_df[filtered_df["supplier"] == supplier_filter]
# if year_filter != "All":
#     filtered_df = filtered_df[filtered_df["year"] == year_filter]

st.sidebar.header("Plant Information")
info_placeholder = st.sidebar.empty()
info_placeholder.info("Click a circle on the map to view plant details.")


# --- Create Map ---
m = folium.Map(location=[10.816446710933224, 106.65637042962993], zoom_start=10)

# --- Add 30km & 60km semi-transparent filled radius zones around Hanoi ---
center_lat, center_lon = 21.030382, 105.852414
center_south_lat, center_south_lon = 10.816446710933224, 106.65637042962993
# --- Draw Polyline for Route ---
polyline_coords = [
    (21.24199742183946, 105.7596070304483),
    (21.18541120324732, 105.7091199679863),
    (21.16768775118246, 105.7017821338598),
    (21.11701055822842, 105.6946421866432),
    (21.09920989187595, 105.6888272923083),
    (21.07638617869617, 105.6789706222959),
    (21.05668096373673, 105.6815919507452),
    (21.05637328838472, 105.6814682424146),
    (21.04401351844446, 105.684393081144),
    (21.03325987517226, 105.6914163240522),
    (21.0220816959434, 105.7008182997981),
    (21.00908905656098, 105.7068307444106),
    (20.98991226017656, 105.7111097796557),
    (20.96810086562991, 105.7330144323358),
    (20.94114160705679, 105.7495810122481),
    (20.93007770079306, 105.7605836101647),
    (20.91810878210952, 105.7727436978516),
    (20.89885757634577, 105.7882568077542),
    (20.89311720284124, 105.7954696173498),
    (20.88734392611168, 105.8122004051177),
    (20.89001169337871, 105.857775412133),
    (20.88714448163163, 105.8820510127565),
    (20.88855858676115, 105.897146623398),
    (20.89657848562472, 105.9101737292405),
    (20.90064069586061, 105.9246503980582),
    (20.90196912726038, 105.9547134630373),
    (20.91376049814836, 105.9809909985116),
    (20.92379486883276, 105.9942720097042),
    (20.96403993391647, 106.0205637875827),
    (20.97351786945435, 106.0233623781725),
    (20.97379260240639, 106.0233580509142),
    (20.98858716569817, 106.0244225680345),
    (20.99639164974496, 106.0296112367933),
    (21.01493007029702, 106.0869401367259),
    (21.02554157561978, 106.0973760226284),
    (21.04102504523776, 106.1015441478436),
    (21.13983488174282, 106.083234356222),
    (21.14820079923921, 106.0618848246622),
    (21.151451648834, 106.0588870126468),
]

# Add the polyline with color and style
folium.PolyLine(
    locations=polyline_coords,
    color="blue",
    weight=5,
    opacity=1,
    dash_array="5, 10",  # dashed line for better visibility
    tooltip="Ring Road 4",
).add_to(m)
# --- Add Second Polyline (Ring Road 5 or another route) ---
polyline2_coords = [
    (21.52096710819852, 106.0727788664571),
    (21.47817619656684, 105.9384976843167),
    (21.48568267571112, 105.8759410729293),
    (21.45193910328372, 105.7757104482872),
    (21.42422074587156, 105.7388880410921),
    (21.4204701014305, 105.6980345920398),
    (21.39203266820101, 105.690903233798),
    (21.3021804334191, 105.6120096154762),
    (21.20589881905731, 105.5014454813026),
    (21.17770099839876, 105.4841005917667),
    (21.1561727877617, 105.4855064868124),
    (21.1324198883168, 105.4907628708742),
    (21.10252886583633, 105.4840993796312),
    (21.09461850179874, 105.4844611464506),
    (21.08801012446817, 105.4875561036603),
    (20.99757808802067, 105.5415290380439),
    (20.99152380189645, 105.5417379166358),
    (20.96372341627243, 105.5340528251503),
    (20.95749337599302, 105.5342842213481),
    (20.95322558642522, 105.5365920180692),
    (20.9038555559891, 105.5750309545221),
    (20.89779445468059, 105.577117864679),
    (20.89331632302276, 105.5770402942477),
    (20.81488763345077, 105.5605784556671),
    (20.81060217198035, 105.5604895899383),
    (20.80644878491101, 105.5619422009786),
    (20.77511306847138, 105.5798659756193),
    (20.69572204669549, 105.6641471725791),
    (20.60866326990645, 105.7376056933251),
    (20.54958068584981, 105.8689253116344),
    (20.54234076547283, 105.9108237500606),
    (20.55134340093689, 105.9656207499767),
    (20.50518861876482, 106.1524961749976),
    (20.56285715797698, 106.2338436458951),
    (20.67682633287614, 106.262393817694),
    (20.77071210381342, 106.3682061662054),
    (20.85150268193881, 106.3950011701824),
    (20.96093312105472, 106.4979125415268),
    (20.96425941800092, 106.4990892571285),
    (20.96739558272206, 106.4980956495876),
    (20.97214919966506, 106.486511164304),
    (21.03301688707862, 106.4287003302116),
    (21.03892763358844, 106.3960038460929),
    (21.08787664713286, 106.4408929454827),
    (21.1789651198858, 106.3571512249969),
    (21.22616036458719, 106.3409557692345),
    (21.25418415826013, 106.2490509849837),
    (21.29791252482445, 106.2088818826698),
    (21.34701991836202, 106.216090768205),
    (21.38018938431252, 106.2010707862809),
    (21.43913460581471, 106.0968435415907),
    (21.52096710819852, 106.0727788664571),
]

# Add the polyline with color and style
folium.PolyLine(
    locations=polyline2_coords,
    color="green",
    weight=4,
    opacity=0.9,
    dash_array="10, 10",  # dashed red line
    tooltip="Ring Road 5",
).add_to(m)

#North Center

folium.Circle(
    location=[center_lat, center_lon],
    radius=30000,  # 30 km
    color="orange",
    weight=2,
    tooltip="30 km radius",
).add_to(m)

folium.Circle(
    location=[center_lat, center_lon],
    radius=60000,  # 60 km
    color="purple",
    weight=2,
    tooltip="60 km radius",
).add_to(m)

folium.Marker(
    [center_lat, center_lon],
    popup="Center Point",
    icon=folium.Icon(color="red", icon="star"),
).add_to(m)

#South Center

folium.Circle(
    location=[center_south_lat, center_south_lon],
    radius=30000,  # 30 km
    color="orange",
    weight=2,
    tooltip="30 km radius",
).add_to(m)

folium.Circle(
    location=[center_south_lat, center_south_lon],
    radius=60000,  # 60 km
    color="purple",
    weight=2,
    tooltip="60 km radius",
).add_to(m)

folium.Marker(
    [center_south_lat, center_south_lon],
    popup="Center Point",
    icon=folium.Icon(color="red", icon="star"),
).add_to(m)
# --- Bridge Location ---

bridges = {
    "Me So Bridge": [20.891177, 105.897808],
    "Ngoc Hoi Bridge": [20.934934, 105.881964],
    "Tran Hung Dao Bridge": [21.019870, 105.867898],
    "Tu Lien Bridge": [21.070019, 105.849699],
    "Hong Ha Bridge": [21.139920, 105.698061],
    "Hoai Thuong Bridge": [21.07147245346811, 106.09552058485136],
}

for name, coords in bridges.items():
    # Marker for bridge location
    folium.Marker(
        location=coords,
        icon=folium.Icon(color="blue", icon="road"),
    ).add_to(m)

    # Estimate text width (auto-adjust but max 500)
    text_width = min(len(name) * 8 + 40, 500)

    # Always-visible text label with fixed background coverage
    folium.map.Marker(
        coords,
        icon=folium.DivIcon(
            html=f"""
            <div style="
                display: inline-block;
                background-color: rgba(255, 255, 255, 0.85);
                border-radius: 6px;
                padding: 3px 8px;
                border: 1px solid #666;
                font-size: 9pt;
                font-weight: 400;
                color: black;
                width: fit-content;
                max-width: {text_width}px;
                white-space: nowrap;
                box-shadow: 0px 1px 2px rgba(0,0,0,0.2);
                transform: translate(30px, -20px);
            ">
                {name}
            </div>
            """,
        ),
    ).add_to(m)

 #--- Closed Polyline / Polygon Zone ---
polygon_coords = [
    [20.88924288323013, 105.8807155104714],
    [20.88583495414192, 105.8818686437095],
    [20.88738429614779, 105.8974898640256],
    [20.89641671886349, 105.913947716764],
    [20.90035613463641, 105.9544369524273],
    [20.92159875555566, 105.994282323926],
    [20.94664729843689, 106.0109387700173],
    [20.94914339210757, 106.0118601790391],
    [20.95031390742827, 106.0098936279089],
    [20.92451905997301, 105.9930600011564],
    [20.91473989978944, 105.9793447796102],
    [20.90392222390733, 105.9541182997613],
    [20.90217789932237, 105.924652122508],
    [20.89749325346639, 105.9096162234453],
    [20.89058011154443, 105.8964331151194],
    [20.88924288323013, 105.8807155104714],
]

# Draw as filled polygon
folium.Polygon(
    locations=polygon_coords,
    color="red",
    weight=2,
    fill=True,
    fill_color="red",
    fill_opacity=0.35,
    tooltip="CC1 Area",
).add_to(m)

# --- Closed Polygons (2 zones) ---

# Polygon 1
polygon1_coords = [
    [21.16731314767603, 105.6986203736546],
    [21.16516092160808, 105.7033197363895],
    [21.18378683428685, 105.7112544681083],
    [21.23026883003332, 105.7520319412219],
    [21.23226898307661, 105.7458378107456],
    [21.18745575944248, 105.7062926063253],
    [21.16731314767603, 105.6986203736546],
]

folium.Polygon(
    locations=polygon1_coords,
    color="red",
    weight=2,
    fill=True,
    fill_color="red",
    fill_opacity=0.35,
    tooltip="CC1 Area",
).add_to(m)


# Polygon 2
polygon2_coords = [
    [21.15282983020117, 106.0590917848442],
    [21.14917315303276, 106.0559605292514],
    [21.13611320443047, 106.0857134860781],
    [21.14139713599917, 106.0861306103758],
    [21.15282983020117, 106.0590917848442],
]

folium.Polygon(
    locations=polygon2_coords,
    color="red",
    weight=2,
    fill=True,
    fill_color="red",
    fill_opacity=0.35,
    tooltip="CC1 Area",
).add_to(m)

# --- Define color by year ---
# def get_color(year: int) -> str:
#     if year == "Viet Nam":
#         return "green"
#     return "blue"

# --- Add CircleMarkers and Optional Labels for Plants ---
for _, row in df.iterrows():
    color = get_color(row["supplier"])
    radius = max(8, row["capacity"] / 10)

    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.5,
        tooltip=f"{row['name']} ({row['capacity']} T/h)",
    ).add_to(m)

    # Capacity label inside circle
    folium.map.Marker(
        [row["lat"], row["lon"]],
        icon=folium.DivIcon(
            html=f"""
            <div style="
                font-size:10pt;
                font-weight:bold;
                color:white;
                text-align:center;
                transform:translate(-30%, -0%);
            ">{row['capacity']}</div>
            """
        ),
    ).add_to(m)

    # Always-visible name label (controlled by toggle)
    if show_labels:
        name_width = min(len(row["name"]) * 8 + 40, 500)
        folium.map.Marker(
            [row["lat"], row["lon"]],
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    display:inline-block;
                    background-color:rgba(255,255,255,0.85);
                    border-radius:6px;
                    padding:3px 8px;
                    border:1px solid #666;
                    font-size:10pt;
                    font-weight:400;
                    color:{get_color(row['supplier'])};
                    width:fit-content;
                    max-width:{name_width}px;
                    white-space:nowrap;
                    box-shadow:0px 1px 2px rgba(0,0,0,0.2);
                    transform:translate(30px,-20px);
                ">
                    {row['name']}
                </div>
                """,
            ),
        ).add_to(m)


# --- Display Map ---
st.markdown(
    """
    <style>
    /* Expand map container to fill page */
    .main > div {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    iframe {
        height: 90vh !important;  /* fill 90% of viewport height */
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st_data = st_folium(m, width=None, height=800)

# --- 1. Update plant info when clicked ---
if st_data and st_data.get("last_object_clicked"):
    clicked = st_data["last_object_clicked"]
    lat, lon = clicked["lat"], clicked["lng"]
    
    # Find nearest plant based on Euclidean distance
    # We use df.loc to ensure we get the specific row object
    dist = (df["lat"] - lat)**2 + (df["lon"] - lon)**2
    plant = df.loc[dist.idxmin()]

    # --- 2. Safe Data Formatting ---
    # Determine Supplier Color
    #supplier_color = "#067432" if "Nhat Ban" in str(plant["supplier"]) else "#ffe0b2"
    
    # Handle 'Product' Display Logic safely
    # We check if the value is NaN. If so, show text; otherwise, format the number.
    raw_product = plant['product']
    if pd.isna(raw_product):
        product_display = "To be invested"
    else:
        # Formats as 1,000 T/year
        product_display = f"{int(raw_product):,} T/year"

    # --- 3. Render HTML ---
    info_placeholder.markdown(
        f"""
        <div style="font-family: sans-serif;">
            <h3>🏭 {plant['name']}</h3>
            <ul>
                <li><b>Supplier:</b> {plant['supplier']}</li>
                <li><b>Capacity:</b> 
                    <span style="background-color:#F8D7DA; color:#B22222; padding:2px 8px; border-radius:10px; font-weight:bold;">
                        {plant['capacity']:,} T/h
                    </span>
                </li>
                <li><b>Year:</b> {plant['year']}</li>
                <li><b>Product:</b> {product_display}</li>
                <li><b>Note:</b> {plant['note']}</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

