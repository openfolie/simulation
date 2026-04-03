from mesa.discrete_space import Grid2DMovingAgent
import commons


class person(Grid2DMovingAgent):

    def take_action(self):
        self.available_options = commons.observe_options()
        # now  consider long term goials and stuff amd take action accordingly

    def observe_options(self):
        pass


class person_rl(person):
    def __init__(self, model):
        super().__init__(model)
        self.neighbours = []
        self.civilization = civilization
        self.gender = gender

    def reward_function():
        pass
