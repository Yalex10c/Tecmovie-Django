# 🎬 TECMOVIE - Plataforma de películas con Django

TECMOVIE es una plataforma web desarrollada con Django y MySQL que permite a los usuarios explorar películas, calificarlas, guardar favoritas, crear watchlists y recibir recomendaciones personalizadas.

---

## 🚀 Funcionalidades principales

- Registro e inicio de sesión
- Catálogo de películas
- Vista de detalle de cada película
- Sistema de calificaciones y reseñas
- Favoritos
- Watchlist
- Historial de visitas
- Recomendaciones personalizadas
- “Mi Mundo” (preferencias por género)
- Panel de administrador (Django Admin)
- Sistema freemium (planes)

---

## 🧠 Tecnologías utilizadas

- Python 3.13
- Django 5.1.7
- MySQL
- PyMySQL
- HTML + CSS
- JavaScript

---

## ⚙️ Instalación del proyecto

### 1. Clonar repositorio

```bash
git clone https://github.com/Yalex10c/Tecmovie-Django.git
cd Tecmovie-Django

----
# Para crear el entorno 
python -m venv venv

# Y para activarlo

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

--------
#Para instalar dependencias

pip install -r requirements.txt

----------------
#Este proyecto usa MySQL manual + Django, por lo que debes:

Crear la base de datos:

-- =====================================
-- CREAR BASE DE DATOS
-- =====================================
CREATE DATABASE plataforma_peliculas;
USE plataforma_peliculas;

-- =====================================
-- TABLA GENEROS
-- =====================================
CREATE TABLE generos (
    id_genero INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

-- =====================================
-- TABLA DIRECTORES
-- =====================================
CREATE TABLE directores (
    id_director INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL
);

-- =====================================
-- TABLA PELICULAS
-- =====================================
CREATE TABLE peliculas (
    id_pelicula INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    anio YEAR NOT NULL,
    id_genero INT,
    id_director INT,
    resumen TEXT,
    imagen_url VARCHAR(500),
    FOREIGN KEY (id_genero) REFERENCES generos(id_genero),
    FOREIGN KEY (id_director) REFERENCES directores(id_director)
);

-- =====================================
-- TABLA ACTORES (REPARTO)
-- =====================================
CREATE TABLE actores (
    id_actor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL
);

-- =====================================
-- RELACION MUCHOS A MUCHOS PELICULAS - ACTORES
-- =====================================
CREATE TABLE pelicula_actor (
    id_pelicula INT,
    id_actor INT,
    PRIMARY KEY (id_pelicula, id_actor),
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE CASCADE,
    FOREIGN KEY (id_actor) REFERENCES actores(id_actor) ON DELETE CASCADE
);

-- =====================================
-- TABLA PLATAFORMAS (DONDE SE PUEDE VER)
-- =====================================
CREATE TABLE plataformas (
    id_plataforma INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    url VARCHAR(500)
);

-- =====================================
-- RELACION PELICULAS - PLATAFORMAS
-- =====================================
CREATE TABLE pelicula_plataforma (
    id_pelicula INT,
    id_plataforma INT,
    PRIMARY KEY (id_pelicula, id_plataforma),
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE CASCADE,
    FOREIGN KEY (id_plataforma) REFERENCES plataformas(id_plataforma) ON DELETE CASCADE
);

-- =====================================
-- TABLA USUARIOS
-- =====================================
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(150) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================
-- TABLA RESEÑAS
-- =====================================
CREATE TABLE resenas (
    id_resena INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_pelicula INT,
    comentario TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE CASCADE
);

-- =====================================
-- TABLA CALIFICACIONES
-- =====================================
CREATE TABLE calificaciones (
    id_calificacion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_pelicula INT,
    puntuacion DECIMAL(2,1) CHECK (puntuacion >= 0 AND puntuacion <= 10),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE CASCADE
);

-- =====================================
-- TABLA PLANES DE SUSCRIPCION
-- =====================================
CREATE TABLE planes (
    id_plan INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(8,2) NOT NULL,
    duracion_meses INT NOT NULL
);

-- =====================================
-- TABLA SUSCRIPCIONES
-- =====================================
CREATE TABLE suscripciones (
    id_suscripcion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_plan INT,
    fecha_inicio DATE,
    fecha_fin DATE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_plan) REFERENCES planes(id_plan)
);

-- =====================================
-- TABLA METODO DE PAGO (SOLO TARJETA)
-- =====================================
CREATE TABLE metodo_pago (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    numero_tarjeta VARCHAR(20) NOT NULL,
    nombre_tarjeta VARCHAR(150) NOT NULL,
    fecha_expiracion DATE NOT NULL,
    cvv VARCHAR(4) NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- =====================================
-- Nueva tabla para géneros múltiples
-- =====================================

CREATE TABLE pelicula_genero (
    id_pelicula INT NOT NULL,
    id_genero INT NOT NULL,
    PRIMARY KEY (id_pelicula, id_genero),
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE CASCADE,
    FOREIGN KEY (id_genero) REFERENCES generos(id_genero) ON DELETE CASCADE
);

-- =====================================
-- Nueva tabla para directores múltiples
-- =====================================

CREATE TABLE pelicula_director (
    id_pelicula INT NOT NULL,
    id_director INT NOT NULL,
    PRIMARY KEY (id_pelicula, id_director),
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE CASCADE,
    FOREIGN KEY (id_director) REFERENCES directores(id_director) ON DELETE CASCADE
);

-- =====================================
-- Copiar géneros actuales
-- =====================================

INSERT INTO pelicula_genero (id_pelicula, id_genero)
SELECT id_pelicula, id_genero
FROM peliculas
WHERE id_genero IS NOT NULL;

-- =====================================
-- Copiar directores actuales
-- =====================================

INSERT INTO pelicula_director (id_pelicula, id_director)
SELECT id_pelicula, id_director
FROM peliculas
WHERE id_director IS NOT NULL;

ALTER TABLE pelicula_genero
ADD INDEX idx_pg_pelicula (id_pelicula),
ADD INDEX idx_pg_genero (id_genero);

ALTER TABLE pelicula_genero
DROP PRIMARY KEY;
ALTER TABLE pelicula_genero
ADD COLUMN id INT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;

ALTER TABLE pelicula_genero
ADD CONSTRAINT uq_pelicula_genero UNIQUE (id_pelicula, id_genero);

ALTER TABLE pelicula_director
ADD INDEX idx_pd_pelicula (id_pelicula),
ADD INDEX idx_pd_director (id_director);

ALTER TABLE pelicula_director
DROP PRIMARY KEY;

ALTER TABLE pelicula_director
ADD COLUMN id INT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;

ALTER TABLE pelicula_director
ADD CONSTRAINT uq_pelicula_director UNIQUE (id_pelicula, id_director);

ALTER TABLE pelicula_actor
ADD INDEX idx_pa_pelicula (id_pelicula),
ADD INDEX idx_pa_actor (id_actor);

ALTER TABLE pelicula_actor
DROP PRIMARY KEY;

ALTER TABLE pelicula_actor
ADD COLUMN id INT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;

ALTER TABLE pelicula_actor
ADD CONSTRAINT uq_pelicula_actor UNIQUE (id_pelicula, id_actor);

ALTER TABLE pelicula_plataforma
ADD INDEX idx_pp_pelicula (id_pelicula),
ADD INDEX idx_pp_plataforma (id_plataforma);

ALTER TABLE pelicula_plataforma
DROP PRIMARY KEY;

ALTER TABLE pelicula_plataforma
ADD COLUMN id INT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;

ALTER TABLE pelicula_plataforma
ADD CONSTRAINT uq_pelicula_plataforma UNIQUE (id_pelicula, id_plataforma);

-- =====================================
-- Preferencias de usuario
-- =====================================

CREATE TABLE usuario_genero_preferencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_genero INT NOT NULL,
    CONSTRAINT fk_ugp_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_ugp_genero FOREIGN KEY (id_genero) REFERENCES generos(id_genero) ON DELETE CASCADE,
    CONSTRAINT uq_usuario_genero UNIQUE (id_usuario, id_genero)
);

-- =====================================
-- Historial de visitas
-- =====================================

CREATE TABLE historial_visitas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_pelicula INT NOT NULL,
    fecha_visita DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_historial_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_historial_pelicula FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE CASCADE
);

SHOW TABLES LIKE 'peliculas';

DESCRIBE pelicula_actor;
DESCRIBE pelicula_plataforma;

---------------------
# Configurar conexión en Django

En: config/settings.py

Configura tu base de datos:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'plataforma_peliculas',
        'USER': 'root',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


----------------------
# Migraciones (solo para tablas de Django)

python manage.py makemigrations
python manage.py migrate

-----------------------
# Para saber si ya todo es correcto y poder entrar a la parte de administrador se tendrá que correr lo siguiente

Crear superusuario: 
python manage.py createsuperuser

------------------------
#Para correr el servidor
Ejecutar servidor: 
python manage.py runserver

Y para abrir la página es en: http://127.0.0.1:8000/ y el panel de admin ingresando con el super usuario http://127.0.0.1:8000/admin/ 