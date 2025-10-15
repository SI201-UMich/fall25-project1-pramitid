# Name: Pramiti Dubey
# UMID: 68521225
# Email: pramitid@umich.edu
# Asked genAI for help with the Unittests and did research from there on tempfile benefits and usages 


import csv
import unittest
import os 
import tempfile

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
        f.write(f"Mass / (Bill x Flipper) Ratio for {species_name}:\n")
        f.write(f"{ratio_value}\n")
        f.write(" \n")
        f.write(f"Average Bill Depth (mm) by Island and Sex:\n")
        for island, sex_dict in bill_depth_summary.items():
            male_avg = sex_dict["male"]
            female_avg = sex_dict["female"]
            f.write(f"{island}:\n")
            f.write(f"  Male:   {male_avg:.2f} mm\n")
            f.write(f"  Female: {female_avg:.2f} mm\n\n")


class PenguinsTests(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.created_paths = []

        # Helper to write and track files
        def write_csv(name, header, rows):
            path = os.path.join(self.base_dir, name)
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(header)
                w.writerows(rows)
            self.created_paths.append(path)
            return path

        hdr = ["species","body_mass_g","bill_length_mm","flipper_length_mm","bill_depth_mm","island","sex"]

        self.ok_csv = write_csv("penguins_ok.csv", hdr, [
            ["Adelie","3700","37.0","180","18.0","Dream","Male"],
            ["Adelie","3800","38.0","190","17.0","Dream","Female"],
            ["Gentoo","5000","46.0","217","15.0","Biscoe","Male"],
            ["Gentoo","5100","47.0","220","16.0","Biscoe","Female"],
            ["Adelie","NA","39.0","181","18.5","Dream","Male"],  # skipped by ratio
        ])

        self.strip_csv = write_csv("penguins_strip.csv", hdr, [
            [' "Adelie" ',' "3700" ',' "39.1" ',' "181" ',' "18.7" ',' "Torgersen" ',' "Male" ']
        ])

        self.header_only_csv = write_csv("penguins_header_only.csv", hdr, [])

        bad_hdr = ["species","body_mass_g","bill_length_mm","flipper_length_mm","island","sex"]  # missing bill_depth_mm
        self.missing_header_csv = write_csv("penguins_missing_header.csv", bad_hdr, [
            ["Adelie","3700","39.1","181","Torgersen","Male"]
        ])

    def tearDown(self):
        for p in self.created_paths:
            try:
                os.remove(p)
            except FileNotFoundError:
                pass

    def test_load_penguins_general_multiple_species(self):
        d = load_penguins(os.path.basename(self.ok_csv))
        self.assertIn("Adelie", d)
        self.assertIn("Gentoo", d)
        self.assertEqual(d["Adelie"]["masses"][0], "3700")
        self.assertEqual(d["Gentoo"]["flippers"][0], "217")

    def test_load_penguins_general_stripping(self):
        d = load_penguins(os.path.basename(self.strip_csv))
        self.assertEqual(list(d.keys()), ["Adelie"])
        self.assertEqual(d["Adelie"]["islands"][0], "Torgersen")
        self.assertEqual(d["Adelie"]["sex"][0], "Male")
        self.assertEqual(d["Adelie"]["bills"][0], "39.1")

    def test_load_penguins_edge_header_only(self):
        self.assertEqual(load_penguins(os.path.basename(self.header_only_csv)), {})

    def test_load_penguins_edge_missing_required_header_raises(self):
        with self.assertRaises(ValueError):
            load_penguins(os.path.basename(self.missing_header_csv))

    def test_calc_mass_ratio_general_basic(self):
        d = load_penguins(os.path.basename(self.ok_csv))
        expected = (3700/(37.0*180.0) + 3800/(38.0*190.0)) / 2.0
        self.assertAlmostEqual(calc_mass_ratio(d, "Adelie"), expected, places=8)

    def test_calc_mass_ratio_general_skips_na(self):
        d = {"Adelie": {
            "masses":["NA","4000"], "bills":["40.0","40.0"], "flippers":["200","200"],
            "depths":[], "islands":[], "sex":[]
        }}
        self.assertAlmostEqual(calc_mass_ratio(d, "Adelie"), 4000/(40.0*200.0), places=8)

    def test_calc_mass_ratio_edge_all_invalid_returns_zero(self):
        d = {"Adelie": {
            "masses":["","NA"], "bills":["","NA"], "flippers":["","NA"],
            "depths":[], "islands":[], "sex":[]
        }}
        self.assertEqual(calc_mass_ratio(d, "Adelie"), 0.0)

    def test_calc_mass_ratio_edge_zero_dimensions_skipped(self):
        d = {"Adelie": {
            "masses":["3700","3800"], "bills":["0","38.0"], "flippers":["180","0"],
            "depths":[], "islands":[], "sex":[]
        }}
        self.assertEqual(calc_mass_ratio(d, "Adelie"), 0.0)

    def test_calc_avg_depth_general_simple(self):
        d = load_penguins(os.path.basename(self.ok_csv))
        res = calc_avg_bill_depth_by_island_and_sex(d)
        self.assertAlmostEqual(res["Dream"]["male"], 18.25, places=6)
        self.assertAlmostEqual(res["Dream"]["female"], 17.0, places=6)
        self.assertAlmostEqual(res["Biscoe"]["male"], 15.0, places=6)
        self.assertAlmostEqual(res["Biscoe"]["female"], 16.0, places=6)

    def test_calc_avg_depth_general_merge_species(self):
        d = {
            "Adelie": {"islands":["Dream"], "sex":["Male"], "depths":["18.0"], "masses":[],"bills":[],"flippers":[]},
            "Gentoo": {"islands":["Dream"], "sex":["Male"], "depths":["20.0"], "masses":[],"bills":[],"flippers":[]}
        }
        res = calc_avg_bill_depth_by_island_and_sex(d)
        self.assertIn("Dream", res)
        self.assertAlmostEqual(res["Dream"]["male"], 19.0, places=6)

    def test_calc_avg_depth_edge_missing_values_zero_for_missing_sex(self):
        d = {"Adelie": {
            "islands":["Torgersen","Torgersen","Torgersen"],
            "sex":["Male","Female","Female"],
            "depths":["18.0","NA",""],
            "masses":[],"bills":[],"flippers":[]
        }}
        res = calc_avg_bill_depth_by_island_and_sex(d)
        self.assertAlmostEqual(res["Torgersen"]["male"], 18.0, places=6)
        self.assertEqual(res["Torgersen"]["female"], 0.0)

    def test_calc_avg_depth_edge_empty_input(self):
        self.assertEqual(calc_avg_bill_depth_by_island_and_sex({}), {})

    # --- output_results_txt (4) ---
    def test_output_results_general_writes_headers_and_ratio(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "penguin_results.txt")
            output_results_txt(out, "Adelie", 0.123456, {"Dream":{"male":18.0,"female":17.5}})
            self.assertTrue(os.path.exists(out))
            with open(out) as f:
                s = f.read()
            self.assertIn("Penguin Calculations:", s)
            self.assertIn("Mass / (Bill x Flipper) Ratio for Adelie:", s)
            self.assertIn("0.123456", s)

    def test_output_results_general_multiple_islands_format(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "penguin_results2.txt")
            summary = {"Dream":{"male":18.0,"female":17.5}, "Biscoe":{"male":15.25,"female":16.75}}
            output_results_txt(out, "Gentoo", 0.5, summary)
            with open(out) as f:
                s = f.read()
            self.assertIn("Dream:", s)
            self.assertIn("  Male:   18.00 mm", s)
            self.assertIn("  Female: 17.50 mm", s)
            self.assertIn("Biscoe:", s)
            self.assertIn("  Male:   15.25 mm", s)
            self.assertIn("  Female: 16.75 mm", s)

    def test_output_results_edge_empty_summary(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "penguin_results3.txt")
            output_results_txt(out, "Adelie", 0.0, {})
            with open(out) as f:
                s = f.read()
            self.assertIn("Average Bill Depth (mm) by Island and Sex:", s)
            
            self.assertNotIn("  Male:", s)
            self.assertNotIn("  Female:", s)

    def test_output_results_edge_zero_formats(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "penguin_results4.txt")
            output_results_txt(out, "Adelie", 0.0, {"Torgersen":{"male":0.0,"female":0.0}})
            with open(out) as f:
                s = f.read()
            self.assertIn("Torgersen:", s)
            self.assertIn("  Male:   0.00 mm", s)
            self.assertIn("  Female: 0.00 mm", s)



def main(): 
    data = load_penguins("penguins.csv")

    species = "Adelie"
    adelie_ratio = calc_mass_ratio(data, "Adelie")

    bill_depth_summary = calc_avg_bill_depth_by_island_and_sex(data)

    output_results_txt("penguin_results.txt", species, adelie_ratio, bill_depth_summary)

    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()

