import numpy as np
import pandas as pd
import seaborn as sns
import mesa
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid
from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from Spaces import Map
import agents
import environment


def agent_portrayal():
    return AgentPortrayalStyle(color="blue", size=50)


def visualize():
    page = SolaraViz(Map((256, 256), False, 400, 2))
