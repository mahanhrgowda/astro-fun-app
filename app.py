# app.py
import streamlit as st
import math
import datetime
import zoneinfo
import random

# Julian Date calculation
def julian_date(year, month, day, hour=0, minute=0, second=0):
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month
    
    if year < 1582 or (year == 1582 and (month < 10 or (month == 10 and day < 15))):
        B = 0
    else:
        A = math.floor(yearp / 100)
        B = 2 - A + math.floor(A / 4)
    
    C = math.floor(365.25 * (yearp + 4716))
    D = math.floor(30.6001 * (monthp + 1))
    jd = B + day + C + D - 1524.5
    jd += (hour + minute / 60.0 + second / 3600.0) / 24.0
    return jd

# Calculate Sun's ecliptic longitude
def calculate_sun_longitude(d):
    w = 282.9404 + 4.70935e-5 * d
    e = 0.016709 - 1.151e-9 * d
    M = (356.0470 + 0.9856002585 * d) % 360
    Mrad = math.radians(M)
    E = M + math.degrees(e * math.sin(Mrad) * (1.0 + e * math.cos(Mrad)))
    Erad = math.radians(E)
    xv = math.cos(Erad) - e
    yv = math.sin(Erad) * math.sqrt(1.0 - e*e)
    v = math.degrees(math.atan2(yv, xv))
    lonsun = (v + w) % 360
    return lonsun

# Improved Moon's ecliptic longitude calculation
def calculate_moon_longitude(d):
    T = d / 36525.0
    L0 = 218.31617 + 481267.88088 * T - 4.06 * T**2 / 3600.0
    M = 134.96292 + 477198.86753 * T + 33.25 * T**2 / 3600.0
    MSun = 357.52543 + 35999.04944 * T - 0.58 * T**2 / 3600.0
    F = 93.27283 + 483202.01873 * T - 11.56 * T**2 / 3600.0
    D = 297.85027 + 445267.11135 * T - 5.15 * T**2 / 3600.0

    Delta = (22640 * math.sin(math.radians(M)) 
             + 769 * math.sin(math.radians(2 * M)) 
             - 4586 * math.sin(math.radians(M - 2 * D)) 
             + 2370 * math.sin(math.radians(2 * D)) 
             - 668 * math.sin(math.radians(MSun)) 
             - 412 * math.sin(math.radians(2 * F)) 
             - 125 * math.sin(math.radians(D)) 
             - 212 * math.sin(math.radians(2 * M - 2 * D)) 
             - 206 * math.sin(math.radians(M + MSun - 2 * D)) 
             + 192 * math.sin(math.radians(M + 2 * D)) 
             - 165 * math.sin(math.radians(MSun - 2 * D)) 
             + 148 * math.sin(math.radians(L0 - MSun)) 
             - 110 * math.sin(math.radians(M + MSun)) 
             - 55 * math.sin(math.radians(2 * F - 2 * D))) / 3600.0

    lonecl = (L0 + Delta) % 360
    return lonecl

# Lahiri Ayanamsa approximation
def calculate_ayanamsa(jd):
    base_ayan = 23.853  # for J2000
    rate_per_year = 50.2719 / 3600  # degrees per year
    years = (jd - 2451545.0) / 365.25
    ayan = base_ayan + years * rate_per_year
    return ayan

def calculate_ascendant(jd, lat, lon):
    d = jd - 2451545.0
    eps = 23.439281 - 0.0000004 * d
    gmst = (280.46061837 + 360.98564736629 * d) % 360
    lst = (gmst + lon + 90) % 360  # Add 90 for adjustment
    lst_rad = math.radians(lst)
    eps_rad = math.radians(eps)
    lat_rad = math.radians(lat)
    y = math.sin(lst_rad)
    x = math.cos(lst_rad) * math.cos(eps_rad) - math.sin(eps_rad) * math.tan(lat_rad)
    asc_trop = math.degrees(math.atan2(y, x))
    if asc_trop < 0:
        asc_trop += 360
    return asc_trop

# Descriptions for Sun, Moon, Ascendant based on Rashi
descriptions = {
    "Mesha": {
        "sun": "Your soul ignites as an energetic pioneer, fueling bold leadership and vitality! 🌞🚀⚡",
        "moon": "Your mind races with pioneering energy, emotionally charged and impulsive! 🌙🔥🏃‍♂️",
        "asc": "Your personality bursts forth as a fiery pioneer, appearing dynamic and trailblazing! ⬆️🦸‍♂️💥"
    },
    "Vrishabha": {
        "sun": "Your soul grounds as a patient builder, embodying steady strength and endurance! 🌞🏰🌱",
        "moon": "Your mind nurtures with building patience, emotionally stable and sensual! 🌙🛡️🍃",
        "asc": "Your personality presents as a reliable builder, looking calm and materially focused! ⬆️🧱🌿"
    },
    "Mithuna": {
        "sun": "Your soul communicates as a curious explorer, vitalizing intellect and adaptability! 🌞🗣️🔎",
        "moon": "Your mind buzzes with curious communication, emotionally versatile and witty! 🌙💡🌀",
        "asc": "Your personality shines as a social communicator, appearing quick-witted and engaging! ⬆️🎭🌟"
    },
    "Karka": {
        "sun": "Your soul protects as a nurturing guardian, radiating emotional depth and care! 🌞🏡❤️",
        "moon": "Your mind flows with protective nurturing, intuitively sensitive and moody! 🌙🛡️🌊",
        "asc": "Your personality emerges as a caring protector, looking empathetic and home-loving! ⬆️🤗💙"
    },
    "Simha": {
        "sun": "Your soul roars as a confident leader, embodying royal charisma and creativity! 🌞👑🌟",
        "moon": "Your mind leads with confident pride, emotionally dramatic and generous! 🌙🦁🎭",
        "asc": "Your personality commands as a bold leader, appearing sunny and authoritative! ⬆️🏆🔥"
    },
    "Kanya": {
        "sun": "Your soul analyzes as a perfectionist, vitalizing precision and service! 🌞📊🔍",
        "moon": "Your mind critiques with analytical detail, emotionally practical and worrisome! 🌙🧠🛠️",
        "asc": "Your personality details as a meticulous helper, looking organized and humble! ⬆️📋🌿"
    },
    "Tula": {
        "sun": "Your soul balances as a diplomatic harmonizer, radiating fairness and partnerships! 🌞⚖️💕",
        "moon": "Your mind seeks harmony diplomatically, emotionally relational and indecisive! 🌙🤝❤️",
        "asc": "Your personality charms as a graceful mediator, appearing elegant and social! ⬆️🌹🕊️"
    },
    "Vrishchika": {
        "sun": "Your soul transforms intensely, embodying depth, power, and resilience! 🌞🦂🔥",
        "moon": "Your mind probes with intense emotions, intuitively secretive and passionate! 🌙🕵️‍♂️🌊",
        "asc": "Your personality magnetizes as a mysterious transformer, looking intense and probing! ⬆️🔮💥"
    },
    "Dhanu": {
        "sun": "Your soul adventures as a philosopher, vitalizing optimism and exploration! 🌞🏹📜",
        "moon": "Your mind wanders philosophically, emotionally free-spirited and blunt! 🌙🧭😊",
        "asc": "Your personality expands as an enthusiastic seeker, appearing jovial and wise! ⬆️🌍🔥"
    },
    "Makara": {
        "sun": "Your soul achieves with discipline, embodying ambition and responsibility! 🌞🏔️🏆",
        "moon": "Your mind structures with disciplined caution, emotionally reserved and pragmatic! 🌙🛡️⏳",
        "asc": "Your personality climbs as a steadfast achiever, looking serious and determined! ⬆️🧗‍♂️🌿"
    },
    "Kumbha": {
        "sun": "Your soul innovates as a visionary, radiating uniqueness and humanitarianism! 🌞💡🌐",
        "moon": "Your mind rebels with innovative ideas, emotionally detached and eccentric! 🌙🤖🌀",
        "asc": "Your personality networks as a forward-thinker, appearing unconventional and friendly! ⬆️🌟🤝"
    },
    "Meena": {
        "sun": "Your soul dreams compassionately, embodying spirituality and empathy! 🌞🌊✨",
        "moon": "Your mind imagines with dreamy intuition, emotionally sensitive and escapist! 🌙🔮💭",
        "asc": "Your personality flows as a mystical dreamer, looking gentle and artistic! ⬆️🧜‍♀️🌈"
    }
}

# Scientific explanations for string types
string_descriptions = {
    "Type I": "Type I string theory is a 10-dimensional supersymmetric theory with unoriented open and closed strings, featuring the SO(32) gauge group, anomaly cancellation via Green-Schwarz mechanism, and related to type IIB by orientifold. 📐🔗",
    "Type IIA": "Type IIA string theory is a non-chiral 10-dimensional superstring theory with (1,1) supersymmetry, low-energy limit type IIA supergravity, equivalent to M-theory compactified on a circle, T-dual to type IIB. 🔄🌌",
    "Type IIB": "Type IIB string theory is a chiral 10-dimensional superstring theory with (2,0) supersymmetry, features S-duality, low-energy type IIB supergravity, central in AdS/CFT correspondence. 🌀🔄",
    "Heterotic SO(32)": "Heterotic SO(32) string theory combines 26D bosonic left-movers and 10D super right-movers, compactified to 10D with SO(32) gauge group, anomaly-free, S-dual to type I. ⚡🔗",
    "Heterotic E8×E8": "Heterotic E8×E8 string theory is a 10D hybrid superstring with E8×E8 gauge group, favored for particle phenomenology due to potential embedding of Standard Model gauge groups. 🌟🔬"
}

# Main app
st.title("Vedic Astrology Fun Descriptor by Mahan H R Gowda")

birth_date = st.date_input("Birth Date", min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31))
birth_time = st.time_input("Birth Time (Local)", step=datetime.timedelta(minutes=1))
timezones = sorted(zoneinfo.available_timezones())
timezone = st.selectbox("Timezone", timezones, index=timezones.index("UTC") if "UTC" in timezones else 0)
birth_lat = st.number_input("Birth Latitude (degrees, positive for North, negative for South)", min_value=-90.0, max_value=90.0, value=0.0)
birth_lon = st.number_input("Birth Longitude (degrees, positive for East, negative for West)", min_value=-180.0, max_value=180.0, value=0.0)

if st.button("Generate Description"):
    local_dt = datetime.datetime.combine(birth_date, birth_time)
    local_tz = zoneinfo.ZoneInfo(timezone)
    local_dt = local_dt.replace(tzinfo=local_tz)
    utc_dt = local_dt.astimezone(zoneinfo.ZoneInfo("UTC"))
    year, month, day = utc_dt.year, utc_dt.month, utc_dt.day
    hour, minute = utc_dt.hour, utc_dt.minute
    jd = julian_date(year, month, day, hour, minute)
    d = jd - 2451545.0
    
    sun_long = calculate_sun_longitude(d)
    moon_long = calculate_moon_longitude(d)
    ayan = calculate_ayanamsa(jd)
    
    sid_moon = (moon_long - ayan) % 360
    
    nak_num = math.floor(sid_moon / (360 / 27))
    nak_rem = sid_moon % (360 / 27)
    pada = math.floor(nak_rem / (360 / 108)) + 1
    
    rashi_num = math.floor(sid_moon / 30)
    
    elong = (moon_long - sun_long) % 360
    paksha = "Shukla" if elong < 180 else "Krishna"
    
    nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purvaphalguni", "Uttaraphalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshta", "Mula", "Purvashada", "Uttarashada", "Shravana", "Dhanishta", "Shatabhisha", "Purvabhadra", "Uttarabhadra", "Revati"]
    nak_name = nakshatras[nak_num]
    
    rashis = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
    rashi_name = rashis[rashi_num]
    
    rashi_elements = {
        "Mesha": "Fire", "Vrishabha": "Earth", "Mithuna": "Air", "Karka": "Water",
        "Simha": "Fire", "Kanya": "Earth", "Tula": "Air", "Vrishchika": "Water",
        "Dhanu": "Fire", "Makara": "Earth", "Kumbha": "Air", "Meena": "Water"
    }
    
    shukla_birds = {
        "Vulture": ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira"],
        "Owl": ["Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purvaphalguni"],
        "Crow": ["Uttaraphalguni", "Hasta", "Chitra", "Swati", "Vishakha"],
        "Cock": ["Anuradha", "Jyeshta", "Mula", "Purvashada", "Uttarashada"],
        "Peacock": ["Shravana", "Dhanishta", "Shatabhisha", "Purvabhadra", "Uttarabhadra", "Revati"]
    }
    krishna_birds = {
        "Peacock": ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira"],
        "Cock": ["Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purvaphalguni"],
        "Crow": ["Uttaraphalguni", "Hasta", "Chitra", "Swati", "Vishakha"],
        "Owl": ["Anuradha", "Jyeshta", "Mula", "Purvashada", "Uttarashada"],
        "Vulture": ["Shravana", "Dhanishta", "Shatabhisha", "Purvabhadra", "Uttarabhadra", "Revati"]
    }
    
    ruling_bird = None
    if paksha == "Shukla":
        for bird, naks in shukla_birds.items():
            if nak_name in naks:
                ruling_bird = bird
                break
    else:
        for bird, naks in krishna_birds.items():
            if nak_name in naks:
                ruling_bird = bird
                break
    
    bird_to_sanskrit = {
        "Vulture": "Gṛdhra",
        "Owl": "Ulūka",
        "Crow": "Kāka",
        "Cock": "Kukkuṭa",
        "Peacock": "Mayūra"
    }
    
    bird_to_element = {
        "Vulture": "Fire",
        "Owl": "Water",
        "Crow": "Earth",
        "Cock": "Air",
        "Peacock": "Ether"
    }
    element_to_string = {
        "Fire": "Type I",
        "Water": "Type IIA",
        "Air": "Type IIB",
        "Earth": "Heterotic SO(32)",
        "Ether": "Heterotic E8×E8"
    }
    
    bird_descriptions = {
        "Vulture": "In Pancha Pakshi Shastra, the Vulture (Gṛdhra) symbolizes Fire 🔥, representing transformation, power, and leadership. Mythically linked to Garuda, Vishnu's vehicle, it embodies swift action and protection. It engages in activities like Ruling (strongest) to Dying (weakest), influencing auspicious timings. Linked to Type I strings, it vibrates with dynamic, open-closed modes, enhancing fiery Rashis like Mesha with passionate drive! 🦅⚡",
        "Owl": "The Owl (Ulūka) in Pancha Pakshi stands for Water 💧, signifying intuition, wisdom, and adaptability. Associated with Lakshmi's night vigilance, it's a harbinger of deep knowledge. Cycles through Eating, Walking, etc., for daily predictions. Tied to Type IIA strings, it flows in balanced, non-chiral dimensions, amplifying watery traits in Nakshatras like Pushya with emotional depth! 🦉🌊🔮",
        "Crow": "Crow (Kāka) represents Earth 🌍, denoting practicality, intelligence, and ancestral connections. As Shani's messenger, it signifies resourcefulness and caution. Its states (Ruling to Sleeping) guide mundane tasks. Connected to Heterotic SO(32) strings, grounding hybrid symmetries, it stabilizes earthy Kanya Rashi with wise, analytical energy! 🐦🌿🧠",
        "Cock": "The Cock (Kukkuṭa) embodies Air 🌬️, symbolizing alertness, courage, and communication. Linked to dawn and warriors like Kartikeya, it crows awakening and vigilance. Activities cycle for timing battles or starts. Aligned with Type IIB strings, chiral and self-dual, it boosts airy Mithuna with swift, intellectual winds! 🐔☁️🏹",
        "Peacock": "Peacock (Mayūra) signifies Ether ✨, illustrating expansion, beauty, and spirituality. Vehicle of Kartikeya, it dances in royal harmony, representing boundless space. From Ruling (peak creativity) to Dying, it aids spiritual pursuits. Mapped to Heterotic E8×E8 strings, unifying grand symmetries, it elevates ethereal Meena with cosmic visions! 🦚🌌💫"
    }
    
    rashi_traits = {
        "Mesha": "energetic pioneer 🔥🚀",
        "Vrishabha": "patient builder 🌱🏰",
        "Mithuna": "curious communicator 🗣️🌟",
        "Karka": "nurturing protector 🏡❤️",
        "Simha": "confident leader 👑🌞",
        "Kanya": "analytical perfectionist 📊🔍",
        "Tula": "diplomatic harmonizer ⚖️💕",
        "Vrishchika": "intense transformer 🦂🔥",
        "Dhanu": "adventurous philosopher 🏹📜",
        "Makara": "disciplined achiever 🏔️🏆",
        "Kumbha": "innovative visionary 💡🌐",
        "Meena": "compassionate dreamer 🌊✨"
    }
    
    nak_traits = {
        "Ashwini": "swift healer 🏇💨",
        "Bharani": "creative warrior ⚔️🎨",
        "Krittika": "fiery critic 🔥🗡️",
        "Rohini": "artistic nurturer 🌸🍼",
        "Mrigashira": "curious explorer 🦌🔎",
        "Ardra": "stormy intellectual 🌩️🧠",
        "Punarvasu": "renewing archer 🏹🔄",
        "Pushya": "protective guru 🌟🛡️",
        "Ashlesha": "intuitive serpent 🐍🔮",
        "Magha": "regal ancestor 👑🕊️",
        "Purvaphalguni": "loving performer ❤️🎭",
        "Uttaraphalguni": "helpful analyst 🤝📈",
        "Hasta": "skillful artisan 🖐️🛠️",
        "Chitra": "charismatic architect 🌟🏗️",
        "Swati": "independent diplomat ⚖️🌬️",
        "Vishakha": "ambitious goal-setter 🏆🔥",
        "Anuradha": "devoted friend 🤝❤️",
        "Jyeshta": "protective elder 🛡️👴",
        "Mula": "truth-seeking root 🌿🔍",
        "Purvashada": "invincible optimist 🏹😊",
        "Uttarashada": "enduring victor 🏆💪",
        "Shravana": "learning listener 👂📚",
        "Dhanishta": "musical networker 🎶🤝",
        "Shatabhisha": "healing mystic 🌟🧙",
        "Purvabhadra": "spiritual warrior ⚔️🙏",
        "Uttarabhadra": "wise supporter 🧠🤝",
        "Revati": "compassionate guide 🐟❤️"
    }
    
    fun_phrases = {
        "Fire": ["ignite passions like a blazing star! 🔥🌟🦅", "transform challenges into victories with fiery zeal! ⚡🏆🔥", "soar high with unstoppable energy! 🚀🔥🕊️"],
        "Water": ["flow through life with deep intuition! 💧🌊🦉", "adapt and nurture like ocean waves! 🌊❤️💙", "dive into emotions with graceful wisdom! 🏊‍♂️🔮💧"],
        "Earth": ["build stable foundations with earthy wisdom! 🌍🏗️🐦", "grow steadily like ancient trees! 🌳💪🟫", "caw out practical solutions grounded in reality! 🐦🛠️🌿"],
        "Air": ["dance freely with intellectual winds! 🌬️💃🐔", "crow ideas that soar through the skies! 🐔☁️🧠", "breeze through challenges with swift agility! 🌪️🏃‍♂️🌬️"],
        "Ether": ["expand infinitely like cosmic space! ✨🌌🦚", "harmonize universes with ethereal grace! 🔮💫🌠", "peacock your boundless potential! 🦚🌈✨"]
    }
    
    element = bird_to_element.get(ruling_bird, "Unknown")
    string_type = element_to_string.get(element, "Unknown")
    sanskrit_name = bird_to_sanskrit.get(ruling_bird, "Unknown")
    bird_desc = bird_descriptions.get(ruling_bird, "This bird embodies cosmic mysteries! 🌌")
    r_trait = rashi_traits.get(rashi_name, "mysterious soul 🌌")
    n_trait = nak_traits.get(nak_name, "cosmic wanderer ⭐")
    fun_phrase = random.choice(fun_phrases.get(element, ["embody the universe's mysteries! 🌌🔮✨"]))
    
    dynamic_desc = f"You are a {r_trait} infused with {n_trait} in Pada {pada} precision ⏳, guided by {ruling_bird} ({sanskrit_name}) of {element} vibes like {string_type} strings vibrating through reality! {fun_phrase}"
    
    # Calculate Sun sign and Ascendant sign
    sid_sun = (sun_long - ayan) % 360
    sun_rashi_num = math.floor(sid_sun / 30)
    sun_rashi_name = rashis[sun_rashi_num]

    asc_trop = calculate_ascendant(jd, birth_lat, birth_lon)
    sid_asc = (asc_trop - ayan) % 360
    asc_rashi_num = math.floor(sid_asc / 30)
    asc_rashi_name = rashis[asc_rashi_num]

    # Get descriptions
    sun_desc = descriptions.get(sun_rashi_name, {"sun": "Unknown soul description 🌌"})["sun"]
    moon_desc = descriptions.get(rashi_name, {"moon": "Unknown mind description 🌌"})["moon"]
    asc_desc = descriptions.get(asc_rashi_name, {"asc": "Unknown personality description 🌌"})["asc"]
    string_desc = string_descriptions.get(string_type, "Unknown string type in scientific context 🔬")

    st.write(f"🌟 **Your Vedic Astrology Snapshot:** 🌟")
    st.write(f"- **Sun Sign:** {sun_rashi_name} (Element: {rashi_elements.get(sun_rashi_name, 'Unknown')}) - {sun_desc}")
    st.write(f"- **Moon Sign:** {rashi_name} (Element: {rashi_elements.get(rashi_name, 'Unknown')}) - {moon_desc}")
    st.write(f"- **Ascendant Sign:** {asc_rashi_name} (Element: {rashi_elements.get(asc_rashi_name, 'Unknown')}) - {asc_desc}")
    st.write(f"- **Nakshatra:** {nak_name}, Pada {pada}")
    st.write(f"- **Paksha:** {paksha}")
    st.write(f"- **Ruling Bird (Panchabhuta):** {ruling_bird} ({sanskrit_name}) ({element})")
    st.write(f"- **Linked String Type:** {string_type} - {string_desc}")
    st.write(f"**Dynamic Fun Description:** {dynamic_desc}")
    st.write(f"**Bird Meaning in Context:** {bird_desc}")
    
    with st.expander("Significance of Sun, Moon, and Ascendant Signs"):
        st.write("""
        - **Sun Sign (Surya Rashi)** 🌞: Represents your core soul (Atma), ego, vitality, father, authority, and career path. It embodies your inner strength and life purpose, shining light on your leadership and societal role.
        - **Moon Sign (Chandra Rashi)** 🌙: Governs your mind (Manas), emotions, intuition, mother, home life, and inner comfort. It's central in Vedic astrology for daily predictions and personality, reflecting how you process feelings and nurture others.
        - **Ascendant Sign (Lagna)** ⬆️: Defines your physical body, appearance, health, self-image, and outward personality—how the world perceives you and your approach to life challenges.
        These three form the "Big Three" in Vedic charts, blending to create your holistic persona. The Sun provides the "why" (purpose) 🔥, Moon the "how" (emotions) 💧, and Ascendant the "what" (presentation) 🌍. Their interplay accounts for unique traits; e.g., a fiery Sun with watery Moon might mean passionate drive tempered by empathy, presented through an earthy Ascendant as grounded ambition.
        """)
    
    with st.expander("Meanings of All Birds in Pancha Pakshi Shastra"):
        for bird, desc in bird_descriptions.items():
            st.write(f"- **{bird}:** {desc}")
    
    with st.expander("Scientific Context of All String Types"):
        for string_type, desc in string_descriptions.items():
            st.write(f"- **{string_type}:** {desc}")