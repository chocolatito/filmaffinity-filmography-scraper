# [filmaffinity-filmography-scraper](https://github.com/chocolatito/filmaffinity-filmography-scraper)
A simple program to extract the filmography of actors or directors from the website `filmaffinity.com`.

* [Install dependencies](#install-dependencies)
* [Project Structure](#project-Structure)
* [Input file](#input-file)
* [Execution](#execution)
  * [Example for development](#example-for-development)
* [Output files](#output-files)

## Install dependencies
```sh
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Project Structure
```
.
├── .flake8
├── .gitignore
├── input.dev.json
├── LICENSE
├── main.py
├── README.md
├── requirements.txt
├── src
│   ├── constants.py
│   ├── crawler.py
│   ├── env-example.template
│   ├── orchestrator.py
│   ├── parser_mixin.py
│   ├── scraper.py
│   └── utils.py
```

> When the scraper is run, a `FILES/` folder is created in the project root if it does not exist.
```
.
├── FILES/
├── .flake8
├── .gitignore
├── input.dev.json
├── LICENSE
```

## Input file
A JSON file containing an array of URLs.
Two types of URLs are allowed:
- Film URL
  - `https://www.filmaffinity.com/us/film<data_movie_id>.html`
- Name URL
  - `https://www.filmaffinity.com/us/name.php?name-id=<name_id>`

```JSON
[
    // URL of movies or directors/actors 
    "https://www.filmaffinity.com/us/film<data_movie_id>.html",
    "https://www.filmaffinity.com/us/film<data_movie_id>.html",
    "https://www.filmaffinity.com/us/name.php?name-id=<name_id>",
    // ...
    "https://www.filmaffinity.com/us/name.php?name-id=<name_id>"
    // ...
    "https://www.filmaffinity.com/us/film<data_movie_id>.html"
]
```
## Execution
Run from `main.py` passing the argument `json_input`
```sh
$ python main.py --json_input `json_filename`
```
The `json_filename` must be:
- The name of the JSON file (e.g. `json_input.json`, `input_20041_b.json`, etc.), when the file is located in the same directory as the `main.py` file.
- The full path of a JSON file in any directorie (e.g. `/home/dev/INPUTs/alpha.json`, `/home/dev/db/testing_v1.json`, etc.)

### Example for development
Example for development `input.dev.json`
```
$ python main.py --json_input input.dev.json
```

## Output files
```
├── FILES/
│   ├── films_results.json
│   └── names_results.json
├── filmaffinity-filmography-scraper.log
```

Example of `./FILES/films_results.json`
```json
{
    "<data_movie_id_1>": {
        "original_title": "string",
        "extra_keys": "object",
        "date_published": "string",
        "duration": "string",
        "country": "string",
        "director": "array",
        "screenwriter": "array",
        "cast": "array",
        "music": "array",
        "cinematography": "array",
        "producer": "array",
        "genre": "array",
        "movie_groups": "array",
        "description": "string",
        "data_movie_id": "string",
        "url": "string",
        "full_details": true
    },
    "<data_movie_id_2>": {
        "title": "string",
        "url": "string",
        "data_movie_id": "string",
        "year": "string",
        "full_details": false
    }
}
```

Example of `./FILES/names_results.json`
```json
{
    "name_id": {
        "name": "string",
        "filmography_url": "string",
        "name_id": "string",
        "filmography": [
            "<data_movie_id_1>",
            "<data_movie_id_2>"
        ],
        "url": "string"
    }
}
```