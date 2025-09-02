import string
import secrets
import streamlit as st
import math

st.set_page_config(page_title="Password Generator", page_icon="🔐", layout="centered")

st.title("🔐 Secure Password Generator")
st.write("Generate strong passwords with customizable options")

# Custom CSS for better styling
st.markdown("""
    <style>
    .tip-text { 
        font-size: 0.9rem; 
        color: #666; 
        margin-top: 5px;
    }
    .strength-indicator {
        padding: 8px;
        border-radius: 4px;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
    }
    .strong { background-color: #d4edda; color: #155724; }
    .medium { background-color: #fff3cd; color: #856404; }
    .weak { background-color: #f8d7da; color: #721c24; }
    </style>
""", unsafe_allow_html=True)

# Preset configurations
presets = {
    "High Security": {"len": 16, "lower": True, "upper": True, "digits": True, "symbols": True},
    "Balanced": {"len": 12, "lower": True, "upper": True, "digits": True, "symbols": False},
    "Basic": {"len": 10, "lower": True, "upper": False, "digits": True, "symbols": False},
    "Custom": {"len": 14, "lower": True, "upper": True, "digits": True, "symbols": True}
}

selected_preset = st.selectbox("Choose a preset:", list(presets.keys()))
preset_config = presets[selected_preset]

# Password length
pwd_length = st.slider("Password Length",
                       min_value=4,
                       max_value=50,
                       value=preset_config["len"])

st.subheader("Character Types")
col1, col2 = st.columns(2)

with col1:
    include_lowercase = st.checkbox("Lowercase letters (a-z)",
                                    value=preset_config["lower"],
                                    disabled=(selected_preset != "Custom"))
    include_numbers = st.checkbox("Numbers (0-9)",
                                  value=preset_config["digits"],
                                  disabled=(selected_preset != "Custom"))

with col2:
    include_uppercase = st.checkbox("Uppercase letters (A-Z)",
                                    value=preset_config["upper"],
                                    disabled=(selected_preset != "Custom"))
    include_symbols = st.checkbox("Special characters (!@#$...)",
                                  value=preset_config["symbols"],
                                  disabled=(selected_preset != "Custom"))

st.subheader("Additional Options")
avoid_similar = st.checkbox("Avoid similar-looking characters (I, l, 1, O, 0, o)", value=True)
simple_symbols_only = st.checkbox("Use only common symbols (!@#$%&*)", value=False)

def build_character_pool(lowercase: bool, uppercase: bool, numbers: bool, symbols: bool,
                         avoid_confusing: bool = False, simple_symbols: bool = False):
    """Build the character sets selected by the user."""
    sets = []

    if lowercase:
        sets.append(set(string.ascii_lowercase))
    if uppercase:
        sets.append(set(string.ascii_uppercase))
    if numbers:
        sets.append(set(string.digits))
    if symbols:
        sets.append(set("!@#$%&*") if simple_symbols else set(string.punctuation))

    if avoid_confusing:
        confusing = set("Il1O0o")
        sets = [s - confusing for s in sets]

    # keep only non-empty sets
    return [s for s in sets if s]

def secure_shuffle(seq):
    """In-place Fisher–Yates shuffle using secrets for randomness."""
    # convert to list if needed
    a = list(seq)
    for i in range(len(a) - 1, 0, -1):
        j = secrets.randbelow(i + 1)  # 0..i inclusive
        a[i], a[j] = a[j], a[i]
    return a

def create_password(length: int, char_sets):
    """Generate a secure password with guaranteed character diversity."""
    if not char_sets:
        raise ValueError("You need to select at least one character type!")

    # Guard: make sure we can place at least one char from each selected set
    if length < len(char_sets):
        raise ValueError(f"Increase length to at least {len(char_sets)} to include all selected groups.")

    rng = secrets.SystemRandom()

    # Ensure one from each set
    password_chars = [rng.choice(tuple(s)) for s in char_sets]

    # Unified pool for remaining characters
    unified = set().union(*char_sets)
    if not unified:
        raise ValueError("No characters available with current settings!")

    unified_list = tuple(unified)
    while len(password_chars) < length:
        password_chars.append(rng.choice(unified_list))

    # Crypto-safe shuffle
    password_chars = secure_shuffle(password_chars)

    return ''.join(password_chars)

def estimate_entropy_bits(length: int, char_sets) -> float:
    """Rough theoretical entropy: length * log2(pool_size)."""
    pool_size = len(set().union(*char_sets)) if char_sets else 0
    if pool_size <= 1:
        return 0.0
    return length * math.log2(pool_size)

# Build character pool
char_pool = build_character_pool(
    include_lowercase,
    include_uppercase,
    include_numbers,
    include_symbols,
    avoid_similar,
    simple_symbols_only
)

if st.button("🎲 Generate Password", type="primary"):
    try:
        generated_pwd = create_password(pwd_length, char_pool)

        st.success("Password generated successfully!")
        st.code(generated_pwd, language=None)
        st.markdown('<div class="tip-text">💡 Click the copy button in the code box above to copy your password</div>',
                    unsafe_allow_html=True)

        # Strength indicator (rule-of-thumb + entropy)
        bits = estimate_entropy_bits(pwd_length, char_pool)
        if bits >= 90:
            strength = "Strong"
            css_class = "strong"
        elif bits >= 60:
            strength = "Medium"
            css_class = "medium"
        else:
            strength = "Weak"
            css_class = "weak"

        st.markdown(f'<div class="strength-indicator {css_class}">Password Strength: {strength} · ~{bits:.0f} bits</div>',
                    unsafe_allow_html=True)

    except ValueError as e:
        st.error(f"Error: {e}")

# Help section
with st.expander("ℹ️ Password Security Tips"):
    st.write("""
    **Creating Strong Passwords:**
    - Use at least 12 characters (16+ is better)
    - Include a mix of character types
    - Avoid dictionary words and personal information
    - Use unique passwords for each account
    - Consider using a password manager

    **Character Pool Size:**
    - Lowercase only: 26 characters
    - + Uppercase: 52 characters  
    - + Numbers: 62 characters
    - + Symbols: 90+ characters

    More character types = stronger password!
    """)
