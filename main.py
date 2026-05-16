from src.orchestrator import Orchestrator

if __name__ == "__main__":
    input_list = ["https://www.filmaffinity.com/us/film120484.html",
                  "https://www.filmaffinity.com/us/name.php?name-id=695479527",]
    orchestrator = Orchestrator(input_list)
    orchestrator.main()
