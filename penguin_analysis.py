# Name: Pramiti Dubey
# UMID: 68521225
# Email: pramitid@umich.edu

import csv
import unittest
import os 

def load_penguins(f):
    base_path = os.path.abspath(os.path.dirname(__file__))
    full_path = os.path.join(base_path, f)

    with open(full_path) as fh:
        r = csv.reader(fh)
        rows = list(r)
    
    header = [h.strip().strip('"') for h in rows[0]]
    species_idx = header.index("species")
    mass_idx = header.index("body_mass_g")
    bill_idx = header.index("bill_length_mm")
    flipper_idx = header.index("flipper_length_mm")
    depth_idx    = header.index("bill_depth_mm")
    island_idx   = header.index("island")
    sex_idx      = header.index("sex")

    species_dict = {}

    for row in rows[1:]:
        species = row[species_idx].strip().strip('"')
        mass = row[mass_idx].strip().strip('"')
        bill = row[bill_idx].strip().strip('"')
        flipper = row[flipper_idx].strip().strip('"')
        depth   = row[depth_idx].strip().strip('"')
        island  = row[island_idx].strip().strip('"')
        sex     = row[sex_idx].strip().strip('"')

        if species not in species_dict:
            species_dict[species] = {
                "masses": [],
                "bills": [],
                "flippers": [],
                "depths":   [],
                "islands":  [],
                "sex":      []
            }

        species_dict[species]["masses"].append(mass)
        species_dict[species]["bills"].append(bill)
        species_dict[species]["flippers"].append(flipper)
        species_dict[species]["depths"].append(depth)
        species_dict[species]["islands"].append(island)
        species_dict[species]["sex"].append(sex)

    return species_dict


def calc_mass_ratio(d, species_name):

    masses = d[species_name]["masses"]
    bills = d[species_name]["bills"]
    flippers = d[species_name]["flippers"]

    total_ratio = 0.0
    count = 0

    for i in range(len(masses)):
        m = masses[i].strip().strip('"')
        b = bills[i].strip().strip('"')
        f = flippers[i].strip().strip('"')

        if m in ("", "NA") or b in ("", "NA") or f in ("", "NA"):
            continue

        m_val = float(m)
        b_val = float(b)
        f_val = float(f)

        if b_val == 0 or f_val == 0:
            continue

        total_ratio += m_val / (b_val * f_val)
        count += 1

    return total_ratio / count if count else 0.0


def calc_avg_bill_depth_by_island_and_sex(d):
    totals = {}
    result = {}

    for species in d:
        islands = d[species]["islands"]
        sexes   = d[species]["sex"]
        depths  = d[species]["depths"]

        for i in range(len(islands)):
            isl = islands[i]
            sx  = sexes[i]
            dep = depths[i]

            if isl == "" or sx == "" or dep == "" or dep == "NA":
                continue 
            
            dep_val = float(dep)

            if isl not in totals:
                totals[isl] = {
                    "male":   {"sum": 0.0, "n": 0},
                    "female": {"sum": 0.0, "n": 0}
                }
                        
            key = sx.lower()
            if key in ("male", "female"):
                totals[isl][key]["sum"] += dep_val
                totals[isl][key]["n"]   += 1
            

    for isl, by_sex in totals.items():
        result[isl] = {
            "male":   (by_sex["male"]["sum"]   / by_sex["male"]["n"])   if by_sex["male"]["n"]   else 0.0,
            "female": (by_sex["female"]["sum"] / by_sex["female"]["n"]) if by_sex["female"]["n"] else 0.0
        }
    return result

    

def output_results_txt(out_path, species_name, ratio_value, bill_depth_summary):
    with open(out_path, "w") as f:
        f.write("Penguin Calculations:\n")
        f.write(" \n")
        f.write(f"Mass ÷ (Bill x Flipper) Ratio for {species_name}:\n")
        f.write(f"{ratio_value}\n")
        f.write(f"Average Bill Depth (mm) by Island and Sex:\n")
        for island, sex_dict in bill_depth_summary.items():
            male_avg = sex_dict["male"]
            female_avg = sex_dict["female"]
            f.write(f"{island}:\n")
            f.write(f"  Male:   {male_avg:.2f} mm\n")
            f.write(f"  Female: {female_avg:.2f} mm\n\n")



def main(): 
    data = load_penguins("penguins.csv")

    species = "Adelie"
    adelie_ratio = calc_mass_ratio(data, "Adelie")

    bill_depth_summary = calc_avg_bill_depth_by_island_and_sex(data)

    output_results_txt("penguin_results.txt", species, adelie_ratio, bill_depth_summary)


if __name__ == "__main__":
    main()

