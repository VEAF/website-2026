# Migration des données depuis l'ancien site

Procédure pour importer les données de l'ancien site Symfony vers le nouveau site FastAPI + Vue.js.

## Prérequis

- Docker Compose lancé : `docker compose up`
- Accès à phpMyAdmin sur l'ancien site
- Accès au répertoire `var/data/files/` de l'ancien site (les fichiers uploadés)

## Étape 1 — Exporter la base de données en YAML

Depuis **phpMyAdmin** de l'ancien site :

1. Sélectionner la base de données
2. Aller dans l'onglet **Exporter**
3. Choisir le format **YAML**
4. **Exclure** les tables suivantes :
   - `*_stats` (tables de statistiques)
   - `pe_*` (tables Perun)
5. Lancer l'export et récupérer le fichier `website.yml`

## Étape 2 — Déposer le fichier YAML

Copier le fichier exporté dans le répertoire `backend/var/` :

```bash
cp website.yml backend/var/website.yml
```

## Étape 3 — Copier les fichiers uploadés

Les fichiers de l'ancien site sont stockés dans `var/data/files/` avec une arborescence `{uuid[0]}/{uuid[1]}/{uuid}` (sans extension).

Créer une archive tar depuis l'ancien site, puis l'extraire dans le répertoire `uploads/` du backend :

```bash
# Sur l'ancien site : créer l'archive
cd /var/www/html    # ou le répertoire racine de l'ancien site
tar czf files.tgz -C var/data/files .

# Copier l'archive vers le nouveau site
cp files.tgz backend/var/files.tgz

# Extraire dans le répertoire uploads du backend
mkdir -p backend/uploads
tar xzf backend/var/files.tgz -C backend/uploads
```

## Étape 4 — Importer les données en base

Cette commande **supprime toutes les tables existantes**, les recrée, puis importe les données depuis le fichier YAML :

```bash
scripts/console.sh maintenance import-yaml
```

Le fichier `var/website.yml` est utilisé par défaut. Pour un autre chemin :

```bash
scripts/console.sh maintenance import-yaml --filepath var/autre_fichier.yml
```

## Étape 5 — Corriger les noms de fichiers

Les fichiers importés depuis l'ancien site sont stockés sans extension (ex: `ab4680f3-...`), or le nouveau site attend `{uuid}.{extension}`. Cette commande renomme les fichiers en ajoutant leur extension depuis la base de données.

Prévisualiser les changements (dry-run, par défaut) :

```bash
scripts/console.sh maintenance fix-filenames
```

Appliquer les renommages :

```bash
scripts/console.sh maintenance fix-filenames --no-dry-run
```

## Résumé des commandes

```bash
# 1. Démarrer les services
docker compose up -d

# 2. Déposer le YAML et les fichiers
cp website.yml backend/var/website.yml
tar xzf backend/var/files.tgz -C backend/uploads

# 3. Importer les données
scripts/console.sh maintenance import-yaml

# 4. Corriger les noms de fichiers
scripts/console.sh maintenance fix-filenames --no-dry-run
```
