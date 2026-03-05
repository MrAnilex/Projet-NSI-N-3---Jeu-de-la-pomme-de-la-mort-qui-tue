import pygame
import random
import sys
import os

# ==========================================
# CONFIGURATION DU JEU (pour la bombe)
# ==========================================
VRAIE_NUKE_ACTIVE = False  # Mets à True pour VRAIMENT éteindre le PC. (À vos risques et périls) (justement le "mode spécial")

# Initialisation obligatoire de Pygame et du module audio
pygame.init()
pygame.mixer.init()

# Paramètres de la fenêtre
LARGEUR = 1280
HAUTEUR = 720
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Leuh paahnyei - Paum Eupdayteuh _ (Le panier - Pomme Update)")
programIcon = pygame.image.load('icon.jpg')
pygame.display.set_icon(programIcon)
horloge = pygame.time.Clock() # Pour gérer les FPS

# Couleurs de secours (si il manque les assets)
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
GRIS = (100, 100, 100)
JAUNE = (255, 255, 0)

# ==========================================
# CHARGEMENT DES ASSETS (Images et Sons)
# ==========================================
# J'utilise des try/except. C'est une façon d'avoir des placeholders au lieu de crash
try:
    img_fond = pygame.image.load("fond.jpg").convert()
    img_fond = pygame.transform.scale(img_fond, (LARGEUR, HAUTEUR))
except:
    img_fond = None # PlaceHolder de fond noir

try:
    img_pomme = pygame.image.load("pomme.png").convert_alpha()
    img_pomme = pygame.transform.scale(img_pomme, (100, 100))
except:
    img_pomme = None

try:
    img_bombe = pygame.image.load("bombe.png").convert_alpha()
    img_bombe = pygame.transform.scale(img_bombe, (100, 100))
except:
    img_bombe = None

try:
    img_nuke = pygame.image.load("nuke.png").convert_alpha()
    img_nuke = pygame.transform.scale(img_nuke, (100, 100))
except:
    img_nuke = None
    

# Chargement des sons
try:
    son_pomme = pygame.mixer.Sound("pomme_son.mp3")
except:
    son_pomme = None

try:
    pygame.mixer.music.load("musique.mp3")
    pygame.mixer.music.play(-1) # -1 veut dire que la musique tourne en boucle
except:
    pass # Si pas de musique, c'est pas grave

try:
    son_mort = pygame.mixer.Sound("mort_son.mp3")
except:
    son_mort = None
    
# Police pour le texte (Score, Game Over)
police = pygame.font.SysFont("Arial", 36, bold=True)
police_gameover = pygame.font.SysFont("Arial", 72, bold=True)

# ==========================================
# VARIABLES GLOBALES DU JEU (L'état du jeu)
# ==========================================
# Le panier (Le joueur)
panier_largeur = 100
panier_hauteur = 20
panier_x = LARGEUR // 2 - panier_largeur // 2
panier_y = HAUTEUR - 50
panier_vitesse = 8

# Statistiques et Mécaniques
score = 0
pommes_attrapees = 0 # Sert à calculer l'accélération (toutes les 10 pommes)
jeu_en_cours = True

# Listes pour stocker nos objets qui tombent. 
# On utilise des dictionnaires pour stocker les infos de chaque objet.
pommes = []
bombes = []
nukes = []

# ==========================================
# BOUCLE PRINCIPALE (Le cœur du jeu)
# ==========================================
while True:
    # 1. GESTION DES ÉVÉNEMENTS (Quitter, touches du clavier)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if jeu_en_cours:
        # Vitesse globale qui augmente toutes les 10 pommes attrapées
        vitesse_chute = 4 + (pommes_attrapees // 10)

        # Mouvements du panier avec les flèches
        touches = pygame.key.get_pressed()
        if touches[pygame.K_LEFT] and panier_x > 0:
            panier_x -= panier_vitesse
        if touches[pygame.K_RIGHT] and panier_x < LARGEUR - panier_largeur:
            panier_x += panier_vitesse

        # Création du "Rectangle" du panier pour détecter les collisions facilement
        rect_panier = pygame.Rect(panier_x, panier_y, panier_largeur, panier_hauteur)

        # 2. APPARITION DES OBJETS (Aléatoire)
        # On a 1 chance sur X qu'un objet apparaisse à chaque image (frame)
        if random.randint(1, 20) == 1:
            # On ajoute un dictionnaire représentant une pomme dans la liste
            pommes.append({"x": random.randint(0, LARGEUR - 100), "y": -100})
        
        if random.randint(1, 50) == 1:
            bombes.append({"x": random.randint(0, LARGEUR - 100), "y": -100})
            
        if random.randint(1,250) == 1: # Les nukes sont très rares
            nukes.append({"x": random.randint(0, LARGEUR - 100), "y": -100})

        # 3. MISE À JOUR DES POSITIONS ET COLLISIONS
        
        # --- GESTION DES POMMES ---
        # On parcourt la liste à l'envers pour pouvoir supprimer des éléments sans bugger la boucle
        for i in range(len(pommes) - 1, -1, -1):
            pommes[i]["y"] += vitesse_chute
            rect_pomme = pygame.Rect(pommes[i]["x"], pommes[i]["y"], 75, 75)
            
            # Si le panier touche la pomme
            if rect_panier.colliderect(rect_pomme):
                score += 1
                pommes_attrapees += 1
                if son_pomme:
                    son_pomme.play()
                pommes.pop(i) # On retire la pomme de l'écran
            
            # Si la pomme tombe tout en bas (loupée !)
            elif pommes[i]["y"] > HAUTEUR:
                pommes.pop(i)

        # --- GESTION DES BOMBES ---
        for i in range(len(bombes) - 1, -1, -1):
            bombes[i]["y"] += vitesse_chute
            rect_bombe = pygame.Rect(bombes[i]["x"], bombes[i]["y"], 75, 75)
            
            if rect_panier.colliderect(rect_bombe):
                jeu_en_cours = False # GAME OVER CLASSIQUE
                if son_mort:
                    son_mort.play()
                raison_mort = "Il semble malheureusement que ce fruit était avarié, cela est fort dommage :("
            elif bombes[i]["y"] > HAUTEUR:
                bombes.pop(i)

        # --- GESTION DES NUKES ---
        for i in range(len(nukes) - 1, -1, -1):
            nukes[i]["y"] += vitesse_chute + 2 # La nuke tombe un peu plus vite, parce que c drol 
            rect_nuke = pygame.Rect(nukes[i]["x"], nukes[i]["y"], 50, 50)
            
            if rect_panier.colliderect(rect_nuke):
                # PLOT TWIST 
                if VRAIE_NUKE_ACTIVE:
                    # Détecte l'OS pour lancer la bonne commande d'extinction
                    if os.name == 'nt': # Si c'est Windows
                        os.system("shutdown /s /t 1") 
                    else: # Si c'est Mac/Linux
                        os.system("shutdown now")
                
                # Quoi qu'il arrive, ça crashe le jeu violemment
                pygame.quit()
                print("SAY GOODBYE !!")
                sys.exit()

            elif nukes[i]["y"] > HAUTEUR:
                nukes.pop(i)

    # 4. AFFICHAGE (Dessiner tout sur l'écran)
    
    # Dessin du fond
    if img_fond:
        ecran.blit(img_fond, (0, 0))
    else:
        ecran.fill(NOIR)

    # Dessin du panier
    pygame.draw.rect(ecran, BLANC, (panier_x, panier_y, panier_largeur, panier_hauteur))

    # Dessin des objets (Les placeHolders)
    for p in pommes:
        if img_pomme:
            ecran.blit(img_pomme, (p["x"], p["y"]))
        else:
            pygame.draw.rect(ecran, VERT, (p["x"], p["y"], 40, 40))
            
    for b in bombes:
        if img_bombe:
            ecran.blit(img_bombe, (b["x"], b["y"]))
        else:
            pygame.draw.rect(ecran, ROUGE, (b["x"], b["y"], 40, 40))
            
    for n in nukes:
        if img_nuke:
            ecran.blit(img_nuke, (n["x"], n["y"]))
        else:
            pygame.draw.rect(ecran, JAUNE, (n["x"], n["y"], 50, 50))
            
         
    # Affichage du texte (Score et Infos)
    texte_score = police.render(f"Score: {score}", True, BLANC)
    texte_vitesse = police.render(f"Vitesse: {4 + (pommes_attrapees // 10)}", True, GRIS)
    
    ecran.blit(texte_score, (10, 10))
    ecran.blit(texte_vitesse, (LARGEUR - 150, 10))

    # Affichage de l'écran de fin si on a touché une bombe
    if not jeu_en_cours:
        texte_fin = police_gameover.render("Oh non! c'est perdu :'(", True, ROUGE)
        texte_raison = police.render(raison_mort, True, BLANC)
        ecran.blit(texte_fin, (LARGEUR//2 - texte_fin.get_width()//2, HAUTEUR//2 - 50))
        ecran.blit(texte_raison, (LARGEUR//2 - texte_raison.get_width()//2, HAUTEUR//2 + 50))

    # On met à jour l'écran réel
    pygame.display.flip()

    # On bloque à 60 FPS (images par seconde)
    horloge.tick(60)
