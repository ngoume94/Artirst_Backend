"""
Script de test complet pour l'API Last.fm
Teste tous les endpoints avec gestion d'erreurs et affichage formaté
"""
import httpx
from typing import Optional, Dict, Any
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0

class Colors:
    """Codes couleurs pour l'affichage terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_section(title: str):
    """Affiche un titre de section"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_success(message: str):
    """Affiche un message de succès"""
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message: str):
    """Affiche un message d'erreur"""
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_info(message: str):
    """Affiche un message d'information"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.ENDC}")

def print_warning(message: str):
    """Affiche un avertissement"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def make_request(
    method: str,
    endpoint: str,
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    expected_status: int = 200
) -> Optional[Any]:
    """
    Effectue une requête HTTP et gère les erreurs
    
    Args:
        method: Méthode HTTP (GET, POST, PUT, DELETE)
        endpoint: Endpoint de l'API
        params: Paramètres de requête
        json_data: Données JSON pour POST/PUT
        expected_status: Code de statut attendu
    
    Returns:
        Réponse JSON ou None en cas d'erreur
    """
    url = f"{BASE_URL}{endpoint}"
    
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            if method == "GET":
                response = client.get(url, params=params)
            elif method == "POST":
                response = client.post(url, json=json_data, params=params)
            elif method == "PUT":
                response = client.put(url, json=json_data, params=params)
            elif method == "DELETE":
                response = client.delete(url, params=params)
            else:
                print_error(f"Méthode HTTP non supportée: {method}")
                return None
        
        if response.status_code == expected_status:
            print_success(f"{method} {endpoint} - Status: {response.status_code}")
            if response.status_code != 204:  # No Content
                return response.json()
            return {"success": True}
        else:
            print_error(f"{method} {endpoint} - Status: {response.status_code}")
            try:
                error_detail = response.json()
                print_info(f"Détails: {json.dumps(error_detail, indent=2)}")
            except:
                print_info(f"Réponse: {response.text}")
            return None
            
    except httpx.TimeoutException:
        print_error(f"Timeout lors de la requête vers {url}")
        return None
    except httpx.ConnectError:
        print_error(f"Impossible de se connecter à {url}")
        print_warning("Vérifiez que le serveur est démarré (python main.py)")
        return None
    except Exception as e:
        print_error(f"Erreur: {str(e)}")
        return None

def test_health_check():
    """Teste le health check de l'API"""
    print_section("0. HEALTH CHECK")
    
    result = make_request("GET", "/health")
    if result:
        print_info(f"Status: {result.get('status')}")
        print_info(f"Database: {result.get('database')}")
    
    root = make_request("GET", "/")
    if root:
        print_info(f"Version: {root.get('version')}")

def test_artists_crud():
    """Teste les opérations CRUD sur les artistes"""
    print_section("1. ARTISTES - CRUD")
    
    # 1. Lister les artistes (pagination)
    print(f"{Colors.BOLD}1.1. Liste des artistes (5 premiers){Colors.ENDC}")
    result = make_request("GET", "/artists/", params={"skip": 0, "limit": 5})
    if result:
        print_info(f"Total: {result.get('total')} artistes")
        print_info(f"Récupérés: {len(result.get('items', []))} artistes")
        for artist in result.get('items', [])[:3]:
            print(f"  - {artist.get('name')} (ID: {artist.get('id')})")
    
    # 2. Rechercher par nom
    print(f"\n{Colors.BOLD}1.2. Recherche d'artistes par nom{Colors.ENDC}")
    result = make_request("GET", "/artists/", params={"name": "metallica", "limit": 3})
    if result:
        print_info(f"Trouvé: {len(result.get('items', []))} artiste(s)")
        for artist in result.get('items', []):
            print(f"  - {artist.get('name')}")
    
    # 3. Détails d'un artiste
    print(f"\n{Colors.BOLD}1.3. Détails d'un artiste spécifique{Colors.ENDC}")
    result = make_request("GET", "/artists/1")
    if result:
        print_info(f"Artiste: {result.get('name')}")
        print_info(f"Total écoutes: {result.get('total_listens', 0):,}")
        print_info(f"Auditeurs: {result.get('listener_count', 0)}")
        top_tags = result.get('top_tags', [])
        if top_tags:
            print_info(f"Top tags: {', '.join([t['tagValue'] for t in top_tags[:3]])}")
    
    # 4. Créer un nouvel artiste
    print(f"\n{Colors.BOLD}1.4. Création d'un nouvel artiste{Colors.ENDC}")
    new_artist = {
        "name": "Test Artist API",
        "url": "https://www.last.fm/music/test",
        "pictureURL": "https://images.last.fm/test.jpg"
    }
    result = make_request("POST", "/artists/", json_data=new_artist, expected_status=201)
    artist_id = None
    if result:
        artist_id = result.get('id')
        print_info(f"Artiste créé avec l'ID: {artist_id}")
    
    # 5. Mettre à jour l'artiste
    if artist_id:
        print(f"\n{Colors.BOLD}1.5. Mise à jour de l'artiste{Colors.ENDC}")
        update_data = {"url": "https://www.last.fm/music/test-updated"}
        result = make_request("PUT", f"/artists/{artist_id}", json_data=update_data)
        if result:
            print_info(f"URL mise à jour: {result.get('url')}")
    
    # 6. Supprimer l'artiste
    if artist_id:
        print(f"\n{Colors.BOLD}1.6. Suppression de l'artiste{Colors.ENDC}")
        make_request("DELETE", f"/artists/{artist_id}", expected_status=204)
    
    # 7. Listeners d'un artiste
    print(f"\n{Colors.BOLD}1.7. Auditeurs d'un artiste{Colors.ENDC}")
    result = make_request("GET", "/artists/1/listeners", params={"limit": 3})
    if result:
        print_info(f"Top {len(result)} auditeurs:")
        for listener in result:
            print(f"  - User {listener['user']['userID']}: {listener['weight']} écoutes")
    
    # 8. Tags d'un artiste
    print(f"\n{Colors.BOLD}1.8. Tags d'un artiste{Colors.ENDC}")
    result = make_request("GET", "/artists/1/tags", params={"limit": 5})
    if result:
        print_info(f"Tags:")
        for tag in result:
            print(f"  - {tag['tagValue']} ({tag['count']} fois)")

def test_users_crud():
    """Teste les opérations CRUD sur les utilisateurs"""
    print_section("2. UTILISATEURS - CRUD")
    
    # 1. Créer un utilisateur
    print(f"{Colors.BOLD}2.1. Création d'un utilisateur de test{Colors.ENDC}")
    test_user_id = 999999
    result = make_request("POST", "/users/", json_data={"userID": test_user_id}, expected_status=201)
    
    # 2. Lister les utilisateurs
    print(f"\n{Colors.BOLD}2.2. Liste des utilisateurs{Colors.ENDC}")
    result = make_request("GET", "/users/", params={"skip": 0, "limit": 5})
    if result:
        print_info(f"Total: {result.get('total')} utilisateurs")
        print_info(f"5 premiers IDs: {[u['userID'] for u in result.get('items', [])[:5]]}")
    
    # 3. Profil utilisateur
    print(f"\n{Colors.BOLD}2.3. Profil d'un utilisateur{Colors.ENDC}")
    result = make_request("GET", "/users/2")
    if result:
        print_info(f"UserID: {result.get('userID')}")
        print_info(f"Artistes écoutés: {result.get('artists_listened')}")
        print_info(f"Tags créés: {result.get('tags_created')}")
        print_info(f"Amis: {result.get('friends_count')}")
    
    # 4. Artistes écoutés par un utilisateur
    print(f"\n{Colors.BOLD}2.4. Top artistes d'un utilisateur{Colors.ENDC}")
    result = make_request("GET", "/users/2/artists", params={"limit": 5})
    if result:
        print_info(f"Top 5 artistes:")
        for item in result[:5]:
            print(f"  - {item['artist']['name']}: {item['weight']} écoutes")
    
    # 5. Amis d'un utilisateur
    print(f"\n{Colors.BOLD}2.5. Amis d'un utilisateur{Colors.ENDC}")
    result = make_request("GET", "/users/2/friends")
    if result:
        print_info(f"Nombre d'amis: {len(result)}")
        if result:
            print_info(f"Premiers amis: {result[:5]}")
    
    # 6. Recommandations
    print(f"\n{Colors.BOLD}2.6. Recommandations pour un utilisateur{Colors.ENDC}")
    result = make_request("GET", "/users/2/recommendations", params={"limit": 5})
    if result:
        print_info(f"Top 5 recommandations:")
        for rec in result[:5]:
            print(f"  - {rec['artist']['name']} (score: {rec['score']})")
    
    # 7. Supprimer l'utilisateur de test
    print(f"\n{Colors.BOLD}2.7. Suppression de l'utilisateur de test{Colors.ENDC}")
    make_request("DELETE", f"/users/{test_user_id}", expected_status=204)

def test_tags_crud():
    """Teste les opérations CRUD sur les tags"""
    print_section("3. TAGS - CRUD")
    
    # 1. Lister les tags
    print(f"{Colors.BOLD}3.1. Liste des tags{Colors.ENDC}")
    result = make_request("GET", "/tags/", params={"skip": 0, "limit": 10})
    if result:
        print_info(f"Total: {result.get('total')} tags")
        tags = result.get('items', [])[:5]
        print_info(f"5 premiers: {', '.join([t['tagValue'] for t in tags])}")
    
    # 2. Créer un tag
    print(f"\n{Colors.BOLD}3.2. Création d'un tag{Colors.ENDC}")
    result = make_request("POST", "/tags/", json_data={"tagValue": "test-api-tag"}, expected_status=201)
    tag_id = None
    if result:
        tag_id = result.get('tagID')
        print_info(f"Tag créé avec l'ID: {tag_id}")
    
    # 3. Détails d'un tag
    if tag_id:
        print(f"\n{Colors.BOLD}3.3. Détails du tag{Colors.ENDC}")
        result = make_request("GET", f"/tags/{tag_id}")
        if result:
            print_info(f"Tag: {result.get('tagValue')}")
            print_info(f"Utilisations: {result.get('usage_count')}")
    
    # 4. Mettre à jour le tag
    if tag_id:
        print(f"\n{Colors.BOLD}3.4. Mise à jour du tag{Colors.ENDC}")
        result = make_request("PUT", f"/tags/{tag_id}", json_data={"tagValue": "test-api-tag-updated"})
    
    # 5. Artistes avec ce tag
    print(f"\n{Colors.BOLD}3.5. Artistes avec le tag 'rock'{Colors.ENDC}")
    result = make_request("GET", "/tags/1/artists", params={"limit": 5})
    if result:
        print_info(f"Nombre d'artistes: {len(result)}")
        for artist in result[:3]:
            print(f"  - {artist.get('name')}")
    
    # 6. Supprimer le tag
    if tag_id:
        print(f"\n{Colors.BOLD}3.6. Suppression du tag{Colors.ENDC}")
        make_request("DELETE", f"/tags/{tag_id}", expected_status=204)

def test_listens():
    """Teste les opérations sur les écoutes"""
    print_section("4. ÉCOUTES (USER-ARTIST)")
    
    # 1. Créer une écoute
    print(f"{Colors.BOLD}4.1. Enregistrer une écoute{Colors.ENDC}")
    listen_data = {
        "userID": 2,
        "artistID": 1,
        "weight": 1000
    }
    result = make_request("POST", "/listens/", json_data=listen_data, expected_status=201)
    if result:
        print_info(f"Écoute enregistrée: User {result.get('userID')} -> Artist {result.get('artistID')}")
    
    # 2. Mettre à jour une écoute
    print(f"\n{Colors.BOLD}4.2. Mettre à jour le poids d'écoute{Colors.ENDC}")
    result = make_request("PUT", "/listens/2/1", json_data={"weight": 1500})
    if result:
        print_info(f"Nouveau poids: {result.get('weight')}")

def test_tagged_artists():
    """Teste les tags appliqués aux artistes"""
    print_section("5. TAGS APPLIQUÉS")
    
    # 1. Appliquer un tag
    print(f"{Colors.BOLD}5.1. Appliquer un tag à un artiste{Colors.ENDC}")
    tagged_data = {
        "userID": 2,
        "artistID": 1,
        "tagID": 1,
        "timestamp": int(datetime.now().timestamp() * 1000)
    }
    result = make_request("POST", "/tagged-artists/", json_data=tagged_data, expected_status=201)
    if result:
        print_info(f"Tag appliqué: User {result.get('userID')} -> Artist {result.get('artistID')}")
    
    # 2. Lister les tags appliqués
    print(f"\n{Colors.BOLD}5.2. Liste des tags appliqués{Colors.ENDC}")
    result = make_request("GET", "/tagged-artists/", params={"limit": 5})
    if result:
        print_info(f"Nombre de tags: {len(result)}")
        for item in result[:3]:
            print(f"  - {item['artist']['name']} -> {item['tag']['tagValue']}")
    
    # 3. Filtrer par artiste
    print(f"\n{Colors.BOLD}5.3. Tags pour un artiste spécifique{Colors.ENDC}")
    result = make_request("GET", "/tagged-artists/", params={"artist_id": 1, "limit": 5})
    if result:
        print_info(f"Tags pour l'artiste 1: {len(result)}")

def test_friendships():
    """Teste les relations d'amitié"""
    print_section("6. AMITIÉS")
    
    # 1. Créer une amitié
    print(f"{Colors.BOLD}6.1. Créer une amitié{Colors.ENDC}")
    friendship_data = {
        "userID": 2,
        "friendID": 3,
        "bidirectional": True
    }
    result = make_request("POST", "/friendships/", json_data=friendship_data, expected_status=201)
    if result:
        print_info(f"Amitié créée: {result.get('userID')} <-> {result.get('friendID')}")

def test_analytics():
    """Teste les endpoints analytiques"""
    print_section("7. ANALYTICS & STATISTIQUES")
    
    # 1. Statistiques globales
    print(f"{Colors.BOLD}7.1. Statistiques globales{Colors.ENDC}")
    result = make_request("GET", "/analytics/global")
    if result:
        print_info(f"Artistes: {result.get('total_artists'):,}")
        print_info(f"Utilisateurs: {result.get('total_users'):,}")
        print_info(f"Tags: {result.get('total_tags'):,}")
        print_info(f"Écoutes: {result.get('total_listens'):,}")
        print_info(f"Tags appliqués: {result.get('total_tagged'):,}")
        print_info(f"Amitiés: {result.get('total_friendships'):,}")
    
    # 2. Artistes populaires
    print(f"\n{Colors.BOLD}7.2. Top 5 artistes les plus populaires{Colors.ENDC}")
    result = make_request("GET", "/analytics/popular-artists", params={"limit": 5})
    if result:
        for i, artist in enumerate(result, 1):
            print(f"  {i}. {artist['name']}: {artist['total_weight']:,} écoutes")
    
    # 3. Tags populaires
    print(f"\n{Colors.BOLD}7.3. Top 5 tags les plus utilisés{Colors.ENDC}")
    result = make_request("GET", "/analytics/popular-tags", params={"limit": 5})
    if result:
        for i, tag in enumerate(result, 1):
            print(f"  {i}. {tag['tagValue']}: {tag['usage_count']} utilisations")
    
    # 4. Utilisateurs actifs
    print(f"\n{Colors.BOLD}7.4. Top 5 utilisateurs les plus actifs{Colors.ENDC}")
    result = make_request("GET", "/analytics/active-users", params={"limit": 5})
    if result:
        for i, user in enumerate(result, 1):
            print(f"  {i}. User {user['userID']}: {user['listen_count']} artistes")
    
    # 5. Utilisateurs similaires
    print(f"\n{Colors.BOLD}7.5. Utilisateurs similaires à l'utilisateur 2{Colors.ENDC}")
    result = make_request("GET", "/analytics/similar-users/2", params={"limit": 5})
    if result:
        for user in result[:3]:
            print(f"  - User {user['userID']}: {user['common_artists']} artistes en commun")

def test_search():
    """Teste les fonctionnalités de recherche"""
    print_section("8. RECHERCHE AVANCÉE")
    
    # 1. Recherche par tags multiples
    print(f"{Colors.BOLD}8.1. Recherche d'artistes avec plusieurs tags{Colors.ENDC}")
    result = make_request("GET", "/search/artists", params={"tags": ["rock", "alternative"], "limit": 5})
    if result:
        print_info(f"Artistes avec tags 'rock' ET 'alternative': {len(result)}")
        for artist in result[:3]:
            print(f"  - {artist.get('name')}")

def run_all_tests():
    """Exécute tous les tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'#' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'#' * 30} TESTS API LAST.FM {'#' * 30}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'#' * 80}{Colors.ENDC}")
    print(f"{Colors.CYAN}Base URL: {BASE_URL}{Colors.ENDC}")
    print(f"{Colors.CYAN}Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    
    try:
        test_health_check()
        test_artists_crud()
        test_users_crud()
        test_tags_crud()
        test_listens()
        test_tagged_artists()
        test_friendships()
        test_analytics()
        test_search()
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ TOUS LES TESTS SONT TERMINÉS{Colors.ENDC}")
        print(f"{Colors.GREEN}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrompus par l'utilisateur{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.RED}Erreur fatale: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()