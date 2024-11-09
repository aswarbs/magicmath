from ProfileGen import Profile, Era, gen_profile
from ProblemGen import generate_countdown_problem
import concurrent.futures
from tqdm import tqdm

class Level():
    def __init__(self, character: Profile, topic: str):
        self.problem = generate_countdown_problem()
        self.character = character
        self.topic = topic
        pass
    def get_rep(self):
        return f"{self.character} <-> {self.topic}"

class Story():
    def __init__(self, levels: list[Level]):
        self.levels = levels
        pass
    def __repr__(self):
        return "".join([l.get_rep() for l in self.levels])




# Assuming Level, Story, Era, and gen_profile are defined somewhere
def generate_level(era) -> Level:
    return Level(
        gen_profile(era),
        topic="Countdown Solver"
    )


def generate_story(level_count=2, era=Era.MODERN) -> Story:
    # Create a ThreadPoolExecutor with as many threads as needed
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Use tqdm to show the progress as levels are generated
        levels = list(tqdm(executor.map(generate_level, [era] * level_count), total=level_count))

    # Return the Story object with the generated levels
    return Story(levels)


if __name__ == '__main__':
    s= generate_story()
    print(s)