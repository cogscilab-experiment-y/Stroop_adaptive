import atexit
import csv
import time
import random
from os.path import join
from psychopy import visual, event, core

from code.load_data import load_config
from code.screen_misc import get_screen_res
from code.show_info import part_info, show_info, show_stim
from code.trials import create_experiment_part
from code.check_exit import check_exit

RESULTS = []
PART_ID = ""
N = 1


@atexit.register
def save_beh_results():
    num = "".join(map(str, list(time.localtime())[:6]))
    with open(join('results', '{}_beh_{}.csv'.format(PART_ID, num)), 'w', newline='') as beh_file:
        dict_writer = csv.DictWriter(beh_file, RESULTS[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(RESULTS)


def run_block(trials_list, config, win, experiment_part_type, block_idx, trial_time, extra_text, feedback):
    global N, RESULTS
    reaction_keys = [word["key"] for word in config["word_bank"]]
    clock = core.Clock()
    block_acc = 0
    for trial in trials_list:
        answer = None
        reaction_time = None
        acc = -1
        stim = visual.TextStim(win, color=trial["color"], text=trial["word"], height=config["stim_size"], pos=config["stim_pos"])

        [text.setAutoDraw(True) for text in extra_text]
        stim.setAutoDraw(True)
        win.callOnFlip(clock.reset)
        win.flip()

        while clock.getTime() < trial_time/1000:
            ans = event.getKeys(keyList=reaction_keys)
            if ans:
                reaction_time = clock.getTime()
                answer = ans[0]
                break
            check_exit()
            win.flip()

        [text.setAutoDraw(False) for text in extra_text]
        stim.setAutoDraw(False)
        win.callOnFlip(event.clearEvents)
        win.flip()

        if answer is not None:
            acc = 1 if answer == trial["key"] else 0
            if acc == 1:
                block_acc += 1

        trial_results = {"n": N,
                         "block_type": experiment_part_type,
                         "block_index": block_idx,
                         "trial_type": trial["trial_type"],
                         "rt": reaction_time,
                         "acc": acc,
                         "trail_time": trial_time,
                         "word": trial["word"],
                         "color": trial["color"],
                         "answer": answer,
                         "correct_answer": trial["key"]}
        RESULTS.append(trial_results)
        N += 1

        if experiment_part_type == "training":
            show_stim(feedback[acc], config["fdbk_show_time"], clock, win)

        wait_time = random.randint(config["wait_time"][0], config["wait_time"][0])
        show_stim(None, wait_time, clock, win)

    return block_acc


def run_experiment_part(win, screen_res, blocks_list, config, experiment_part_type, extra_text, feedback):
    show_info(win, join('.', 'messages', f"{experiment_part_type}.txt"), text_color=config["text_color"], text_size=config["text_size"],
              screen_res=screen_res)
    trial_time = config["start_trial_time"]
    for block_idx, block in enumerate(blocks_list):
        block_acc = run_block(trials_list=block["trial_list"], config=config, win=win, experiment_part_type=experiment_part_type,
                              block_idx=block_idx+1, trial_time=trial_time, extra_text=extra_text, feedback=feedback)
        if block_acc >= block["step_down_acc"]:
            trial_time -= block["step_down_time"]
            if trial_time < config["minimal_time"]:
                trial_time = config["minimal_time"]
        elif block_acc <= block["step_up_acc"]:
            trial_time += block["step_up_time"]
    return trial_time

def main():
    global PART_ID
    config = load_config()
    info, PART_ID = part_info()

    screen_res = dict(get_screen_res())
    win = visual.Window(list(screen_res.values()), fullscr=True, units='pix', screen=0, color=config["screen_color"])
    mouse = event.Mouse(visible=False)

    extra_text = [visual.TextBox2(win, color=text["color"], text=text["text"], letterHeight=text["size"], pos=text["pos"], alignment="center")
                  for text in config["extra_text_to_show"]]

    feedback_text = (config["fdbk_incorrect"], config["fdbk_no_answer"], config["fdbk_correct"])
    feedback = {i: visual.TextBox2(win, color=config["fdbk_color"], text=text, letterHeight=config["fdbk_size"], alignment="center")
                for (i, text) in zip([0, -1, 1], feedback_text)}

    training_trials = create_experiment_part(info=config["training_trials"], word_bank=config["word_bank"])
    run_experiment_part(win=win, screen_res=screen_res, blocks_list=training_trials, config=config, experiment_part_type="training",
                        extra_text=extra_text, feedback=feedback)

    experiment_trials = create_experiment_part(info=config["experiment_trials"], word_bank=config["word_bank"])
    trial_time = run_experiment_part(win=win, screen_res=screen_res, blocks_list=experiment_trials, config=config, experiment_part_type="experiment",
                                     extra_text=extra_text, feedback=feedback)
    trial_results = {"n": N,
                     "block_type": "end",
                     "block_index": len(config["experiment_trials"]) + 1,
                     "trial_type": "end",
                     "rt": "end",
                     "acc": "end",
                     "trail_time": trial_time,
                     "word": "end",
                     "color": "end",
                     "answer": "end",
                     "correct_answer": "end"}
    RESULTS.append(trial_results)
    show_info(win, join('.', 'messages', f'end.txt'), text_color=config["text_color"], text_size=config["text_size"], screen_res=screen_res)


if __name__ == "__main__":
    main()
