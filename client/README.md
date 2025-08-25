## Client — UI (HTML/CSS/JS)

Interface simple pour téléverser une vidéo, sélectionner les langues, suivre la progression et télécharger la vidéo sous-titrée et/ou le fichier `.srt`.

### Lancement

```
cd client
# Option rapide: ouvrir index.html dans le navigateur
# Option recommandée (CORS stable):
python -m http.server 5500  # http://localhost:5500
```

### Configuration

Dans `script.js`, la variable `apiUrl` pointe par défaut vers `http://localhost:8000`.
Adaptez-la si votre backend tourne ailleurs.

```js
this.apiUrl = "http://localhost:8000";
```

### Usage

-   Glisser-déposer ou sélectionner un fichier `.mp4/.avi/.mov/.mkv`
-   Choisir langue source et cible
-   Cliquer sur « Lancer la traduction »
-   Une fois terminé, télécharger la vidéo sous-titrée et/ou le `.srt`

### Comportement UI

-   Barre de progression et états intermédiaires simulés côté client pour une meilleure UX.
-   Les liens de téléchargement sont configurés à partir de la réponse JSON du backend.
