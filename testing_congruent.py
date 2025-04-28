import src.congruent_incongruent.experiment as experiment
import src.congruent_incongruent.generator as generator

screen = experiment.initialize_pygame()
experiment.show_text(screen, "Press space to quit", 40, (255, 255, 255), 0, 0)
experiment.wait_for_answer(screen)

