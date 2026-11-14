PRAGMA foreign_keys = ON;
-- PRAGMA journal_mode = WAL; -- recomendado para un bot con escrituras frecuentes

-- ============================================================
-- CHATS: canales y grupos de Telegram.
-- id = chat_id de Telegram (estable y único, sin AUTOINCREMENT).
-- ============================================================
CREATE TABLE IF NOT EXISTS chats (
    id          INTEGER PRIMARY KEY,
    type        TEXT    NOT NULL CHECK (type IN ('private','group','supergroup','channel')),
    name        TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- POSTS: una publicación en un canal.
--   channel_*    -> para localizar el mensaje en el canal
--   discussion_* -> para localizar el hilo en el grupo vinculado
-- ============================================================
CREATE TABLE IF NOT EXISTS posts (
    id                      INTEGER PRIMARY KEY,
    channel_chat_id         INTEGER NOT NULL,
    channel_message_id      INTEGER NOT NULL,
    discussion_chat_id      INTEGER,            -- NULL hasta vincular el grupo
    discussion_message_id   INTEGER,            -- msg que abre el hilo en el grupo
    title_id                INTEGER NOT NULL,
    created_at              TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (channel_chat_id)    REFERENCES chats(id)  ON DELETE CASCADE,
    FOREIGN KEY (discussion_chat_id) REFERENCES chats(id)  ON DELETE SET NULL,
    FOREIGN KEY (title_id)           REFERENCES titles(id) ON DELETE CASCADE,

    UNIQUE (channel_chat_id, channel_message_id)
);

CREATE INDEX IF NOT EXISTS idx_posts_discussion
    ON posts (discussion_chat_id, discussion_message_id);
CREATE INDEX IF NOT EXISTS idx_posts_title ON posts (title_id);

-- ============================================================
-- DOMAINS: dominios normalizados.
--   kind: origin -> de dónde se sacó el contenido (pelisplus.com)
--         paste  -> pastes con los enlaces (paste.ee)
--         cloud  -> hosts de descarga (mega.nz)
-- ============================================================
CREATE TABLE IF NOT EXISTS domains (
    id         INTEGER PRIMARY KEY,
    kind       TEXT    NOT NULL CHECK (kind IN ('origin','paste','cloud')),
    host       TEXT    NOT NULL UNIQUE,
    name       TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PATHS: todo lo que va después del host ('/file/AbC-123').
-- URL completa = 'https://' || domains.host || paths.path
-- ============================================================
CREATE TABLE IF NOT EXISTS paths (
    id         INTEGER PRIMARY KEY,
    domain_id  INTEGER NOT NULL,
    path       TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
    UNIQUE (domain_id, path)
);

-- ============================================================
-- TITLES: unifica movies + tv_shows.
-- ============================================================
CREATE TABLE IF NOT EXISTS titles (
    id                 INTEGER PRIMARY KEY,
    media_type         TEXT    NOT NULL CHECK (media_type IN ('movie','tv')),
    original_title     TEXT    NOT NULL,
    title              TEXT    NOT NULL,
    release_date       TEXT,   -- movie: release_date | tv: first_air_date (YYYY-MM-DD)
    original_language  TEXT,
    tagline            TEXT,
    overview           TEXT,
    runtime            INTEGER,  -- solo movies
    number_of_seasons  INTEGER,  -- solo tv
    number_of_episodes INTEGER,  -- solo tv
    vote_average       NUMERIC,
    vote_count         INTEGER,
    created_at         TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- SEASONS
-- ============================================================
CREATE TABLE IF NOT EXISTS seasons (
    id            INTEGER PRIMARY KEY,
    title_id      INTEGER NOT NULL,
    season_number INTEGER NOT NULL,
    name          TEXT    NOT NULL,
    air_date      TEXT,
    episode_count INTEGER,
    overview      TEXT,
    vote_average  NUMERIC,
    created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (title_id) REFERENCES titles(id) ON DELETE CASCADE,
    UNIQUE (title_id, season_number)
);

-- ============================================================
-- EPISODES
-- ============================================================
CREATE TABLE IF NOT EXISTS episodes (
    id             INTEGER PRIMARY KEY,
    season_id      INTEGER NOT NULL,
    episode_number INTEGER NOT NULL,
    name           TEXT    NOT NULL,
    air_date       TEXT,
    overview       TEXT,
    runtime        INTEGER,
    vote_average   NUMERIC,
    vote_count     INTEGER,
    created_at     TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE CASCADE,
    UNIQUE (season_id, episode_number)
);

-- ============================================================
-- GENRES (id = id del género en TMDB)
-- ============================================================
CREATE TABLE IF NOT EXISTS genres (
    id         INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL UNIQUE,
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TITLE_GENRES (reemplaza movie_genres + tv_show_genres)
-- ============================================================
CREATE TABLE IF NOT EXISTS title_genres (
    title_id   INTEGER NOT NULL,
    genre_id   INTEGER NOT NULL,
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (title_id, genre_id),

    FOREIGN KEY (title_id) REFERENCES titles(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_title_genres_genre ON title_genres (genre_id);

-- ============================================================
-- EXTERNAL_IDS: provider = 'tmdb', 'imdb', 'tvdb', ...
-- ============================================================
CREATE TABLE IF NOT EXISTS external_ids (
    title_id    INTEGER NOT NULL,
    provider    TEXT    NOT NULL,
    external_id TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (title_id, provider),
    FOREIGN KEY (title_id) REFERENCES titles(id) ON DELETE CASCADE,
    UNIQUE (provider, external_id)
);

-- ============================================================
-- LINKS (reemplaza a sources y a la vieja origins).
-- Toda URL asociada a un título, en una sola tabla:
--   kind = origin   -> páginas de donde se obtuvo la peli (varias por título)
--   kind = paste    -> paste(s) con los enlaces de descarga
--   kind = download -> enlaces directos de descarga
-- parent_id: solo para downloads -> a qué paste pertenece el enlace.
-- season_id / episode_id: solo para series. name: '1080p Latino', etc.
-- is_active = 0 cuando el enlace cae; dead_at = cuándo se detectó.
-- ============================================================
CREATE TABLE IF NOT EXISTS links (
    id         INTEGER PRIMARY KEY,
    title_id   INTEGER NOT NULL,
    path_id    INTEGER NOT NULL,
    parent_id  INTEGER,
    season_id  INTEGER,
    episode_id INTEGER,
    name       TEXT,
    is_active  INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1)),
    dead_at    TEXT,
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (title_id)   REFERENCES titles(id)  ON DELETE CASCADE,
    FOREIGN KEY (path_id)    REFERENCES paths(id)   ON DELETE CASCADE,
    FOREIGN KEY (parent_id)  REFERENCES links(id)   ON DELETE SET NULL,
    FOREIGN KEY (season_id)  REFERENCES seasons(id) ON DELETE CASCADE,
    FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE

    -- UNIQUE (title_id, path_id) -- mismo enlace una vez por título
);

CREATE INDEX IF NOT EXISTS idx_links_parent ON links(parent_id);
CREATE INDEX IF NOT EXISTS idx_links_title_path ON links(title_id, path_id);

-- para el job que revisa enlaces caídos
CREATE INDEX IF NOT EXISTS idx_links_dead ON links (is_active) WHERE is_active = 0;

CREATE TABLE IF NOT EXISTS post_messages (
    id          INTEGER PRIMARY KEY,
    post_id     INTEGER NOT NULL,
    message_id  INTEGER NOT NULL,
    kind        TEXT    NOT NULL DEFAULT 'links'
                CHECK (kind IN ('links','info','other')),
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    UNIQUE (post_id, message_id)
);

-- ============================================================
-- POST_ITEMS: relación post <-> título.
-- bot_message_id: id del primer comentario del bot en el hilo
-- (el que lleva origins + paste + descargas). NULL hasta publicarlo.
-- ============================================================
/*
CREATE TABLE IF NOT EXISTS post_items (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id        INTEGER NOT NULL,
    title_id       INTEGER NOT NULL,
    bot_message_id INTEGER,
    created_at     TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (post_id)  REFERENCES posts(id)  ON DELETE CASCADE,
    FOREIGN KEY (title_id) REFERENCES titles(id) ON DELETE CASCADE
);
*/

CREATE INDEX IF NOT EXISTS idx_post_messages_post ON post_messages(post_id);
--CREATE INDEX IF NOT EXISTS idx_post_messages_title ON post_messages(title_id);

-- ============================================================
-- VISTA: URL completa ya armada, lista para mostrar/publicar
-- ============================================================
CREATE VIEW IF NOT EXISTS v_links AS
SELECT
    l.id, l.title_id, l.parent_id, l.name, l.season_id,
    l.episode_id, l.is_active, l.dead_at,
    d.host,
    p.path,
    'https://' || d.host || p.path AS url,
    l.created_at, l.updated_at
FROM links l
JOIN paths p   ON p.id = l.path_id
JOIN domains d ON d.id = p.domain_id;

-- ============================================================
-- TRIGGERS: updated_at automático (SQLite no tiene ON UPDATE)
-- ============================================================
CREATE TRIGGER IF NOT EXISTS trg_chats_updated AFTER UPDATE ON chats BEGIN
    UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_posts_updated AFTER UPDATE ON posts BEGIN
    UPDATE posts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_post_messages_updated AFTER UPDATE ON post_messages BEGIN
    UPDATE post_messages SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_titles_updated AFTER UPDATE ON titles BEGIN
    UPDATE titles SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_seasons_updated AFTER UPDATE ON seasons BEGIN
    UPDATE seasons SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_episodes_updated AFTER UPDATE ON episodes BEGIN
    UPDATE episodes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_genres_updated AFTER UPDATE ON genres BEGIN
    UPDATE genres SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_title_genres_updated AFTER UPDATE ON title_genres BEGIN
    UPDATE title_genres SET updated_at = CURRENT_TIMESTAMP
    WHERE title_id = NEW.title_id AND genre_id = NEW.genre_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_external_ids_updated AFTER UPDATE ON external_ids BEGIN
    UPDATE external_ids SET updated_at = CURRENT_TIMESTAMP
    WHERE title_id = NEW.title_id AND provider = NEW.provider;
END;

CREATE TRIGGER IF NOT EXISTS trg_domains_updated AFTER UPDATE ON domains BEGIN
    UPDATE domains SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_paths_updated AFTER UPDATE ON paths BEGIN
    UPDATE paths SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_links_updated AFTER UPDATE ON links BEGIN
    UPDATE links SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;