# [filmaffinity-filmography-scraper](https://github.com/chocolatito/filmaffinity-filmography-scraper)
A simple program to extract the filmography of actors or directors from the website `filmaffinity.com`.

## Install dependencies
```sh
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Project Structure
```
.
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

Run from `main.py`. Add the film URLs or names (directors, actors, etc.) from the `input_list` variable.
```py
# /main.py

if __name__ == "__main__":
    input_list = [
        # ...
    ]
    # ...
```

> A `FILES/` folder is created in the project root if it does not exist.
```
.
├── FILES/
├── LICENSE
├── main.py
├── README.md
```

Name of `.log` file:
- `filmaffinity-filmography-scraper.log`

Output files.
```
├── FILES/
│   ├── films_results.json
│   └── names_results.json
```
