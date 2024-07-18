# Inverted Index using SPIMI technique
- [Introducción](#introducción)
    - [Objetivo del proyecto](#objetivo-del-proyecto)
    - [Dominio de datos](#dominio-de-datos)
- [Backend: Índice Invertido](#backend-índice-invertido)
    - [Construcción en memoria secundaria](#construcción-en-memoria-secundaria)
    - [Ejecución de consultas aplicando Similitud de Coseno](#ejecución-de-consultas-aplicando-similitud-de-coseno)
    - [Índice Invertido en PostgreSQL](#índice-invertido-en-postgresql)
- [Backend: Índice Multidimensional](#backend-índice-multidimensional)
  	-[Técnica de indexación de las librerías utilizadas]
  	-[KNN Search y Range Search]
  	-[Maldición de la dimensionalidad]
- [Frontend](#frontend)
    - [Manual de usuario](#manual-de-usuario)
    - [Diseño de GUI](#diseño-de-gui)
- [Experimentación](#experimentación)
    - [Resultados experimentales](#resultados-experimentales)
    - [Análisis y discusión](#análisis-y-discusión)
- [Autores](#autores)


# Introducción
## Objetivo del proyecto
El objetivo de este proyecto es construir un índice invertido utilizando la técnica Single-Pass In-Memory Indexing (SPIMI) para manejar grandes colecciones de documentos. 
 - El índice invertido permitirá realizar consultas eficientes y recuperar los documentos más relevantes utilizando la similitud de coseno. 
 - Se implementará una interfaz gráfica de usuario (GUI) para facilitar la interacción con el sistema de recuperación de información. 
 - Se realizarán experimentos para evaluar el rendimiento del índice invertido y analizar los resultados obtenidos.
## Dominio de datos
El dominio de datos consiste en letras de canciones disponibles en Spotify. El dataset contiene la siguiente información:
- **Nombre del archivo**: `spotify_songs.csv`
- **Cantidad de filas**: 18,454
- **Cantidad de columnas**: 25
- **Nombres de columnas**: `track_id`, `track_name`, `track_artist`, `lyrics`, etc.

Las columnas que usaremos para la construcción del índice invertido son `track_name`, `track_artisti` y `lyrics`. El objetivo es permitir a los usuarios buscar canciones por su nombre o por palabras clave en las letras de las canciones.


# Backend: Índice Invertido
## Construcción en memoria secundaria
La construcción del índice invertido se realiza en memoria secundaria utilizando la técnica SPIMI, que incluye los siguientes pasos:

1. **Preprocesamiento**: Las letras de las canciones se preprocesan utilizando la tokenización, eliminación de stopwords y stemming.
2. **Construcción del índice**: Los términos se agrupan en bloques. Cada bloque se ordena y se escribe en disco para liberar espacio en memoria.
3. **Merge de bloques**: Los bloques ordenados se fusionan en un índice invertido final, almacenado en disco en formato `.txt`.

## Ejecución de consultas aplicando Similitud de Coseno
La ejecución de consultas se realiza aplicando la similitud de coseno entre la consulta y los documentos en el índice. El proceso incluye:

1. **Procesamiento de la consulta**: La consulta se tokeniza, se eliminan las stopwords y se aplican técnicas de stemming.
2. **Cálculo de pesos TF-IDF**: Se calculan los pesos TF-IDF para los términos de la consulta y los documentos.
3. **Similitud de coseno**: Se calcula la similitud de coseno entre la consulta y cada documento en el índice. Los documentos se ordenan por su relevancia y se devuelve el top-k de documentos más relevantes.

## Índice Invertido en PostgreSQL
El índice invertido puede ser integrado en PostgreSQL utilizando técnicas avanzadas de indexación como GIN (Generalized Inverted Index) para realizar búsquedas eficientes en texto completo.

Al aplicar el índice GIN a una columna de texto completo en PostgreSQL, este motor de base de datos utiliza un proceso de tokenización para dividir el texto en palabras o significativas. Elimina los stop words y caracteres no alfabéticos según el diccionario de texto completo especificado (en esta implementación será 'english'). Una vez que el texto se ha tokenizado, PostgreSQL genera un vector de texto (tsvector) para cada fila en la tabla que contiene la columna indexada. Este vector representa un conjunto ordenado de tokens que están presentes en el texto. Finalmente, cada palabra única se convierte en clave del índice, es decir, mantiene una lista de 'postings', donde cada posting contiene información sobre las filas de la tabla donde esa palabra en específico aparece.

Los pasos a seguir para la implementación del índice GIN en PostgreSQL fueron los siguientes:

1. Creamos una tabla `spotify_table` cuyas columnas son los mismos atributos indicados en el archivo de datos elegido.
2. Cargamos la información del archivo de datos a la tabla.
   
```sql
COPY spotify_table
FROM 'C:\Program Files\PostgreSQL\13\data\spotify_songs.csv'
DELIMITER ','
CSV HEADER;
```
3. Creamos una nueva columna `author_lyrics_tsvector` en la tabla de tipo `tsvector`, la cual alojará la concatenación de los 3 campos elegidos a realizar la búsqueda de texto completo.
```sql
ALTER TABLE spotify_table ADD COLUMN author_lyrics_tsvector tsvector;
```
```sql
UPDATE spotify_table 
SET author_lyrics_tsvector = setweight(to_tsvector('english', track_artist), 'A') 
	|| setweight(to_tsvector('english', track_name), 'B') 
	|| setweight(to_tsvector('english', lyrics), 'C');
```

4. Por último, construimos el índice GIN sobre esta nueva columna.
```sql
CREATE INDEX idx_gin_author_lyrics ON spotify_table USING GIN (author_lyrics_tsvector);
```
5. Para realizar la consulta, utilizamos la función `ts_query` para convertir la cadena de búsqueda en una estructura que PostgreSQL pueda comparar con los índices creados.
```sql
SELECT track_id, track_name, track_artist, lyrics
FROM spotify_table
WHERE author_lyrics_tsvector @@ to_tsquery('english', query)
LIMIT K
```
# Backend: Índice Multidimensional
## Técnica de indexación de las librerías utilizadas
### RTree
La librería de ```rtree``` utiliza un índice R-tree para indexar datos multidimensionales. Un R-tree es una estructura de datos que organiza los datos espaciales en forma de árbol, permitiendo búsquedas eficientes basadas en la localización. Utiliza técnicas de particionamiento espacial para agrupar objetos que están cerca unos de otros en el espacio multidimensional.

#### Construcción del Índice en rtree
1. **Creación del Árbol:** Se inicia creando un árbol vacío.
2. **Inserción de Datos:** Se añaden los datos al árbol R-tree, donde cada dato está asociado con un MBR que representa su ubicación en el espacio multidimensional.
3. **Optimización y Balanceo:** El árbol R-tree se optimiza y balancea para asegurar que las búsquedas sean eficientes.

### Faiss
Faiss emplea técnicas avanzadas como índices vectoriales (como el índice IVFADC) para realizar búsquedas eficientes en grandes conjuntos de datos vectoriales, como características extraídas de imágenes o texto. Utiliza métodos de agrupamiento jerárquico y cuantización vectorial para optimizar el espacio de búsqueda.

#### Construcción del Índice en faiss
1. **Selección del Índice:** Se elige un tipo de índice adecuado para los datos vectoriales, como IVFADC (Índice de Vector de Fuerza Acelerada con Clustering Densidad Aproximado).
2. **Entrenamiento del Índice:** Se entrena el índice con los datos vectoriales de entrada, donde se aplican técnicas de agrupamiento y cuantización para optimizar el espacio de búsqueda.
3. **Indexación Eficiente:** Faiss realiza la indexación de los vectores de manera eficiente, preparándolos para realizar búsquedas rápidas.

## Búsquedas
### RTree
- **KNN Search:** rtree permite realizar búsquedas de los k vecinos más cercanos utilizando el índice R-tree. Esto se logra buscando en el árbol los nodos más cercanos al punto de consulta y refinando la búsqueda en los nodos cercanos para encontrar los vecinos más cercanos.
- **Range Search:** También es posible realizar búsquedas por rango en rtree. Esto implica buscar todos los objetos dentro de un rango específico definido por un rectángulo o una región en el espacio multidimensional.

### Faiss
- **KNN Search:** En faiss, el KNN Search se realiza utilizando índices de aproximación que optimizan la búsqueda de los vecinos más cercanos en espacios vectoriales de alta dimensionalidad.
- **Range Search:** Faiss soporta búsquedas por rango mediante el uso de índices que permiten buscar todos los vectores dentro de un radio específico en el espacio vectorial.

## Maldición de la dimensionalidad
Para mitigar la maldición de la dimensionalidad se pueden seguir las siguientes estrategias:

- **Selección de Características:** Reducir la dimensionalidad de los datos eliminando características irrelevantes o redundantes puede ayudar a mitigar la maldición de la dimensionalidad.
- **Cuantización:** Faiss utiliza técnicas de cuantización que reducen la dimensionalidad efectiva de los datos, haciendo que las búsquedas sean más rápidas y eficientes.
- **Índices Aproximados:** Faiss permite el uso de índices aproximados que facilitan la búsqueda rápida en datos de alta dimensionalidad al sacrificar una pequeña cantidad de precisión.
- **Uso de GPUs:** Faiss está optimizado para utilizar GPUs, lo que permite realizar cálculos intensivos en paralelo y manejar grandes volúmenes de datos multidimensionales con mayor rapidez.


# Frontend
## Manual de usuario
## Diseño de GUI

# Experimentación
## Resultados experimentales
## Análisis y discusión



# Autores

|                     **Isaac Vera Romero**                   |                                 **David Torres Osorio**                                 |                       **Pedro Mori**                     |  **Leonardo Candio** |   **Esteban Vasquez**  |
|:----------------------------------------------------------------------------------:|:-----------------------------------------------------------------------------------:|:-----------------------------------------------------------------------------------:|:-----------------------------------------------------------------------------------:|:----:|
|           ![Isaac Vera Romero](https://avatars.githubusercontent.com/u/67709665?v=4)            |      ![David Torres Osorio](https://avatars.githubusercontent.com/u/63759366?v=4)       |              ![Pedro Mori](https://avatars.githubusercontent.com/u/82919499?v=4)              | ![Leonardo Candio](https://avatars.githubusercontent.com/u/75516714?v=4) | ![Esteban Vasquez](https://avatars.githubusercontent.com/u/41312479?v=4) |                                             
| <a href="https://github.com/IsaacVera10" target="_blank">`github.com/IsaacVera10`</a> | <a href="https://github.com/davidt02tech" target="_blank">`github.com/davidt02tech`</a> | <a href="https://github.com/PedroMO11" target="_blank">`github.com/PedroMO11`</a> | <a href="https://github.com/leonardocandio" target="_blank">`github.com/leonardocandio`</a>|<a href="https://github.com/MuchSquid" target="_blank">`github.com/MuchSquid`</a>|

