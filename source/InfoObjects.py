#!/usr/bin/env python3

'''
Created on Tue Mar 28 13:27:00 2023
@author: danikam
'''

# List of weight class names used by GREET, from heaviest to lightest
GREET_classes_dict = {
    1: 'Heavy GVW',
    2: 'Medium GVW',
    3: 'Light GVW',
    4: 'Light-duty'}
    
# List of weight class names used by GREET, from heaviest to lightest
VW_classes_dict = {
    1: 'Heavy Unloaded VW',
    2: 'Medium Unloaded VW',
    3: 'Light Unloaded VW',
    4: 'Light-duty'}

# Dictionary to map fuel integer identifiers in VIUS survey to fuel names
fuels_dict = {
    1: 'Gasoline',
    2: 'Diesel',
    3: 'Natural gas',
    4: 'Propane',
    5: 'Alcohol fuels',
    6: 'Electricity',
    7: 'Gasoline and natural gas',
    8: 'Gasoline and propane',
    9: 'Gasoline and alcohol fuels',
    10: 'Gasoline and electricity',
    11: 'Diesel and natural gas',
    12: 'Diesel and propane',
    13: 'Diesel and alcohol fuels',
    14: 'Diesel and electricity',
    15: 'Not reported',
    16: 'Not applicable',
}

# List of commodities in the FAF5 database
faf5_commodities_list = [
    'all',
    'Live animals/fish',
    'Cereal grains',
    'Other ag prods.',
    'Animal feed',
    'Meat/seafood',
    'Milled grain prods.',
    'Other foodstuffs',
    'Alcoholic beverages',
    'Tobacco prods.',
    'Building stone',
    'Natural sands',
    'Gravel',
    'Nonmetallic minerals',
    'Metallic ores',
    'Coal',
    'Crude petroleum',
    'Gasoline',
    'Fuel oils',
    'Natural gas and other fossil products',
    'Basic chemicals',
    'Pharmaceuticals',
    'Fertilizers',
    'Chemical prods.',
    'Plastics/rubber',
    'Logs',
    'Wood prods.',
    'Newsprint/paper',
    'Paper articles',
    'Printed prods.',
    'Textiles/leather',
    'Nonmetal min. prods.',
    'Base metals',
    'Articles-base metal',
    'Machinery',
    'Electronics',
    'Motorized vehicles',
    'Transport equip.',
    'Precision instruments',
    'Furniture',
    'Misc. mfg. prods.',
    'Waste/scrap',
    'Mixed freight',
]

# Dictionary to map string identifiers of percentage of ton-miles spent carrying a given commodity to human-readable commodity names
pretty_commodities_dict = {
    'PALCOHOLIC': 'Alcoholic Beverages',
    'PANIMALFEED': 'Animal Feed',
    'PBAKERYPROD': 'Bakery Products',
    'PBASEMETAL': 'Articles of Base Metal',
    'PCHEMICALS': 'Basic Chemicals',
    'PCOAL': 'Coal',
    'PCRUDEPETRLM': 'Crude Petroleum',
    'PELECTRONIC': 'Electronics',
    'PEMPCONTAIN': 'EShipping Containers',
    'PFERTILIZER': 'Fertilizer',
    'PFUELOIL': 'Fuel oil',
    'PFURNITURE': 'Furniture',
    'PGASOLINE': 'Gasoline',
    'PGRAINS': 'Cereal Grains',
    'PGRAVEL': 'Gravel',
    'PHAZWASTE': 'Hazardous waste',
    'PLIVEANIMAL': 'Live Animal',
    'PLOGS': 'Logs',
    'PMACHINERY': 'Machinery',
    'PMAIL': 'Mail',
    'PMEATS': 'Meats',
    'PMETALPRIM': 'Base Metal in Primary or Semifinished Forms',
    'PMISCPROD': 'Miscellaneous Manufactured Products',
    'PMIXFREIGHT': 'Mixed Freight (For-Hire Carriers Only)',
    'PNEWSPRINT': 'Pulp, Newsprint, Paper, and Paperboard',
    'PNONMETAL': 'Nonmetallic Mineral Products',
    'PORES': 'Metallic Ores and Concentrates',
    'POTHER': 'Products, Equipment, or Materials Not Elsewhere Classified',
    'POTHERAGRIC': 'All Other Agricultural Products',
    'POTHERCHEM': 'All Other Chemical Products and Preparations',
    'POTHERCOAL': 'Natural gas and other fossil products',
    'POTHERFOOD': 'All Other Prepared Foodstuffs',
    'POTHERMIN': 'All Other Nonmetallic Minerals',
    'POTHERTRANS': 'All Other Transportation Equipment',
    'POTHERWASTE': 'All Other Waste and Scrap',
    'PPAPER': 'Paper or Paperboard Articles',
    'PPHARMACEUT': 'Pharmaceutical Products',
    'PPLASTICS': 'Plastics and Rubber',
    'PPRECISION': 'Precision Instruments and Apparatus',
    'PPRINTPROD': 'Printed Products',
    'PRECYCLABLE': 'Recyclable Products',
}

# Dictionary to map FAF5 commodity names to VIUS identifiers (including aggregation in some cases)
FAF5_VIUS_commodity_map = {
    'Live animals/fish': {
        'VIUS': ['PLIVEANIMAL'],
        'FAF5': ['Live animals/fish'],
        'short name': 'live_animals_fish'
    },
    'Cereal grains': {
        'VIUS': ['PGRAINS'],
        'FAF5': ['Cereal grains'],
        'short name': 'cereal_grains'
    },
    'Other agricultural products': {
        'VIUS': ['POTHERAGRIC'],
        'FAF5': ['Other ag prods.', 'Tobacco prods.'],
        'short name': 'other_ag_prods'
    },
    'Animal feed': {
        'VIUS': ['PANIMALFEED'],
        'FAF5': ['Animal feed'],
        'short name': 'animal_feed'
    },
    'Meat/seafood': {
        'VIUS': ['PMEATS'],
        'FAF5': ['Meat/seafood'],
        'short name': 'meat_seafood'
    },
    'Milled grain prods.': {
        'VIUS': ['PBAKERYPROD'],
        'FAF5': ['Milled grain prods.'],
        'short name': 'milled_grain_prods'
    },
    'Other foodstuffs': {
        'VIUS': ['POTHERFOOD'],
        'FAF5': ['Other foodstuffs'],
        'short name': 'other_food'
    },
    'Alcoholic beverages': {
        'VIUS': ['PALCOHOLIC'],
        'FAF5': ['Alcoholic beverages'],
        'short name': 'alcohol'
    },
    'Nonmetallic minerals': {
        'VIUS': ['PNONMETAL'],
        'FAF5': ['Nonmetallic minerals'],
        'short name': 'nonmetal_mins'
    },
    'Metallic ores': {
        'VIUS': ['PORES'],
        'FAF5': ['Metallic ores'],
        'short name': 'metal_ores'
    },
    'Coal': {
        'VIUS': ['PCOAL'],
        'FAF5': ['Coal'],
        'short name': 'coal'
    },
    'Crude petroleum': {
        'VIUS': ['PCRUDEPETRLM'],
        'FAF5': ['Crude petroleum'],
        'short name': 'crude_petroleum'
    },
    'Gasoline': {
        'VIUS': ['PGASOLINE'],
        'FAF5': ['Gasoline'],
        'short name': 'gasoline'
    },
    'Fuel oils': {
        'VIUS': ['PFUELOIL'],
        'FAF5': ['Fuel oils'],
        'short name': 'fuel_oils'
    },
    'Natural gas and other fossil products': {
        'VIUS': ['POTHERCOAL'],
        'FAF5': ['Natural gas and other fossil products'],
        'short name': 'other_fossil_products'
    },
    'Basic chemicals': {
        'VIUS': ['PCHEMICALS'],
        'FAF5': ['Basic chemicals'],
        'short name': 'basic_chems'
    },
    'Pharmaceuticals': {
        'VIUS': ['PPHARMACEUT'],
        'FAF5': ['Pharmaceuticals'],
        'short name': 'pharmaceut'
    },
    'Fertilizers': {
        'VIUS': ['PFERTILIZER'],
        'FAF5': ['Fertilizers'],
        'short name': 'fertilizer'
    },
    'Chemical products': {
        'VIUS': ['POTHERCHEM'],
        'FAF5': ['Chemical prods.'],
        'short name': 'chem_prods'
    },
    'Plastics/rubber': {
        'VIUS': ['PPLASTICS'],
        'FAF5': ['Plastics/rubber'],
        'short name': 'plastics_rubber'
    },
    'Logs': {
        'VIUS': ['PLOGS'],
        'FAF5': ['Logs'],
        'short name': 'logs'
    },
    'Wood products': {
        'VIUS': ['PNEWSPRINT', 'PPAPER', 'PPRINTPROD'],
        'FAF5': ['Newsprint/paper', 'Wood prods.', 'Paper articles', 'Printed prods.'],
        'short name': 'wood_prods'
    },
    'Miscellaneous manufactured products': {
        'VIUS': ['PMISCPROD'],
        'FAF5': ['Textiles/leather', 'Misc. mfg. prods.', 'Motorized vehicles'],
        'short name': 'misc_manuf_prods'
    },
    'Nonmetallic mineral products': {
        'VIUS': ['PNONMETAL'],
        'FAF5': ['Nonmetal min. prods.', 'Building stone', 'Natural sands', 'Gravel'],
        'short name': 'nonmetal_min_prods'
    },
    'Base metal in primary or semifinished forms': {
        'VIUS': ['PMETALPRIM'],
        'FAF5': ['Base metals'],
        'short name': 'base_metals'
    },
    'Articles of Base Metal': {
        'VIUS': ['PBASEMETAL'],
        'FAF5': ['Articles-base metal'],
        'short name': 'base_metal'
    },
    'Machinery': {
        'VIUS': ['PMACHINERY'],
        'FAF5': ['Machinery'],
        'short name': 'machinery'
    },
    'Electronics': {
        'VIUS': ['PELECTRONIC'],
        'FAF5': ['Electronics'],
        'short name': 'electronics'
    },
    'Transportation equipment': {
        'VIUS': ['POTHERTRANS'],
        'FAF5': ['Transport equip.'],
        'short name': 'transport_equip'
    },
    'Precision instruments': {
        'VIUS': ['PPRECISION'],
        'FAF5': ['Precision instruments'],
        'short name': 'precision_inst'
    },
    'Furniture': {
        'VIUS': ['PFURNITURE'],
        'FAF5': ['Furniture'],
        'short name': 'furniture'
    },
    'Waste/scrap': {
        'VIUS': ['POTHERWASTE', 'PHAZWASTE'],
        'FAF5': ['Waste/scrap'],
        'short name': 'waste_scrap'
    },
    'Mixed freight': {
        'VIUS': ['PMIXFREIGHT'],
        'FAF5': ['Mixed freight'],
        'short name': 'mixed_freight'
    },
}

# Dictionary to map trip range windows used in FAF5 data to trip range windows in VIUS survey
FAF5_VIUS_range_map = {
    'Below 100 miles': {
        'VIUS': ['TRIP0_50', 'TRIP051_100'],
        'FAF5': ['Below 100'],
        'short name': 'below_100'
    },
    '100 to 250 miles': {
        'VIUS': ['TRIP101_200'],
        'FAF5': ['100 - 249'],
        'short name': '100_250'
    },
    '250 to 500 miles': {
        'VIUS': ['TRIP201_500'],
        'FAF5': ['250 - 499'],
        'short name': '250_500'
    },
    'Over 500 miles': {
        'VIUS': ['TRIP500MORE'],
        'FAF5': ['500 - 749', '750 - 999', '1,000 - 1,499', '1,500 - 2,000', 'Over 2,000'],
        'short name': 'over_500'
    },
}

# Dictionary to coarsely map trip range windows used in FAF5 data to trip range windows in VIUS survey into two categories
FAF5_VIUS_range_map_coarse = {
    'Below 250 miles': {
        'VIUS': ['TRIP0_50', 'TRIP051_100', 'TRIP101_200'],
        'FAF5': ['Below 100', '100 - 249'],
        'short name': 'below_250'
    },
    'Over 250 miles': {
        'VIUS': ['TRIP201_500', 'TRIP500MORE'],
        'FAF5': ['250 - 499', '500 - 749', '750 - 999', '1,000 - 1,499', '1,500 - 2,000', 'Over 2,000'],
        'short name': 'over_250'
    },
}

# Dictionary to map string identifiers of trip range used in VIUS data to human-readable descriptions
pretty_range_dict = {
    'TRIP0_50': 'Range <= 50 miles',
    'TRIP051_100': '51 miles <= Range <= 100 miles',
    'TRIP101_200': '101 miles <= Range <= 200 miles',
    'TRIP201_500': '201 miles <= Range <= 500 miles',
    'TRIP500MORE': 'Range >= 501 miles'
}

# Dictionary to map integer identifiers of administrative states used in the VIUS data to state names
states_dict = {
    1: 'Alabama',
    2: 'Alaska',
    4: 'Arizona',
    5: 'Arkansas',
    6: 'California',
    8: 'Colorado',
    9: 'Connecticut',
    10: 'Delaware',
    11: 'District of Columbia',
    12: 'Florida',
    13: 'Georgia',
    15: 'Hawaii',
    16: 'Idaho',
    17: 'Illinois',
    18: 'Indiana',
    19: 'Iowa',
    20: 'Kansas',
    21: 'Kentucky',
    22: 'Louisiana',
    23: 'Maine',
    24: 'Maryland',
    25: 'Massachusetts',
    26: 'Michigan',
    27: 'Minnesota',
    28: 'Mississippi',
    29: 'Missouri',
    30: 'Montana',
    31: 'Nebraska',
    32: 'Nevada',
    33: 'New Hampshire',
    34: 'New Jersey',
    35: 'New Mexico',
    36: 'New York',
    37: 'North Carolina',
    38: 'North Dakota',
    39: 'Ohio',
    40: 'Oklahoma',
    41: 'Oregon',
    42: 'Pennsylvania',
    44: 'Rhode Island',
    45: 'South Carolina',
    46: 'South Dakota',
    47: 'Tennessee',
    48: 'Texas',
    49: 'Utah',
    50: 'Vermont',
    51: 'Virginia',
    53: 'Washington',
    54: 'West Virginia',
    55: 'Wisconsin',
    56: 'Wyoming'
}
