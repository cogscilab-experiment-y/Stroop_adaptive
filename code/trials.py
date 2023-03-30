import random


class TrialsTypes:
    congruent = 'congruent'
    incongruent = 'incongruent'
    neutral = 'neutral'


def create_trial(trial_type, word_bank):
    if trial_type == TrialsTypes.congruent:
        word = random.choice(word_bank)
        word["trial_type"] = TrialsTypes.congruent
        return word
    elif trial_type == TrialsTypes.incongruent:
        words = random.sample(word_bank, 2)
        return {'word': words[1]['word'], 'color': words[0]['color'], 'key': words[0]['key'], 'trial_type': TrialsTypes.incongruent}
    elif trial_type == TrialsTypes.neutral:
        word = random.choice(word_bank)
        return {'word': "HHHHHH", 'color': word['color'], 'key': word['key'], 'trial_type': TrialsTypes.neutral}


def create_block(block_info, word_bank):
    trial_types_list = [TrialsTypes.congruent] * block_info["n_congruent"] + \
                       [TrialsTypes.incongruent] * block_info["n_incongruent"] + \
                       [TrialsTypes.neutral] * block_info["n_neutral"]

    random.shuffle(trial_types_list)
    trial_list = [create_trial(trial_type=trial_type, word_bank=word_bank) for trial_type in trial_types_list]
    return {"trial_list": trial_list,
            "step_down_acc": block_info["step_down_acc"],
            "step_down_time": block_info["step_down_time"],
            "step_up_acc": block_info["step_up_acc"],
            "step_up_time": block_info["step_up_time"]}


def create_experiment_part(info, word_bank):
    return [create_block(block_info=block_info, word_bank=word_bank) for block_info in info]
