import random
import csv

distr_filename: str = "slot_distribution.txt"
spell_csv: str = 'spells.csv'
spell_durations_csv: str = 'spell_durations.csv'


def compress_time(time: str) -> str:
    time = time.replace("REACTION", "REACT")
    time = time.replace("ACTION", "A")
    time = time.replace("BONUS ", "B")
    time = time.replace("HOUR", "HR")
    time = time.replace("MINUTE", "MIN")
    time = time.replace("1 ", "")
    time = time.replace("CONCENTRATION, UP TO ", "")
    time = time.replace("CONCENTRATION UP TO ", "")
    time = time.replace("UP TO ", "")
    time = time.replace("INSTANTANEOUS", "INST")
    time = time.replace("UNTIL DISPELLED", "DISP")
    time = time.replace("TRIGGERED", "TRIG")
    time = time.replace(" OR", ",")
    return time


def compress_range(dist: str) -> str:
    dist = dist.split('(')[0].strip()
    dist = dist.replace("-FT", "")
    dist = dist.replace("FT", "")
    dist = dist.replace("MILE", "MI")
    dist = dist.replace("MILES", "MI")
    dist = dist.replace("(10-RADIUS SPHERE)", "")
    return dist


def compress_name(name: str) -> str:
    name = name.replace("FAITHFUL", "")
    name = name.replace("MAGNIFICENT", "")
    name = name.replace("PRIVATE", "")
    return name


def read_durations():
    spell_durations = {}

    def process_line(line: [str]):
        nonlocal spell_durations

        name = line[0].upper().strip()
        name = compress_name(name)
        duration = line[1].upper()
        duration = compress_time(duration)
        spell_durations[name] = duration

    with open(spell_durations_csv) as file:
        csvreader = csv.reader(file)
        next(csvreader)
        for line in csvreader:
            process_line(line)

    return spell_durations


def read_spells_csv(spell_durations):
    spells = {}

    def process_line(line: [str]):
        nonlocal spells

        level = int(line[0])
        name = line[1].upper().strip()
        name = compress_name(name)

        ritual = "R " if len(line[2].strip()) > 0 else "  "
        concentration = "C " if len(line[3].strip()) > 0 else "  "
        vsm = line[5].upper()
        verbal = "V " if "V" in vsm else "  "
        somatic = "S " if "S" in vsm else "  "
        material = "M " if "M" in vsm else "  "

        crvsm = f"{concentration}{ritual}{verbal}{somatic}{material}"

        ran = line[4].upper()
        ran = compress_range(ran)

        cast_time = line[7].upper()
        cast_time = compress_time(cast_time)
        duration = spell_durations[name]

        school = line[6].upper()[:4]
        desc = line[8]

        entry = f"{name:<29} | {crvsm:<7} | {cast_time:<8} | {duration:<10} | {ran:<9} | {school:<4} | {desc:>}"
        if level not in spells:
            spells[level] = []
        spells[level].append(entry)

    with open(spell_csv) as file:
        csvreader = csv.reader(file)
        next(csvreader)
        for line in csvreader:
            process_line(line)

    return spells


def read_distribution():
    distr = {}
    with open(distr_filename) as file:
        for line in file:
            line = line.strip().split()
            if not line:
                continue

            level = int(line[0].strip())
            num = int(line[-1].strip())
            distr[level] = num

    return distr


def generate_spells(available, needed):
    spell_txt = ""
    title = f"{'NAME':^29} | {'  ATTRS  ':^7} | {'TIME':^8} | {'DURATION':^10} | {'RANGE':^9} | {'SCHOOL':^4} | {'DESCRIPTION':>}"
    spell_txt += f"{title}\n{'-'*200}\n"

    for level, num in needed.items():
        spell_txt += f"{f'LEVEL {level}:':<29} | {' ' * 10} | {' ' * 8} | {' ' * 10} | {' ' * 9} | {' ' * 4} |\n"
        available_in_level = available[level]
        current_chosen = set()
        count = 0

        while count < num:
            idx = random.randint(0, len(available_in_level) - 1)
            new_spell: str = available_in_level[idx]
            if new_spell in current_chosen:
                continue

            current_chosen.add(new_spell)
            count += 1
            spell_txt += f"{new_spell}\n"

        spell_txt += f"{' ' * 29} | {' ' * 10} | {' ' * 8} | {' ' * 10} | {' ' * 9} | {' ' * 4} |\n"

    return spell_txt


def main():
    spell_durations = read_durations()
    spells_available = read_spells_csv(spell_durations)
    spells_needed = read_distribution()

    seed: str = input("Enter Dice seed:\n")
    random.seed(seed)
    spells = generate_spells(spells_available, spells_needed)
    print(spells)

    with open("saved_spells.txt", "w") as file:
        file.write(f"Seed: {seed}\n")
        file.write(spells)


if __name__ == "__main__":
    main()
