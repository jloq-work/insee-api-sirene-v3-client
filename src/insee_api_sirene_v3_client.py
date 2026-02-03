
from .config import API_BASE_URL, HEADERS

# =========================
# REQUÊTE UNITAIRE 
# =========================
def requete_unitaire(endpoint: str,item_id: str) -> Dict:
    """
    Récupère un objet unique via son identifiant
    """
    url = f"{API_BASE_URL}/{endpoint}/{item_id}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    print("URL envoyée :",response.request.url)
    response.raise_for_status()
    return response.json()

# ======================================================================================================
# Préparation requête multi-critères: normalisation des paramètres de type date formulés dans le query q
# ======================================================================================================

DATE_REGEX = re.compile(r'(?<!")\b\d{4}-\d{2}-\d{2}\b(?!")')
MOIS_REGEX = re.compile(r'\b(\d{4})-(\d{2})\b')

def normaliser_q(q: str) -> str:
    """Nettoie la syntaxe de q (espaces, opérateurs)."""
    q = q.strip()
    q = re.sub(r"\s+(AND|OR|NOT)\s+", r" \1 ", q, flags=re.IGNORECASE)
    q = re.sub(r"\s+", " ", q)
    return q

def normaliser_dates_dans_q(q: str) -> str:
    """Ajoute des guillemets aux dates complètes YYYY-MM-DD"""
    q = DATE_REGEX.sub(r'"\g<0>"', q)
    # Optionnel : transformer YYYY-MM en intervalle du mois
    def repl(match):
        annee, mois = match.groups()
        return f'[{annee}-{mois}-01 TO {annee}-{mois}-31]'
    q = MOIS_REGEX.sub(repl, q)
    return q

def valider_q(q: str) -> None:
    """Validation simple de la syntaxe q."""
    if q.count("(") != q.count(")"):
        raise ValueError("q invalide : parenthèses non équilibrées")
    if re.match(r"^(AND|OR|NOT)\b", q):
        raise ValueError("q invalide : opérateur en début")
    if re.search(r"\b(AND|OR|NOT)$", q):
        raise ValueError("q invalide : opérateur en fin")
    if re.search(r"\b(AND|OR|NOT)\s+(AND|OR|NOT)\b", q):
        raise ValueError("q invalide : opérateurs consécutifs")

# ===========================================
# REQUÊTE MULTI-CRITÈRES UL et ETABLISSEMENTS
# ===========================================
def requete_multi_criteres(
    endpoint: str = "siret",
    q: Optional[str] = None,
    champs: Optional[str] = None,
    tri: Optional[str] = None,
    nombre: int = 1000,
    max_rows: Optional[int] = None,
    retry_delay: float = 1.0,
    max_retries: int = 5
) -> tuple[pd.DataFrame, dict]:
    """
    Requête multi-critères INSEE Sirene :
    - pagination par curseur (désactivée si inutile)
    - gestion 404 / 429
    - normalisation des dates
    - limite max_rows
    - retour DataFrame + header
    """

    # plafond API
    if nombre > 1000:
        nombre = 1000

    # racine JSON selon endpoint
    if endpoint == "siret":
        racine = "etablissements"
    elif endpoint == "siren":
        racine = "unitesLegales"
    else:
        raise ValueError("endpoint doit être 'siret' ou 'siren'")

    # normalisation / validation de q
    if q:
        q = normaliser_dates_dans_q(q)
        valider_q(q)

    curseur = "*"
    all_results = []
    header_global = {}
    first_page = True  # 👈 flag clé

    while True:
        params = {k: v for k, v in {
            "q": q,
            "champs": champs,
            "tri": tri,
            "nombre": nombre,
            "curseur": curseur
        }.items() if v is not None}

        url = f"{API_BASE_URL}/{endpoint}"

        # retry sur 429
        for _ in range(max_retries):
            response = requests.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=10
            )
            if response.status_code == 429:
                time.sleep(retry_delay)
            else:
                break
        else:
            raise RuntimeError("Rate limit (429) dépassé")

        if response.status_code == 404:
            break

        response.raise_for_status()
        data = response.json()

        header = data.get("header", {})
        header_global = header

        batch = data.get(racine, [])
        all_results.extend(batch)

        total = header.get("total", 0)

        # ✅ CAS CRITIQUE : une seule page → PAS de pagination
        if first_page and total <= nombre:
            break

        first_page = False

        # limite max_rows
        if max_rows and len(all_results) >= max_rows:
            all_results = all_results[:max_rows]
            break

        # pagination normale
        curseur = header.get("curseurSuivant")
        if not curseur:
            break

        time.sleep(retry_delay)

    df = pd.json_normalize(all_results) if all_results else pd.DataFrame()
    return df, header_global
