################################################################################

# Q-Chef API Server Data Checking and Editing
# Authors: Kaz

# In order to run this file alone:
# $ python prune_recipe_data_2022.py

# This script removes recipes identified by NGD as being unsuitable fo the longitudinal study

################################################################################
# Imports
################################################################################
import json

################################################################################
# Constants
################################################################################
r_data = {}
# Grab the data from their jsons
with open('../server/src/data/qchef_recipes.json', 'r') as f:
  r_data = json.load(f)

urls_to_delete = [
  "www.bbc.co.uk/food/recipes/hasselback_bacon_61171",
  "www.bbc.co.uk/food/recipes/greenchutney_86561",
  "www.bbc.co.uk/food/recipes/crispy_fish_fingers_34974",
  "www.bbc.co.uk/food/recipes/potato_and_pepper_bake_76628",
  "www.bbc.co.uk/food/recipes/oven_chips_67210",
  "www.bbc.co.uk/food/recipes/celeriac_remoulade_65265",
  "www.bbc.co.uk/food/recipes/roastturkeywithbread_87596",
  "www.bbc.co.uk/food/recipes/prawncocktail_87595",
  "www.bbc.co.uk/food/recipes/bacon_and_egg_canapes_11283",
  "www.bbc.co.uk/food/recipes/tomatochutney_75669",
  "www.bbc.co.uk/food/recipes/spanish_tomato_bread_15677",
  "www.bbc.co.uk/food/recipes/toadinthehole_3354",
  "www.bbc.co.uk/food/recipes/green_tomato_chutney_41573",
  "www.bbc.co.uk/food/recipes/easychickenliverpate_87604",
  "www.bbc.co.uk/food/recipes/dolmades_72399",
  "www.bbc.co.uk/food/recipes/tuscan_fries_61356",
  "www.bbc.co.uk/food/recipes/thebestchipsyouhavee_93121",
  "www.bbc.co.uk/food/recipes/roastchicken_90247",
  "www.bbc.co.uk/food/recipes/christmas_carrots_90489",
  "www.bbc.co.uk/food/recipes/greencurrypaste_67789",
  "www.bbc.co.uk/food/recipes/how_to_make_fish_fingers_64484",
  "www.bbc.co.uk/food/recipes/roastpotatoeswithlem_83939",
  "www.bbc.co.uk/food/recipes/pestomash_67178",
  "www.bbc.co.uk/food/recipes/padthai_67953",
  "www.bbc.co.uk/food/recipes/sundriedtomatoandoli_66043",
  "www.bbc.co.uk/food/recipes/cheeseomelette_80621",
  "www.bbc.co.uk/food/recipes/course_country_terrine_54023",
  "www.bbc.co.uk/food/recipes/steaktartare_88981",
  "www.bbc.co.uk/food/recipes/creamedbrusselssprou_84835",
  "www.bbc.co.uk/food/recipes/ragudipomodoro_70563",
  "www.bbc.co.uk/food/recipes/italianbeanandspinac_84283",
  "www.bbc.co.uk/food/recipes/freshtomatosalsawith_8881",
  "www.bbc.co.uk/food/recipes/gameterrine_14230",
  "www.bbc.co.uk/food/recipes/how_to_make_a_tomato_07153",
  "www.bbc.co.uk/food/recipes/floss_fantastic_fish_31623",
  "www.bbc.co.uk/food/recipes/donals_diy_beans_on_29702",
  "www.bbc.co.uk/food/recipes/tomato_confit_canapes_28293",
  "www.bbc.co.uk/food/recipes/smokedsalmonpate_66102",
  "www.bbc.co.uk/food/recipes/savoury_biscuits_46091",
  "www.bbc.co.uk/food/recipes/mapleroastparsnips_84758",
  "www.bbc.co.uk/food/recipes/roastturkeyandstuffi_71053",
  "www.bbc.co.uk/food/recipes/homemade_fish_fingers_85938",
  "www.bbc.co.uk/food/recipes/hollandaisesauce_1309",
  "www.bbc.co.uk/food/recipes/braisedmince_91963",
  "www.bbc.co.uk/food/recipes/roasted_red_pepper_50795",
  "www.bbc.co.uk/food/recipes/roastpotatoes_92811",
  "www.bbc.co.uk/food/recipes/homemade_beer_mustard_55981",
  "www.bbc.co.uk/food/recipes/scrambledeggswithpas_81593",
  "www.bbc.co.uk/food/recipes/homemade_beans_on_toast_46976",
  "www.bbc.co.uk/food/recipes/griddledhalloumi_79154",
  "www.bbc.co.uk/food/recipes/patatas_bravas_72566",
  "www.bbc.co.uk/food/recipes/potatowedgeswithrose_86029",
  "www.bbc.co.uk/food/recipes/sage_and_parmesan_73369",
  "www.bbc.co.uk/food/recipes/patatabravas_81525",
  "www.bbc.co.uk/food/recipes/pizzadoughbase_70980",
  "www.bbc.co.uk/food/recipes/crispfriedplaice_90189",
  "www.bbc.co.uk/food/recipes/steamedmussels_76585",
  "www.bbc.co.uk/food/recipes/roastbeetroot_72797",
  "www.bbc.co.uk/food/recipes/low-fat_roast_potatoes_35344",
  "www.bbc.co.uk/food/recipes/red_onion_and_brie_80420",
  "www.bbc.co.uk/food/recipes/mashedpotatoes_90230",
  "www.bbc.co.uk/food/recipes/bombaypotatoes_1406",
  "www.bbc.co.uk/food/recipes/fondantpotatoes_93087",
  "www.bbc.co.uk/food/recipes/puff_pastry_pizza_bites_98325",
  "www.bbc.co.uk/food/recipes/how_to_make_pizza_50967",
  "www.bbc.co.uk/food/recipes/tomato_and_chilli_jam_20031",
  "www.bbc.co.uk/food/recipes/chapatis_77146",
  "www.bbc.co.uk/food/recipes/maneesh_55703",
  "www.bbc.co.uk/food/recipes/chilli_con_carne_with_75631",
  "www.bbc.co.uk/food/recipes/cheeseandcherrytomat_84142",
  "www.bbc.co.uk/food/recipes/ham_and_egg_pots_63131",
  "www.bbc.co.uk/food/recipes/lighter_fish_finger_18584",
  "www.bbc.co.uk/food/recipes/roastpotatoes_8818",
  "www.bbc.co.uk/food/recipes/theperfectbakedpotat_67837",
  "www.bbc.co.uk/food/recipes/homemade_beans_on_toast_39014",
  "www.bbc.co.uk/food/recipes/savourypancakebatter_74778",
  "www.bbc.co.uk/food/recipes/gingerglazedcarrots_73411",
  "www.bbc.co.uk/food/recipes/totally_lazy_mini_98499",
  "www.bbc.co.uk/food/recipes/smoked_mackerel_pt_with_36210",
  "www.bbc.co.uk/food/recipes/chicken_liver_pt_55821",
  "www.bbc.co.uk/food/recipes/celeriacremoulade_77607",
  "www.bbc.co.uk/food/recipes/homemade_hotdogs_70075",
  "www.bbc.co.uk/food/recipes/potatoes_in_their_skins_48795",
  "www.bbc.co.uk/food/recipes/healthy_oven_chips_82256",
  "www.bbc.co.uk/food/recipes/blue_cheese_and_fig_34219",
  "www.bbc.co.uk/food/recipes/tabbouleh_91782",
  "www.bbc.co.uk/food/recipes/crispy_potato_peelings_07088",
  "www.bbc.co.uk/food/recipes/pad_thai_38349"
]

################################################################################
# MAIN
################################################################################
if __name__ == "__main__":
  new_r_data = {}

  ids_to_delete = [url.split("_")[-1] for url in urls_to_delete]

  for k,r_id in enumerate(ids_to_delete):
    if len(r_id) < 5:
      # Create the new r_id number
      ids_to_delete[k] = "0" * (5 - len(r_id)) + r_id

  print(len(ids_to_delete))
  print(len(r_data))
  # Go through all of the recipes
  for r_id, r_info in r_data.items():
    if r_id not in ids_to_delete:
      new_r_data[r_id] = r_info
  print(len(new_r_data))
  print(len(new_r_data)-len(r_data))
  # Save the modified data back into their jsons
  with open('../server/src/data/qchef_recipes_pruned.json', 'w') as f:
    f.write(json.dumps(new_r_data))
