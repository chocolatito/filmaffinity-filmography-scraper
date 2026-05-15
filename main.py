from src.orchestrator import Orchestrator

if __name__ == "__main__":    
    # title
    input_list = ["https://www.filmaffinity.com/us/film120484.html"]
    orchestrator = Orchestrator(input_list)
    orchestrator.main_from_title_to_director()
    # name
    # input_list = ["https://www.filmaffinity.com/us/name.php?name-id=695479527"]
    # orchestrator = Orchestrator(input_list)
    # orchestrator.main_from_director_to_title()
